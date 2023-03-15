from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import *


def create_app():
    app = FastAPI()

    origins = [
        "http://localhost:3000",
        "localhost:3000",
        "http://localhost:3001",
        "localhost:3001",
        "http://localhost:3002",
        "localhost:3002"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.get("/", tags=["Healthcheck"])
    async def root():
        return {"message": "I'm Alive"}

    app.include_router(bots_router)
    app.include_router(users_router)
    app.include_router(chats_router)
    app.include_router(user_uploads_router)

    return app
