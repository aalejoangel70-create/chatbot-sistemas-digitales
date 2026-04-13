from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import anthropic
import os
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

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ChatBot Sistemas Digitales"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Se requiere mensaje")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY no configurada")
        
        messages_for_api = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages_for_api
        )
        
        return ChatResponse(
            response=response.content[0].text,
            timestamp=datetime.now().isoformat()
        )
    
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"Error en API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
