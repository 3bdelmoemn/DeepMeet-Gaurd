from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check():
    from main import assistant, stt_thread
    
    return {
        "status": "healthy",
        "assistant_ready": assistant is not None,
        "listening_active": stt_thread is not None and stt_thread.is_alive() if stt_thread else False
    }