---
library_name: pytorch
tags:
- audio
- spoofing-detection
- anti-spoofing
- wav2vec2
- ecapa-tdnn
license: apache-2.0
pipeline_tag: audio-classification
model-index:
- name: spectra_0
  results:
  - task:
      type: Speech Antispoofing
    dataset:
      name: ASVspoof19_LA
      type: ASVspoof19_LA
    metrics:
    - name: Equal Error Rate
      type: Equal Error Rate
      value: 0.181
  - task:
      type: Speech Antispoofing
    dataset:
      name: ASVspoof21_LA
      type: ASVspoof21_LA
    metrics:
    - name: Equal Error Rate
      type: Equal Error Rate
      value: 6.475
  - task:
      type: Speech Antispoofing
    dataset:
      name: ASVspoof21_DF
      type: ASVspoof21_DF
    metrics:
    - name: Equal Error Rate
      type: Equal Error Rate
      value: 5.41
  - task:
      type: Speech Antispoofing
    dataset:
      name: ASVspoof5
      type: ASVspoof5
    metrics:
    - name: Equal Error Rate
      type: Equal Error Rate
      value: 14.426
  - task:
      type: Speech Antispoofing
    dataset:
      name: ADD2022
      type: ADD2022
    metrics:
    - name: Equal Error Rate
      type: Equal Error Rate
      value: 14.716
  - task:
      type: Speech Antispoofing
    dataset:
      name: In-the-Wild
      type: In-the-Wild
    metrics:
    - name: Equal Error Rate
      type: Equal Error Rate
      value: 1.026
---

## Model Card: Spectra-0 (anti-spoofing / bonafide vs spoof)

`Spectra-0` is a model for **speech spoofing detection** (binary classification: `bonafide` vs `spoof`) from **raw audio waveforms**. Architecture: SSL encoder (`Wav2Vec2`) → MLP projection → `ECAPA-TDNN` 2-class classifier.

- **Input**: waveform \(float32\), shape `(batch, num_samples)` (typically 16 kHz).
- **Output**: logits of shape `(batch, 2)`, where **index 0 = spoof**, **index 1 = bonafide**.

On first run, the model will automatically download the SSL encoder `facebook/wav2vec2-xls-r-300m` via `transformers`.

## Evaluation Results

| Model     | ASVspoof19 LA | ASVspoof21 LA | ASVspoof21 DF | ASVspoof5 | ADD2022  | In-the-Wild |
|-----------|--------|--------|--------|--------|--------|--------|
| [Res2TCNGuard](https://github.com/mtuciru/Res2TCNGuard)      | 7.487  | 19.130 | 19.883 | 37.620 | 49.538 | 49.246 |
| [AASIST3](https://huggingface.co/MTUCI/AASIST3)    | 27.585 | 37.407 | 33.099 | 41.001 | 47.192 | 39.626 | 
| [XSLS](https://github.com/QiShanZhang/SLSforASVspoof-2021-DF)      | 0.231  | 7.714  | 4.220  | 17.688 | 33.951 | 7.453 | 
| [TCM-ADD](https://github.com/ductuantruong/tcm_add)       | **0.152** | 6.655  | **3.444** | 19.505 | 35.252 | 7.767 |
| [DF Arena 1B](https://huggingface.co/Speech-Arena-2025/DF_Arena_1B_V_1)    | 43.793 | 40.137 | 42.994 | 35.333 | 42.139 | 17.598 |
| **Spectra-0** | 0.181  | **6.475** | 5.410  | **14.426** | **14.716** | **1.026** |

## Quickstart

### Clone from Hugging Face

This repository is hosted on Hugging Face Hub: `https://huggingface.co/MTUCI/spectra_0`.

```bash
git lfs install
git clone https://huggingface.co/MTUCI/spectra_0
cd spectra_0
```

### Install dependencies

```bash
pip install -U torch torchaudio transformers huggingface_hub safetensors soundfile
```

### Single-file inference (example preprocessing)

```python
import random
import torch
import torchaudio
import soundfile as sf

from model import spectra_0


def pad_random(x: torch.Tensor, max_len: int = 64600) -> torch.Tensor:
    # x: (num_samples,) or (1, num_samples)
    if x.ndim > 1:
        x = x.squeeze()
    x_len = x.shape[0]
    if x_len >= max_len:
        start = random.randint(0, x_len - max_len)
        return x[start:start + max_len]
    num_repeats = int(max_len / x_len) + 1
    return x.repeat(num_repeats)[:max_len]


def load_audio_mono(path: str) -> torch.Tensor:
    audio, sr = sf.read(path, dtype="float32")
    audio = torch.from_numpy(audio)
    if audio.ndim > 1:
        # (num_samples, channels) -> mono
        audio = audio.mean(dim=1)
    if sr != 16000:
        audio = torchaudio.functional.resample(audio, sr, 16000)
    return audio


device = "cuda" if torch.cuda.is_available() else "cpu"
model = spectra_0.from_pretrained(pretrained_model_name_or_path=".").eval().to(device)

audio = load_audio_mono("path/to/audio.wav")
audio = torchaudio.functional.preemphasis(audio.unsqueeze(0))  # (1, T)
audio = pad_random(audio.squeeze(0), 64600).unsqueeze(0)       # (1, 64600)

with torch.inference_mode():
    logits = model(audio.to(device))  # (1, 2)
    score_spoof = logits[0, 0].item()
    score_bonafide = logits[0, 1].item()

print({"score_bonafide": score_bonafide, "score_spoof": score_spoof})
```

## Threshold-based classification (and how to tune it)

In `model.py`, the `Spectra0Model` class provides `classify()` with a **default threshold** chosen as an “optimal” value for the original setting:

- **Default threshold**: `-1.0625009` (it thresholds `logit_bonafide = logits[:, 1]`)
- **Note**: this threshold **may not be optimal** on a different dataset/domain. It’s recommended to tune the threshold on your dataset using **EER** (Equal Error Rate) or a target FAR/FRR.

Example:

```python
with torch.inference_mode():
    pred = model.classify(audio.to(device), threshold=-1.0625009)  # 1=bonafide, 0=spoof
```

### Tuning the threshold via EER (typical workflow)

1) Run the model on a labeled set and collect scores for both classes.

2) Compute EER and the threshold

## Limitations and notes

- This is a **pre-release** model.
- Significantly stronger models are planned for **Q3–Q4 2026** — stay tuned.

## License

MIT (see the `license` field in the model repo header).

## Contacts

TG channel: https://t.me/korallll_ai
email: k.n.borodin@mtuci.ru
website: https://lab260.ru/