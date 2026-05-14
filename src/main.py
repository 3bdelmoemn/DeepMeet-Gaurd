from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers import health_router,data_router,setup_router,communication_router
from server.services import detector, simulator
from server.helpers import get_config
import logging

logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logger = logging.getLogger('uvicorn.error')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up DeepMeet Guard API...")
    try:
        app.state.config = get_config()
        app.state.simulator = simulator
        app.state.detector = detector
        simulator.setup()
        detector.setup()
        logger.info("✅ Initialization complete.")
    except Exception as e:
        logger.critical(f"❌ Startup failed: {e}")
        raise

    yield

    logger.info("🛑 Shutting down...")
    try:
        simulator.cleanup()
        detector.cleanup()
    except Exception as e:
        logger.error(f"⚠️ Cleanup error: {e}")
    logger.info("✅ Cleanup complete.")

app = FastAPI(title="DeepMeet Guard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(data_router)
app.include_router(setup_router)
app.include_router(communication_router)
# app.include_router(detection_router)
# app.include_router(cleanup_router)

