from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.routers import *


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

    # app.include_router(users_router)
    # app.include_router(referrals_router)
    # app.include_router(admin_router)
    # app.include_router(ledger_router)
    # app.include_router(skill_router)
    # app.include_router(chats_router)
    # app.include_router(auth_router)
    # app.include_router(notifications_router)
    # app.include_router(search_users_router)

    return app
