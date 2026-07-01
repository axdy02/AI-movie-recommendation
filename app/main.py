from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_origin_regex=settings.backend_cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
