from fastapi import FastAPI, Request
from fastapi_pagination import add_pagination
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from app.core.database import engine
from app.api.main import router as router_api
from app.domain.model_base import Base
from app.admin import create_admin
from app.core.utils import limiter
from app.core.handlers import custom_rate_limit_handler
from fastapi_pagination.utils import disable_installed_extensions_check


def create_db() -> None:
    """
    Function responsible for creating the database.
    """
    # Create the database
    Base.metadata.create_all(bind=engine)


def get_configured_server_app() -> FastAPI:
    disable_installed_extensions_check()
    app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

    app.state.limiter = limiter

    # Add exception handler here after FastAPI app is created
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

    add_pagination(app)
    app.include_router(router_api)

    # TODO: add case for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    create_db()
    create_admin(app=app, engine=engine)

    return app


server_app = get_configured_server_app()

# Mounting static directories
server_app.mount("/media", StaticFiles(directory="app/media"), name="media")
server_app.mount("/static", StaticFiles(directory="app/static"), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:server_app", host="0.0.0.0", port=8000, reload=True, workers=2)
