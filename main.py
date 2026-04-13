import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/chat")
async def chat(request: ChatRequest):
    # PRUEBA 1: ¿Render está leyendo la clave?
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"response": "ERROR CRÍTICO: Render no está detectando tu variable GOOGLE_API_KEY. Revisa la pestaña Environment."}

    try:
        # PRUEBA 2: ¿La clave es válida para Google?
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        user_text = request.messages[-1].content
        response = model.generate_content(user_text)
        
        return {"response": response.text}

    except Exception as e:
        # PRUEBA 3: Si Google rechaza la conexión, aquí nos dirá por qué
        return {"response": f"ERROR DE GOOGLE: {str(e)}"}

@app.get("/")
async def home():
    return FileResponse("index.html")
