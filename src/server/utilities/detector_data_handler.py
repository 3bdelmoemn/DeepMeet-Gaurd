import os
import time
import json
import wave
import struct
import logging
import threading
import numpy as np
import soundcard as sc
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor, as_completed
from server.helpers import get_config

settings = get_config()
logger = logging.getLogger(__name__)

SILENCE_THRESHOLD = 0.01   # RMS أقل من كده = صمت
SILENCE_DURATION  = 1.5    # ثواني صمت متتالية = الصوت وقف


# ============================================================
# Internal Helpers
# ============================================================

def _normalize_meeting_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def _get_meeting_dir(meeting_name: str) -> str:
    return os.path.join(
        settings.DETECTOR_STORAGE_PATH,
        _normalize_meeting_name(meeting_name)
    )


def _get_period_dir(meeting_dir: str, period_num: int) -> str:
    return os.path.join(meeting_dir, f"period_{period_num}")


def _get_results_dir(meeting_dir: str) -> str:
    return os.path.join(meeting_dir, "meeting_results")


def _is_silent(chunk: np.ndarray) -> bool:
    rms = np.sqrt(np.mean(chunk ** 2))
    return rms < SILENCE_THRESHOLD


# ============================================================
# Public Utilities
# ============================================================

def create_meeting_session(meeting_name: str) -> str:
    """Creates meeting folder and returns meeting_dir."""
    meeting_dir = _get_meeting_dir(meeting_name)
    os.makedirs(_get_results_dir(meeting_dir), exist_ok=True)
    logger.info(f"✅ Meeting session created: {meeting_dir}")
    return meeting_dir


def capture_speaker_audio(
    meeting_dir: str,
    period_num: int,
    sample_rate: int = 16000,
    max_duration: int = None,
) -> list[str]:
    """
    Captures audio from speaker (WASAPI Loopback).
    Splits into separate samples — each sample ends when silence is detected
    or max_duration is reached.
    Returns list of saved WAV file paths.
    """
    max_duration = max_duration or settings.DETECTOR_MAX_DURATION
    period_dir   = _get_period_dir(meeting_dir, period_num)
    os.makedirs(period_dir, exist_ok=True)

    saved_files  = []
    chunk_size   = int(sample_rate * 0.1)        # 100ms chunks
    silence_chunks_needed = int(SILENCE_DURATION / 0.1)

    try:
        default_speaker = sc.default_speaker()
        loopback_mic    = next(
            (m for m in sc.all_microphones(include_loopback=True)
             if m.isloopback and m.name == default_speaker.name),
            sc.default_microphone()
        )
    except Exception as e:
        logger.error(f"❌ Failed to get loopback device: {e}")
        raise

    logger.info(f"🎙️ Capturing period {period_num} from: {loopback_mic.name}")

    with loopback_mic.recorder(samplerate=sample_rate, channels=1) as mic:
        elapsed         = 0.0
        current_sample  = []
        silence_counter = 0
        sample_index    = 0

        def _save_sample(frames: list) -> str | None:
            if not frames:
                return None
            audio     = np.concatenate(frames)
            filename  = os.path.join(period_dir, f"sample_{sample_index}.wav")
            sf.write(filename, audio, sample_rate)
            logger.info(f"💾 Saved sample: {filename}")
            return filename

        while elapsed < max_duration:
            chunk    = mic.record(numframes=chunk_size)
            mono     = chunk[:, 0] if chunk.ndim > 1 else chunk
            elapsed += chunk_size / sample_rate

            if _is_silent(mono):
                silence_counter += 1
                # صوت وقف → احفظ الـ sample الحالي
                if silence_counter >= silence_chunks_needed and current_sample:
                    path = _save_sample(current_sample)
                    if path:
                        saved_files.append(path)
                    current_sample  = []
                    silence_counter = 0
                    sample_index   += 1
            else:
                silence_counter = 0
                current_sample.append(mono)

        # احفظ أي صوت متبقي في نهاية الـ period
        if current_sample:
            path = _save_sample(current_sample)
            if path:
                saved_files.append(path)

    logger.info(f"✅ Period {period_num} captured: {len(saved_files)} samples")
    return saved_files


def run_period_detection(
    detector,
    period_dir: str,
    period_num: int,
) -> list[dict]:
    """
    Runs detector on all samples in the period folder in parallel.
    Returns list of results.
    """
    wav_files = [
        os.path.join(period_dir, f)
        for f in os.listdir(period_dir)
        if f.endswith(".wav")
    ]

    if not wav_files:
        logger.warning(f"⚠️ No samples found in period {period_num}")
        return []

    results = []

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(detector.predict, path, return_layer_results=True): path
            for path in wav_files
        }
        for future in as_completed(futures):
            path = futures[future]
            try:
                result = future.result()
                results.append({
                    "sample": os.path.basename(path),
                    "result": result,
                })
                logger.info(f"🔍 Detected [{os.path.basename(path)}]: {result['prediction']}")
            except Exception as e:
                logger.error(f"❌ Detection failed for {path}: {e}")
                results.append({
                    "sample": os.path.basename(path),
                    "error": str(e),
                })

    return results


def save_period_results(
    meeting_dir: str,
    period_num: int,
    results: list[dict],
) -> str:
    """Saves detection results for a period as JSON."""
    results_dir = _get_results_dir(meeting_dir)
    os.makedirs(results_dir, exist_ok=True)

    output = {
        "period":     period_num,
        "timestamp":  time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total":      len(results),
        "fake_count": sum(1 for r in results if r.get("result", {}).get("prediction") == "Fake"),
        "real_count": sum(1 for r in results if r.get("result", {}).get("prediction") == "Real"),
        "samples":    results,
    }

    path = os.path.join(results_dir, f"period_{period_num}.json")
    with open(path, "w") as f:
        json.dump(output, f, indent=4)

    logger.info(f"💾 Results saved: {path}")
    return path


def get_meeting_report(meeting_dir: str) -> dict:
    """Aggregates all period results into a full meeting report."""
    results_dir = _get_results_dir(meeting_dir)

    if not os.path.exists(results_dir):
        raise FileNotFoundError(f"No results found for meeting: {meeting_dir}")

    periods     = []
    total_fake  = 0
    total_real  = 0

    for filename in sorted(os.listdir(results_dir)):
        if filename.endswith(".json"):
            with open(os.path.join(results_dir, filename)) as f:
                data = json.load(f)
            periods.append(data)
            total_fake += data.get("fake_count", 0)
            total_real += data.get("real_count", 0)

    total   = total_fake + total_real
    verdict = "Fake" if total_fake > total_real else "Real"

    return {
        "meeting":         os.path.basename(meeting_dir),
        "total_samples":   total,
        "total_fake":      total_fake,
        "total_real":      total_real,
        "fake_percentage": round((total_fake / total * 100), 2) if total else 0,
        "verdict":         verdict,
        "periods":         periods,
    }