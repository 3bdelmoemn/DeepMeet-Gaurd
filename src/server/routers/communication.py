from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import threading
import logging

logger = logging.getLogger('uvicorn.error')

router = APIRouter(tags=["Simulator communication"], prefix="/deepmeet/simulator/communication")


# ============================================================
# Start
# ============================================================
@router.post("/start")
async def start_simulation(user_id: str, request: Request):
    simulator = request.app.state.simulator

    # منع تشغيل أكتر من simulation في نفس الوقت
    if hasattr(request.app.state, "simulation_thread") and \
       request.app.state.simulation_thread is not None and \
       request.app.state.simulation_thread.is_alive():
        raise HTTPException(status_code=409, detail="Simulation already running")

    try:
        thread = threading.Thread(
            target=simulator.communicate,
            daemon=True,
            name=f"simulation-{user_id}"
        )
        request.app.state.simulation_thread = thread
        request.app.state.simulation_user_id = user_id
        thread.start()
        logger.info(f"✅ Simulation started for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ Simulation start failed [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Simulation start failed")

    return JSONResponse({
        "status": "success",
        "message": "Simulation started",
        "user_id": user_id,
    })


# ============================================================
# End
# ============================================================
@router.post("/end")
async def end_simulation(user_id: str, request: Request):
    simulator = request.app.state.simulator

    # تأكد إن في simulation شغالة
    thread: threading.Thread = getattr(request.app.state, "simulation_thread", None)
    if thread is None or not thread.is_alive():
        raise HTTPException(status_code=409, detail="No simulation is running")

    try:
        simulator.cleanup()
        thread.join(timeout=5)
        request.app.state.simulation_thread = None
        request.app.state.simulation_user_id = None
        logger.info(f"✅ Simulation ended for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ Simulation end failed [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Simulation end failed")

    return JSONResponse({
        "status": "success",
        "message": "Simulation ended",
        "user_id": user_id,
    })


# ============================================================
# Report
# ============================================================
@router.post("/report")
async def report_simulation(user_id: str, request: Request):
    simulator = request.app.state.simulator

    try:
        report = simulator.get_report()
        logger.info(f"✅ Report generated for user: {user_id}")
    except Exception as e:
        logger.error(f"❌ Report generation failed [{user_id}]: {e}")
        raise HTTPException(status_code=500, detail="Simulation report failed")

    return JSONResponse({
        "status": "success",
        "message": "Simulation report generated",
        "user_id": user_id,
        "report": report,
    })