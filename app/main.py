from fastapi import FastAPI

from app.config import settings
from app.routers import (
    admin,
    auth,
    health,
    movies,
    ratings,
    recommendations,
    users,
    watch_history,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        debug=settings.debug,
    )

    app.include_router(health.router)

    feature_routers = (
        auth.router,
        users.router,
        movies.router,
        watch_history.router,
        ratings.router,
        recommendations.router,
        admin.router,
    )
    for router in feature_routers:
        app.include_router(router, prefix=settings.api_prefix)

    return app


app = create_app()
