from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from database import init_db
from routers import loads, fmcsa, calls

app = FastAPI(
    title="HappyRobot Carrier Sales API",
    description="Backend API for inbound carrier load sales automation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


app.include_router(loads.router)
app.include_router(fmcsa.router)
app.include_router(calls.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
