from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import List
from google import genai
from google.genai import types
import edge_tts
import os

app = FastAPI()

client = genai.Client()

@app.post("/process")
async def processar_dados(audio: UploadFile = File(...), images: List[UploadFile] = File(None)):
    try:
        audio_bytes = await audio.read()
        
        contents = [
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/3gp",
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
            model="gemini-2.5-flash",
            contents=contents
        )
        
        texto_resposta = response.text
        
    except Exception as e:
        texto_resposta = "Desculpa, criadora, ocorreu um erro ao processar os dados no servidor."
        print(f"Erro detalhado: {e}")
    
    output_audio_path = "resposta_horus.mp3"
    voice = "pt-BR-AntonioNeural" # Voz humanizada em português
    communicate = edge_tts.Communicate(texto_resposta, voice)
    await communicate.save(output_audio_path)
    
    return FileResponse(output_audio_path, media_type="audio/mp3")
