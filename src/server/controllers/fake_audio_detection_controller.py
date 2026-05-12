
from __future__ import annotations

import os
import struct
import tempfile
import threading
import wave
from functools import wraps
from typing import Any
import matplotlib
matplotlib.use('Agg')
import torch


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_cached_predict(original_fn, loader_fn, *loader_args, **loader_kwargs):
    """
    يحوّل دالة predict(y, sr, ...) إلى نسخة تحمّل الـ model مرة واحدة بس.

    الـ strategy:
      - أول call → loader_fn() يبني الـ model ويحطه في _cached_model
      - التاني call فصاعدًا → يستخدم نفس الـ model من الـ cache
      - thread-safe بـ Lock

    Args:
        original_fn : الدالة الأصلية في الـ run.py (predict)
        loader_fn   : callable يرجع الـ model جاهز (eval + to(device))
        *loader_args / **loader_kwargs : arguments للـ loader_fn
    """
    lock = threading.Lock()
    cache: dict[str, Any] = {}          # {"model": <loaded model>}

    @wraps(original_fn)
    def cached(*args, **kwargs):
        if "model" not in cache:
            with lock:
                if "model" not in cache:   # double-checked locking
                    cache["model"] = loader_fn(*loader_args, **loader_kwargs)
        # نمرّر الـ cached model للـ original عن طريق kwarg خاص
        return original_fn(*args, _cached_model=cache["model"], **kwargs)

    return cached


# ─────────────────────────────────────────────────────────────────────────────
# Per-model patchers
# ─────────────────────────────────────────────────────────────────────────────

def _patch_spectra0():
    """يعمل cache للـ Spectra0Model بدل ما يعيد from_pretrained() كل مرة."""
    import Jabberjay.Models.Spectra0.run as mod
    from Jabberjay.Models.Spectra0.model import Spectra0Model

    if getattr(mod, "_jj_patched", False):
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model():
        return Spectra0Model.from_pretrained(mod._MODEL_ID).eval().to(device)

    _orig = mod.predict

    @wraps(_orig)
    def _patched(y, sr, _cached_model=None):
        if _patched._model is None:
            with _patched._lock:
                if _patched._model is None:
                    print("  [Cache] Loading Spectra0 model…")
                    _patched._model = _load_model()
        model = _patched._model
        audio = mod._preprocess(y, sr).to(device)
        import torch
        with torch.inference_mode():
            probs = torch.softmax(model(audio), dim=1)[0]
        return [
            {"label": "Spoof",     "score": float(probs[0])},
            {"label": "Bonafide",  "score": float(probs[1])},
        ]

    _patched._model = None
    _patched._lock  = threading.Lock()

    mod.predict      = _patched
    mod._jj_patched  = True
    print("  [Patch] Spectra0.predict ✅")


def _patch_rawnet2():
    """يعمل cache للـ RawNet2 model + weights بدل ما يعيد load_state_dict كل مرة."""
    import Jabberjay.Models.RawNet2.run as mod
    from Jabberjay.Models.RawNet2.model import RawNet
    from Jabberjay.Utilities.hugging_face import download_pretrained_model
    import yaml, torch
    from torch import Tensor

    if getattr(mod, "_jj_patched", False):
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"

    @wraps(mod.predict)
    def _patched(y, _cached_model=None):
        if _patched._model is None:
            with _patched._lock:
                if _patched._model is None:
                    print("  [Cache] Loading RawNet2 model…")
                    with open(mod._CONFIG_PATH) as f:
                        cfg = yaml.safe_load(f)
                    m = RawNet(cfg["model"], device)
                    m.to(device)
                    weights = download_pretrained_model(
                        repo_id="MattyB95/pre_trained_DF_RawNet2",
                        filename="pre_trained_DF_RawNet2.pth",
                    )
                    m.load_state_dict(
                        torch.load(weights, map_location=device, weights_only=True)
                    )
                    m.eval()
                    _patched._model = m

        model = _patched._model
        audio_tensor = Tensor(y).unsqueeze(0).to(device)
        with torch.no_grad():
            out   = model(audio_tensor)
            probs = out.exp()
            _, predicted = out.max(dim=1)
        confidence = float(probs[0][predicted.item()])
        return predicted, confidence

    _patched._model = None
    _patched._lock  = threading.Lock()

    mod.predict     = _patched
    mod._jj_patched = True
    print("  [Patch] RawNet2.predict ✅")


