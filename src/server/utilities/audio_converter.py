"""
Audio Converter Utility
Converts any audio file to .wav format, saves it in the same directory,
and removes the original file.
"""

import os
import subprocess
from pathlib import Path
import os
import threading
import time
import pyaudio
import wave
import tempfile
import librosa
import numpy as np
from datetime import datetime
import logging
import soundfile as sf
# import soundcard as sc



SUPPORTED_EXTENSIONS = {
    ".mp3", ".mp4", ".m4a", ".aac", ".ogg", ".flac",
    ".wma", ".aiff", ".aif", ".opus", ".webm", ".amr"
}


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio file to .wav format.

    - Saves the .wav file in the same directory as the input.
    - Deletes the original file after successful conversion.

    Args:
        input_path (str): Absolute or relative path to the input audio file.

    Returns:
        str: Path to the converted .wav file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the file extension is not supported.
        RuntimeError: If the conversion fails.
    """
    input_path = Path(input_path).resolve()

    # ── Validation ──────────────────────────────────────────────────────────
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.is_file():
        raise ValueError(f"Path is not a file: {input_path}")

    ext = input_path.suffix.lower()

    if ext == ".wav":
        print(f"[INFO] File is already .wav — no conversion needed: {input_path}")
        return str(input_path)

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported extension '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # ── Build output path ────────────────────────────────────────────────────
    output_path = input_path.with_suffix(".wav")

    # Guard: avoid overwriting an existing .wav that is NOT the source file
    if output_path.exists():
        print(f"[WARNING] Output file already exists and will be overwritten: {output_path}")

    # ── Convert with ffmpeg ──────────────────────────────────────────────────
    cmd = [
        "ffmpeg",
        "-y",                    # overwrite output if exists
        "-i", str(input_path),   # input
        "-vn",                   # drop video streams (if any)
        "-acodec", "pcm_s16le",  # standard 16-bit PCM WAV
        "-ar", "44100",          # sample rate 44.1 kHz
        "-ac", "2",              # stereo
        str(output_path),
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"ffmpeg conversion failed for '{input_path}':\n{error_msg}"
        )

    # ── Remove original ──────────────────────────────────────────────────────
    input_path.unlink()
    print(f"[INFO] Converted & replaced: '{input_path.name}' → '{output_path.name}'")
    print(f"[INFO] Saved at: {output_path}")

    return str(output_path)


# def record_speaker_audio(duration: int = 8, sample_rate: int = 44100):
#     print("🎙️ Recording directly from system speakers (WASAPI Loopback)...")
    
#     try:
#         # 1. بنسأل ويندوز: إيه السماعة الأساسية اللي مطلعة صوت دلوقتي؟
#         default_speaker = sc.default_speaker()
        
#         # 2. بنجيب المايك الافتراضي اللي بيسجل من السماعة دي (Loopback)
#         mics = sc.all_microphones(include_loopback=True)
#         loopback_mic = None
        
#         for mic in mics:
#             if mic.isloopback and mic.name == default_speaker.name:
#                 loopback_mic = mic
#                 break
                
#         # لو ملقاش الـ Loopback (نادر جداً)، هيستخدم المايك العادي كاحتياطي
#         if not loopback_mic:
#             print("⚠️ Loopback not found, falling back to default mic.")
#             loopback_mic = sc.default_microphone()
            
#         # 3. بدء التسجيل!
#         with loopback_mic.recorder(samplerate=sample_rate, channels=2) as mic:
#             recording = mic.record(numframes=sample_rate * duration)
            
#         # 4. حفظ الملف
# # 4. حفظ الملف
#             os.makedirs("detection_audio", exist_ok=True)
#             filename = f"speaker_{int(time.time())}.wav"

#             # Create the relative path: "detection_audio/speaker_123.wav"
#             relative_filepath = os.path.join("detection_audio", filename)

#             # Convert THAT relative path into an absolute path
#             filepath = os.path.abspath(relative_filepath)

#             sf.write(filepath, recording, sample_rate)
#             print(f"✅ Saved successfully: {filepath}")
#             return filepath
#     except Exception as e:
#         print(f"❌ Recording error: {e}")
#         return None
