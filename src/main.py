from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers import health_router,data_router,setup_router,communication_router,detection_router
from server.services import detector, simulator
from server.helpers import get_config
import logging
import sys

# ── Structured logging ──────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logger = logging.getLogger("deepmeet-guard")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up DeepMeet Guard API...")
    try:
        app.state.config = get_config()
        app.state.simulator = simulator
        app.state.detector = detector

        logger.info("  → Initializing simulator...")
        simulator.setup()
        logger.info("  ✅ Simulator ready.")

        logger.info("  → Initializing detector...")
        detector.setup()
        logger.info("  ✅ Detector ready.")

        logger.info("✅ All subsystems initialized.")
    except Exception as e:
        logger.critical("❌ Startup failed: %s", e, exc_info=True)
        raise

    yield

    logger.info("🛑 Shutting down...")
    try:
        simulator.cleanup()
        detector.cleanup()
    except Exception as e:
        logger.error("⚠️ Cleanup error: %s", e)
    logger.info("✅ Cleanup complete.")

app = FastAPI(title="DeepMeet Guard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

app.include_router(health_router)
app.include_router(data_router)
app.include_router(setup_router)
app.include_router(communication_router)
app.include_router(detection_router)

