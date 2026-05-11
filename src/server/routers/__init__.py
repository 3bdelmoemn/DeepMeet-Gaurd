from .health import router as health_router
from .setup import router as setup_router
from .chat import router as chat_router
from .detection import router as detection_router
from .cleanup import router as cleanup_router

__all__ = [
    "health_router",
    "setup_router",
    "chat_router",
    "detection_router",
    "cleanup_router"
]