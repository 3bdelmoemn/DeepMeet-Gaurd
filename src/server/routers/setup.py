from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from server.utilities import get_user_session, get_user_audio_path, get_user_text_path
import logging

logger = logging.getLogger('uvicorn.error')

router = APIRouter(tags=["Simulator Setup"], prefix="/deepmeet/simulator/setup")


# ============================================================
# Impersonate
# ============================================================
@router.post("/impersonate")
async def impersonate(user_id: str, request: Request):
    try:
        user_info, org_info = get_user_session(user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"User session not found: {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to load user session [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Failed to load user session")

    try:
        simulator = request.app.state.simulator
        simulator.impersonate(user_info=user_info, organization_info=org_info)
        logger.info(f"✅ Impersonation complete for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ Impersonation failed [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Impersonation failed")

    return JSONResponse({
        "status": "success",
        "message": "Impersonation complete",
        "user_id": user_id,
    })


# ============================================================
# Clone
# ============================================================
@router.post("/clone")
async def clone(user_id: str, request: Request):
    try:
        audio_path = get_user_audio_path(user_id)
        text_path = get_user_text_path(user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"User session not found: {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to get user paths [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Failed to load user files")

    try:
        simulator = request.app.state.simulator
        simulator.update_reference(ref_audio_path=audio_path, ref_text_path=text_path)
        logger.info(f"✅ Cloning complete for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ Cloning failed [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Cloning failed")

    return JSONResponse({
        "status": "success",
        "message": "Cloning complete",
        "user_id": user_id,
    })