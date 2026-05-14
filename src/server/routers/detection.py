from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from server.utilities import (
    create_meeting_session,
    capture_speaker_audio,
    run_period_detection,
    save_period_results,
    get_meeting_report,
    _get_meeting_dir,
    _get_period_dir,
)
from server.helpers import get_config
import threading
import logging

settings = get_config()
logger   = logging.getLogger('uvicorn.error')

router = APIRouter(tags=["Detector"], prefix="/deepmeet/detector")


# ============================================================
# Start Detection
# ============================================================
@router.post("/start")
async def start_detection(meeting_name: str, request: Request):
    detector = request.app.state.detector

    # منع تشغيل أكتر من detection في نفس الوقت
    if getattr(request.app.state, "detection_active", False):
        raise HTTPException(status_code=409, detail="Detection already running")

    try:
        meeting_dir = create_meeting_session(meeting_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create meeting session: {e}")

    def _detection_loop():
        request.app.state.detection_active   = True
        request.app.state.detection_meeting  = meeting_dir
        period_num = 1

        try:
            while request.app.state.detection_active:
                logger.info(f"📍 Starting period {period_num}...")

                # 1. Capture
                try:
                    saved_files = capture_speaker_audio(
                        meeting_dir=meeting_dir,
                        period_num=period_num,
                        max_duration=settings.DETECTOR_MAX_DURATION,
                    )
                except Exception as e:
                    logger.error(f"❌ Capture failed period {period_num}: {e}")
                    break

                # 2. Detect in parallel
                period_dir = _get_period_dir(meeting_dir, period_num)
                results    = run_period_detection(detector, period_dir, period_num)

                # 3. Save results
                save_period_results(meeting_dir, period_num, results)

                period_num += 1

                # انتظر الـ interval الجاي
                logger.info(f"⏳ Waiting {settings.DETECTOR_PERIOD_INTERVAL}s for next period...")
                for _ in range(settings.DETECTOR_PERIOD_INTERVAL):
                    if not request.app.state.detection_active:
                        break
                    threading.Event().wait(1)

        except Exception as e:
            logger.error(f"❌ Detection loop error: {e}")
        finally:
            request.app.state.detection_active = False
            logger.info("🛑 Detection loop stopped.")

    thread = threading.Thread(target=_detection_loop, daemon=True, name=f"detection-{meeting_name}")
    request.app.state.detection_thread = thread
    thread.start()

    logger.info(f"✅ Detection started for meeting: {meeting_name}")
    return JSONResponse({
        "status":       "success",
        "message":      "Detection started",
        "meeting_name": meeting_name,
    })


# ============================================================
# End Detection
# ============================================================
@router.post("/end")
async def end_detection(request: Request):
    if not getattr(request.app.state, "detection_active", False):
        raise HTTPException(status_code=409, detail="No detection is running")

    request.app.state.detection_active = False

    thread: threading.Thread = getattr(request.app.state, "detection_thread", None)
    if thread:
        thread.join(timeout=10)
        request.app.state.detection_thread = None

    logger.info("✅ Detection stopped.")
    return JSONResponse({
        "status":  "success",
        "message": "Detection stopped",
    })


# ============================================================
# Report
# ============================================================
@router.get("/report")
async def detection_report(meeting_name: str, request: Request):
    try:
        from server.utilities import _get_meeting_dir
        meeting_dir = _get_meeting_dir(meeting_name)
        report      = get_meeting_report(meeting_dir)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No results found for: {meeting_name}")
    except Exception as e:
        logger.error(f"❌ Report failed [{meeting_name}]: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

    return JSONResponse({
        "status": "success",
        "report": report,
    })