def _patch_vit(dataset_name: str, visualisation_name: str):
    # MelSpectrogram في الـ enum بيتحول لـ Mel_Spectrogram في الـ HuggingFace repo name
    _VIS_HF_NAME = {
        "MelSpectrogram": "Mel_Spectrogram",
        "ConstantQ":      "ConstantQ",
        "MFCC":           "MFCC",
    }
    hf_vis = _VIS_HF_NAME.get(visualisation_name, visualisation_name)

    import importlib
    mod_path = f"Jabberjay.Models.Transformer.VIT.{visualisation_name}.run"
    mod = importlib.import_module(mod_path)

    if getattr(mod, "_jj_patched", False):
        return

    from transformers import pipeline as hf_pipeline
    from Jabberjay.Models.Transformer.VIT.utility import get_image
    from Jabberjay.Utilities.enum_handler import Dataset
    from Jabberjay.Utilities.label_normalizer import normalize_pipeline_scores
    import librosa, numpy as np

    _pipeline_cache: dict[str, Any] = {}
    _lock = threading.Lock()

    @wraps(mod.predict)
    def _patched(audio, dataset, _cached_model=None):
        key = dataset.value if isinstance(dataset, Dataset) else str(dataset)
        if key not in _pipeline_cache:
            with _lock:
                if key not in _pipeline_cache:
                    model_id = f"MattyB95/VIT-{key}-{hf_vis}-Synthetic-Voice-Detection"
                    print(f"  [Cache] Loading VIT pipeline: {model_id}…")
                    _pipeline_cache[key] = hf_pipeline(
                        task="image-classification", model=model_id
                    )

        pipe = _pipeline_cache[key]
        y, sr = audio
        S     = librosa.feature.melspectrogram(y=y, sr=sr)
        S_db  = librosa.power_to_db(S=S, ref=np.max)
        image = get_image(data=S_db, sr=sr)
        raw   = pipe(image)
        return normalize_pipeline_scores(raw)

    mod.predict     = _patched
    mod._jj_patched = True
    print(f"  [Patch] VIT/{visualisation_name}.predict ✅")

# ─────────────────────────────────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────────────────────────────────

