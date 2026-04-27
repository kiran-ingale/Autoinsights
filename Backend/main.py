import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from Backend/Agents/main/.env
env_path = Path(__file__).parent / "Agents" / "main" / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .agent_service import run_analysis
from .upload import upload_dataset

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(data: dict):
    return await run_analysis(data)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    return await upload_dataset(file)
