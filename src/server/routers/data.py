from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from server.models.schemas import InterviewSetupRequest
from server.utilities import (
    create_user_session,
    get_user_audio_path,
    get_user_text_path,
)
from server.utilities import convert_to_wav
import aiofiles
import os
import logging

logger = logging.getLogger('uvicorn.error')

router = APIRouter(tags=["Simulator Data"], prefix="/deepmeet/simulator/data")

# Upload limits (bytes)
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50 MB
MAX_TEXT_SIZE  = 1 * 1024 * 1024    # 1 MB


# ============================================================
# 1. Upload user info + organization info
# ============================================================
@router.post("/upload/info")
async def upload_info(interview_setup: InterviewSetupRequest):
    try:
        user_id = create_user_session(interview_setup)
        logger.info(f"✅ Session created for: {interview_setup.user_info.name}")
        return JSONResponse({
            "status": "success",
            "message": "User info saved successfully",
            "user_id": user_id,
        })
    except Exception as e:
        logger.error(f"❌ Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 2. Upload audio + reference text
# ============================================================
@router.post("/upload/references")
async def upload_references(
    user_id: str = Form(...),
    audio: UploadFile = File(...),
    reference_text: UploadFile = File(...),
):
    # Validate file sizes before processing
    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail=f"Audio file too large ({len(audio_bytes)} bytes). Max: {MAX_AUDIO_SIZE} bytes")
    text_bytes = await reference_text.read()
    if len(text_bytes) > MAX_TEXT_SIZE:
        raise HTTPException(status_code=413, detail=f"Text file too large ({len(text_bytes)} bytes). Max: {MAX_TEXT_SIZE} bytes")
    # Get paths
    try:
        original_ext = os.path.splitext(audio.filename)[1] or ".wav"
        audio_path = get_user_audio_path(user_id, ext=original_ext)
        text_path = get_user_text_path(user_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Save audio
    try:
        async with aiofiles.open(audio_path, "wb") as f:
            await f.write(audio_bytes)
        logger.info(f"✅ Audio saved: {audio_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save audio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save audio: {e}")

    # Convert to WAV if needed
    if original_ext.lower() != ".wav":
        try:
            wav_path = convert_to_wav(audio_path)
            os.remove(audio_path)
            audio_path = wav_path
            logger.info(f"✅ Converted to WAV: {wav_path}")
        except Exception as e:
            logger.error(f"❌ Audio conversion failed: {e}")
            raise HTTPException(status_code=500, detail=f"Audio conversion failed: {e}")

    # Save reference text
    try:
        async with aiofiles.open(text_path, "wb") as f:
            await f.write(text_bytes)
        logger.info(f"✅ Reference text saved: {text_path}")
    except Exception as e:
        logger.error(f"❌ Failed to save reference text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save reference text: {e}")

    return JSONResponse({
        "status": "success",
        "message": "Audio and reference text uploaded successfully",
        "user_id": user_id,
    })