"""
Audio Converter Utility
Converts any audio file to .wav format, saves it in the same directory,
and removes the original file.
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)



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
        logger.info("File is already .wav — no conversion needed: %s", input_path)
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
        logger.warning("Output file already exists and will be overwritten: %s", output_path)

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

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"ffmpeg conversion timed out after 120 seconds for '{input_path}'"
        )

    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"ffmpeg conversion failed for '{input_path}':\n{error_msg}"
        )

    # ── Remove original ──────────────────────────────────────────────────────
    input_path.unlink()
    logger.info("Converted & replaced: '%s' → '%s'", input_path.name, output_path.name)
    logger.info("Saved at: %s", output_path)

    return str(output_path)



