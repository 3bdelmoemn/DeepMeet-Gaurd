from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["detection"])


@router.get("/api/detection/latest")
async def get_latest_detection():
    from main import last_detection_result
    return JSONResponse(last_detection_result)


@router.post("/api/detection/start")
async def start_detection():
    """Start periodic speaker detection"""
    from main import start_periodic_detection, detection_thread, detection_stop_flag
    
    if detection_thread is not None and detection_thread.is_alive():
        return JSONResponse({"status": "already_running", "message": "Detection already running"})
    
    detection_stop_flag = False
    detection_thread = start_periodic_detection()
    
    return JSONResponse({"status": "success", "message": "Detection started"})


@router.post("/api/detection/stop")
async def stop_detection():
    """Stop periodic speaker detection"""
    from main import detection_stop_flag, detection_thread
    
    detection_stop_flag = True
    if detection_thread and detection_thread.is_alive():
        detection_thread.join(timeout=3)
    
    return JSONResponse({"status": "success", "message": "Detection stopped"})