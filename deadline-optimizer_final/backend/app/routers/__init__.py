from .courses import router as courses_router
from .assignments import router as assignments_router
from .deadlines import router as deadlines_router
from .analytics import router as analytics_router

__all__ = [
    "courses_router",
    "assignments_router",
    "deadlines_router",
    "analytics_router",
]
