
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS configuration for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(prompt: Prompt):
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise HTTPException(
            status_code=500,
            detail="HF_TOKEN not found in environment variables"
        )

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt.prompt.strip()
    }

    for attempt in range(3):
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                full_response = result[0]["generated_text"]

                # Smart extraction logic to remove echoed prompt
                output = full_response.replace(prompt.prompt.strip(), "", 1).strip()

                return {"result": output}

            raise HTTPException(
                status_code=500,
                detail="Unexpected response format from Hugging Face API"
            )

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 503 and attempt < 2:
                time.sleep(2)
                continue
            raise HTTPException(
                status_code=response.status_code,
                detail=f"HTTP error occurred: {http_err}"
            )
        except Exception as err:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred: {err}"
            )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            prompt = await websocket.receive_text()
            hf_token = os.getenv("HF_TOKEN")
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "inputs": prompt.strip()
            }

            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                headers=headers,
                json=payload
            )
            result = response.json()
            output = result[0]["generated_text"].replace(prompt.strip(), "").strip()

            await websocket.send_json({"text": output})
        except Exception:
            await websocket.close(code=1001)
            break

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)