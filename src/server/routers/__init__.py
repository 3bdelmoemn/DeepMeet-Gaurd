from .health import router as health_router
from .data import router as data_router
from .setup import router as setup_router
from .communication import router as communication_router

__all__ = [
    "health_router",
    "data_router",
    "setup_router",
    "communication_router",

]