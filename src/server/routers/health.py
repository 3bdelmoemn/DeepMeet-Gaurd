from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/deepmeet/health")
async def health_check(request: Request):
    simulator = request.app.state.simulator
    detector = request.app.state.detector

    return {
        "status": "healthy",
        "simulator_ready": simulator is not None,
        "detector_ready": detector is not None,
    }