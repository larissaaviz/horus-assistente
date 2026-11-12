from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import List
from google import genai
from google.genai import types
import edge_tts
import os

app = FastAPI()

# Endpoint de rastreio para o Render saber que o serviço está online
@app.get("/")
def read_root():
    return {"status": "Hórus está online e operacional, criadora!"}

client = genai.Client()

@app.post("/process")
async def processar_dados(audio: UploadFile = File(...), images: List[UploadFile] = File(None)):
    try:
        audio_bytes = await audio.read()
        print(f"Tamanho do áudio recebido: {len(audio_bytes)} bytes")
        
        if len(audio_bytes) < 100:
            return {"error": "Áudio vazio recebido"}

        contents = [
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/mp4",
            )
        ]
        
        if images:
            for img in images:
                img_bytes = await img.read()
                if len(img_bytes) > 100:
                    contents.append(
                        types.Part.from_bytes(
                            data=img_bytes,
                            mime_type="image/jpeg",
                        )
                    )
        
        contents.append("Responde de forma concisa, direta e humanizada em português como o assistente Hórus, ajudando a tua criadora com base no que ouviste.")
        
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )
        
        texto_resposta = response.text
        
    except Exception as e:
        texto_resposta = "Desculpa, criadora, ocorreu um erro ao processar os dados no servidor."
        print(f"Erro detalhado: {e}")
    
    output_audio_path = "resposta_horus.mp3"
    voice = "pt-BR-AntonioNeural"
    communicate = edge_tts.Communicate(texto_resposta, voice)
    await communicate.save(output_audio_path)
    
    return FileResponse(output_audio_path, media_type="audio/mp3")
