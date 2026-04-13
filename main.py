import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import google.generativeai as genai

app = FastAPI()

# Configuración de CORS para que tu frontend pueda hablar con el backend
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

# Configuración de Gemini con la clave de Render
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not API_KEY:
            return {"response": "Error: No se encontró la API KEY en Render."}
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        user_message = request.messages[-1].content
        response = model.generate_content(user_message)
        
        return {"response": response.text}
    except Exception as e:
        return {"response": f"Hubo un error interno: {str(e)}"}

@app.get("/health")
async def health():
    return {"status": "ok"}
