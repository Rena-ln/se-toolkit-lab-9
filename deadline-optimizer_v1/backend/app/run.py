import uvicorn
from app.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_debug,
        log_level="info",
    )
