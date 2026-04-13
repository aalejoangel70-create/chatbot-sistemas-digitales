import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
from datetime import datetime

app = FastAPI(
    title="ChatBot Sistemas Digitales",
    description="Asistente especializado en sistemas digitales",
    version="1.0.0"
)

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

class ChatResponse(BaseModel):
    response: str
    timestamp: str

SYSTEM_PROMPT = """Eres un investigador senior especializado en Sistemas Digitales. 
Tu rol es explicar conceptos complejos de manera clara y pedagógica.
ÁREAS DE EXPERTICIA:
1. Compuertas Lógicas (AND, OR, NOT, NAND, NOR, XOR, XNOR)
2. Álgebra de Boole y Simplificación de Circuitos
3. Circuitos Combinacionales y Secuenciales
4. Introducción a FPGA
5. Lenguajes HDL (VHDL, Verilog)
6. Lógica Digital y Sistemas Numéricos
7. Microcontroladores
Explica conceptos de forma progresiva (básico → avanzado).
Utiliza analogías cuando sea posible.
Proporciona ejemplos prácticos."""

# Configuración de Gemini
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(API_KEY),
        "service": "ChatBot Sistemas Digitales"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not API_KEY:
            raise HTTPException(status_code=500, detail="GOOGLE_API_KEY no configurada en Render")
        
        if not request.messages:
            raise HTTPException(status_code=400, detail="Se requiere mensaje")
        
        # Obtenemos el último mensaje del usuario
        user_message = request.messages[-1].content
        
        # Generar respuesta con Gemini
        response = model.generate_content(user_message)
        
        return ChatResponse(
            response=response.text,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

# Si no tienes carpeta 'static', esto servirá los archivos de la raíz
app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
