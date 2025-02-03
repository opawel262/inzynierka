from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi import staticfiles

from app.api.main import router as router_api


def create_db() -> None:
    """
    Function responsible for creating the database.
    """

    # Create the database
    Base.metadata.create_all(bind=engine)


def get_configured_server_app() -> FastAPI:
    app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

    add_pagination(app)

    app.include_router(router_api)

    # app.mount(
    #     "/media/uploads/user",
    #     staticfiles.StaticFiles(directory="app/media/uploads/user"),
    #     name="user_uploads",
    # )
    app.mount(
        "/static/", staticfiles.StaticFiles(directory="app/static"), name="static"
    )

    create_db()

    return app


server_app = get_configured_server_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:server_app", host="0.0.0.0", port=8000, reload=True, workers=2)
