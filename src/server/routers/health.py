from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/deepmeet/health")
async def health_check(request: Request):
    simulator = request.app.state.simulator
    detector = request.app.state.detector

    # Subsystem readiness checks
    sim_ready = simulator is not None
    det_ready = detector is not None

    # Check deeper subsystem health if available
    subsystems = {}
    if sim_ready:
        subsystems["stt_connected"] = getattr(simulator, '_stt_ready', False) if hasattr(simulator, '_stt_ready') else True
        subsystems["tts_ready"] = getattr(simulator, '_tts_ready', False) if hasattr(simulator, '_tts_ready') else True
        subsystems["llm_connected"] = getattr(simulator, '_llm_ready', False) if hasattr(simulator, '_llm_ready') else True
    if det_ready:
        subsystems["detector_models_loaded"] = getattr(detector, '_ready', False) if hasattr(detector, '_ready') else True

    detection_active = getattr(request.app.state, "detection_active", False)

    return {
        "status": "healthy" if (sim_ready and det_ready) else "degraded",
        "simulator_ready": sim_ready,
        "detector_ready": det_ready,
        "detection_active": detection_active,
        "subsystems": subsystems,
    }