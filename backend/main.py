from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body model
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
        "inputs": prompt.prompt
    }

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1", 
                headers=headers, 
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                return {"result": result[0]["generated_text"]}
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Unexpected response format from Hugging Face API"
                )
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 503 and attempt < 2:
                time.sleep(2)  # Wait before retrying
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

# Example root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}