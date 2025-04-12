from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import logging
import time
from typing import Dict, Any
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Quantum.dev API",
    description="A zero-latency, AI-powered API for generating code and text using Mistral-7B-Instruct via Hugging Face's free Inference API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Generation",
            "description": "Endpoints for AI-driven code and text generation."
        },
        {
            "name": "Health",
            "description": "System status and health checks."
        }
    ]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for prompt input
class Prompt(BaseModel):
    prompt: str
    max_tokens: int = 200
    temperature: float = 0.7
    top_p: float = 0.95

@app.post(
    "/generate",
    tags=["Generation"],
    summary="Generate text or code with Mistral AI",
    description="Generate code, text, or chat responses using Mistral-7B-Instruct-v0.1."
)
async def generate(prompt: Prompt) -> Dict[str, Any]:
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        logger.error("HF_TOKEN not found")
        raise HTTPException(status_code=500, detail="Hugging Face API token not configured")

    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt.prompt.strip(),
        "parameters": {
            "max_new_tokens": prompt.max_tokens,
            "temperature": prompt.temperature,
            "top_p": prompt.top_p,
            "repetition_penalty": 1.1
        }
    }

    for attempt in range(3):
        try:
            logger.info(f"Sending prompt: {prompt.prompt[:50]}...")
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and result and "generated_text" in result[0]:
                output = result[0]["generated_text"].replace(prompt.prompt.strip(), "", 1).strip()
                logger.info("Generated response successfully")
                return {
                    "result": output,
                    "status": "success",
                    "model": "Mistral-7B-Instruct-v0.1"
                }

            logger.error("Unexpected response format")
            raise HTTPException(status_code=500, detail="Invalid response from AI model")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 503 and attempt < 2:
                logger.warning(f"Model loading, retrying in 2s (attempt {attempt + 1}/3)")
                await asyncio.sleep(2)
                continue
            logger.error(f"HTTP error: {http_err}")
            raise HTTPException(status_code=response.status_code, detail=f"AI service error: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request failed: {req_err}")
            raise HTTPException(status_code=500, detail="Failed to connect to AI service")
        except Exception as err:
            logger.error(f"Unexpected error: {err}")
            raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            prompt = await websocket.receive_text()
            if not prompt.strip():
                await websocket.send_json({"error": "Empty prompt received"})
                continue

            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                await websocket.send_json({"error": "API token not configured"})
                await websocket.close(code=1001)
                return

            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": prompt.strip(),
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "repetition_penalty": 1.1
                }
            }

            try:
                logger.info(f"WebSocket prompt: {prompt[:50]}...")
                response = requests.post(
                    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and result and "generated_text" in result[0]:
                    output = result[0]["generated_text"].replace(prompt.strip(), "", 1).strip()
                    await websocket.send_json({
                        "text": output,
                        "status": "success",
                        "model": "Mistral-7B-Instruct-v0.1"
                    })
                else:
                    await websocket.send_json({"error": "Invalid response from AI model"})

            except Exception as err:
                logger.error(f"WebSocket error: {err}")
                await websocket.send_json({"error": f"Failed to generate: {str(err)}"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as err:
        logger.error(f"WebSocket unexpected error: {err}")
        await websocket.send_json({"error": "Internal server error"})
    finally:
        await websocket.close(code=1001)

@app.get(
    "/",
    tags=["Health"],
    summary="API Root",
    description="Welcome message for Quantum.dev API."
)
async def root() -> Dict[str, str]:
    return {"message": "Welcome to Quantum.dev - AI-powered code and text generation with Mistral"}

@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check the status of Quantum.dev API and connectivity to Mistral AI."
)
async def health_check() -> Dict[str, str]:
    try:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise Exception("HF_TOKEN not configured")

        headers = {"Authorization": f"Bearer {hf_token}"}
        response = requests.get(
            "https://api-inference.huggingface.co/status",
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        return {
            "status": "healthy",
            "api": "Quantum.dev",
            "model": "Mistral-7B-Instruct-v0.1",
            "huggingface": "connected"
        }
    except Exception as err:
        logger.error(f"Health check failed: {err}")
        return {
            "status": "unhealthy",
            "api": "Quantum.dev",
            "error": str(err)
        }

@app.get(
    "/favicon.ico",
    tags=["Health"],
    include_in_schema=False
)
async def favicon():
    return Response(status_code=204)