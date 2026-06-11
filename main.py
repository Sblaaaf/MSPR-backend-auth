from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyctuator.pyctuator import Pyctuator

from app.routes import router

app = FastAPI(
    title="HealthAI Auth Service",
    description="Service d'authentification pour HealthAI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

Pyctuator(
    app,
    "HealthAI Auth Service",
    app_url="http://localhost:8004",
    pyctuator_endpoint_url="http://localhost:8004/pyctuator",
    registration_url=None,
)