class FakeAudioDetectionController:
    """
    Singleton controller for fake audio detection.

    Usage
    -----
    ctrl = FakeAudioDetectionController()
    ctrl.setup()                     # يحمّل كل الـ models مرة واحدة
    result = ctrl.detect("x.wav")   # inference فوري بدون أي re-loading
    """

    _instance  = None
    _is_ready  = False
    _init_lock = threading.Lock()

    # ── singleton ────────────────────────────────────────────────────────────
    def __new__(cls):
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._is_ready:
            return
        from Jabberjay import Jabberjay
        from server.helpers import get_config
        from .liveness_model_controller import VoiceDeepfakeDetector

        self.config            = get_config()
        self.__jj              = Jabberjay()
        self.__model_liveness  = VoiceDeepfakeDetector(self.config.LAYER_FOUR__MODELPATH)

    # ── internal helpers ─────────────────────────────────────────────────────
    @staticmethod
    def __create_dummy_wav() -> str:
        """4 ثواني صمت عند 16 kHz — كافية لـ warm-up كل model."""
        tmp       = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        n_samples = 16_000 * 4
        with wave.open(tmp.name, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16_000)
            f.writeframes(struct.pack("<" + "h" * n_samples, *([0] * n_samples)))
        return tmp.name

    def __apply_patches(self):
        """
        Monkey-patch الـ Jabberjay run.py modules بـ cached versions.
        بيتعمل مرة واحدة بس، والـ first detect() call بعد كده هي اللي
        تحمّل الـ weights فعليًا في الـ cache.
        """
        print("[Controller] Applying model-cache patches…")

        # Layer 1 — Spectra0
        if self.config.LAYER_ONE_NAME == "Spectra0":
            _patch_spectra0()

        # Layer 2 — VIT  (يحتاج dataset + visualisation)
        if self.config.LAYER_TWO_NAME == "VIT":
            _patch_vit(
                dataset_name      = self.config.VIT_DATASET_NAME,       # "ASVspoof5"
                visualisation_name= self.config.VIT_VISIUALIZATION,     # "MelSpectrogram"
            )

        # Layer 3 — RawNet2
        if self.config.LAYER_THREE_NAME == "RawNet2":
            _patch_rawnet2()

    # ── public API ───────────────────────────────────────────────────────────
    def setup(self) -> bool:
        """
        Warm-up: يطبّق الـ patches ثم يشغّل inference وهمي لكل model
        عشان الـ weights تتحمّل في الـ cache قبل ما أي request حقيقي يوصل.
        كل الـ calls التانية بعد كده بتكون no-ops.
        """
        if self._is_ready:
            print("Models already loaded ✅")
            return True

        # 1) طبّق الـ patches أولًا
        self.__apply_patches()

        # 2) warm-up بـ inference وهمي
        dummy_path = self.__create_dummy_wav()
        try:
            dummy_audio = self.__jj.load(dummy_path)

            print("[Controller] Warming up models…")
            r1 = self.__jj.detect(dummy_audio, model=self.config.LAYER_ONE_NAME)
            r2 = self.__jj.detect(
                dummy_audio,
                model         = self.config.LAYER_TWO_NAME,
                dataset       = self.config.VIT_DATASET_NAME,
                visualisation = self.config.VIT_VISIUALIZATION,
            )
            r3 = self.__jj.detect(dummy_audio, model=self.config.LAYER_THREE_NAME)
            r4 = self.__model_liveness.detect(dummy_path)

            if all([r1, r2, r3, r4]):
                FakeAudioDetectionController._is_ready = True
                print("Fake Audio Detection Models Loaded Successfully ✅")
                return True

        finally:
            os.remove(dummy_path)

        print("Failed to load Fake Audio Detection Models ❌")
        return False

    def detect(self, audio_path: str) -> dict:
        """
        يشغّل الـ 4 detection layers على الـ WAV المعطى.
        الـ models محمّلة في الـ cache → inference فوري.

        Raises:
            RuntimeError: لو setup() لم يُستدعَ أولًا.
        """
        if not self._is_ready:
            raise RuntimeError("Models not loaded — call setup() first.")

        audio = self.__jj.load(audio_path)

        r1 = self.__jj.detect(audio, model=self.config.LAYER_ONE_NAME)
        r2 = self.__jj.detect(
            audio,
            model         = self.config.LAYER_TWO_NAME,
            dataset       = self.config.VIT_DATASET_NAME,
            visualisation = self.config.VIT_VISIUALIZATION,
        )
        r3 = self.__jj.detect(audio, model=self.config.LAYER_THREE_NAME)
        r4 = self.__model_liveness.detect(audio_path)

        # print(f"Detection results for {audio_path}:")
        # print(f"  Layer 1 ({self.config.LAYER_ONE_NAME}):  {r1}")
        # print(f"  Layer 2 ({self.config.LAYER_TWO_NAME}):  {r2}")
        # print(f"  Layer 3 ({self.config.LAYER_THREE_NAME}): {r3}")
        # print(f"  Layer 4 (Liveness): {r4}")

        return {f"{self.config.LAYER_ONE_NAME}": r1, f"{self.config.LAYER_TWO_NAME}": r2, f"{self.config.LAYER_THREE_NAME}": r3, f"{self.config.LAYER_FOUR_NAME}": r4}
    
    def predict(self, audio_path: str,return_layer_results:bool=False) -> dict:
        fake_score=0
        real_score=0
        
        results=self.detect(audio_path)
        r1=results[f"{self.config.LAYER_ONE_NAME}"]
        r2=results[f"{self.config.LAYER_TWO_NAME}"]
        r3=results[f"{self.config.LAYER_THREE_NAME}"]
        r4=results[f"{self.config.LAYER_FOUR_NAME}"]
        
        r1_label=1 if r1.label == "Spoof" else 0
        r2_label=1 if r2.label == "Spoof" else 0
        r3_label=1 if r3.label == "Spoof" else 0
        r4_label=1 if r4["prediction"] == "AI" else 0


        w1=self.config.LAYER_ONE_WEIGHT
        w2=self.config.LAYER_TWO_WEIGHT
        w3=self.config.LAYER_THREE_WEIGHT
        w4=self.config.LAYER_FOUR_WEIGHT
        
        if r1_label == 1:
            fake_score+=w1
        else:
            real_score+=w1
            
        if r2_label == 1:
            fake_score+=w2
        else:
            real_score+=w2
        
        if r3_label == 1:
            fake_score+=w3
        else:
            real_score+=w3
        
        if r4_label == 1:
            fake_score+=w4
        else:
            real_score+=w4
        total_score=w1+w2+w3+w4
        
        fake_percentage=(fake_score/total_score)*100
        real_percentage=(real_score/total_score)*100
        if return_layer_results:
            layers=[
                {"layer": self.config.LAYER_ONE_NAME, "label": r1_label, "weight": w1},
                {"layer": self.config.LAYER_TWO_NAME, "label": r2_label, "weight": w2},
                {"layer": self.config.LAYER_THREE_NAME, "label": r3_label, "weight": w3},
                {"layer": self.config.LAYER_FOUR_NAME, "label": r4_label, "weight": w4},
            ]
            if fake_percentage > real_percentage:
                return {"prediction": "Fake", "confidence": "100 %", "layers": layers}
            else:
                return {"prediction": "Real", "confidence": "100 %", "layers": layers}

        
        if fake_percentage > real_percentage:
            return {"prediction": "Fake", "confidence": "100 %"}
        else:
            return {"prediction": "Real", "confidence": "100 %"}
        
        