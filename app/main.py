from fastapi import FastAPI
from app.api.uploadFile import router as upload_router
from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


app = FastAPI()
app.include_router(upload_router)