from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from google import genai
from google.genai import types
import edge_tts
import traceback
import wave
import io

app = FastAPI()

@app.get("/")
@app.head("/")
def read_root():
    return {"status": "Hórus está online e operacional, criadora!"}

client = genai.Client()

@app.post("/process")
async def processar_dados(audio: UploadFile = File(...), images: Optional[List[UploadFile]] = File(None)):
    try:
        audio_bytes = await audio.read()
        print(f"Tamanho do áudio recebido: {len(audio_bytes)} bytes")
        
        if len(audio_bytes) < 100:
            raise HTTPException(status_code=400, detail="Áudio demasiado pequeno ou vazio.")

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)      # Mono
            wav_file.setsampwidth(2)      # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            wav_file.writeframes(audio_bytes)
        wav_bytes = wav_buffer.getvalue()

        contents = [
            types.Part.from_bytes(
                data=wav_bytes,
                mime_type="audio/wav",
            )
        ]
        
        if images:
            for img in images:
                img_bytes = await img.read()
                print(f"Tamanho da imagem recebida: {len(img_bytes)} bytes")
                if len(img_bytes) > 50:
                    contents.append(
                        types.Part.from_bytes(
                            data=img_bytes,
                            mime_type="image/jpeg",
                        )
                    )
        
        contents.append("Responde de forma concisa, direta e humanizada em português como o assistente Hórus, ajudando a tua criadora com base no que ouviste e viste.")
        
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )
        
        texto_resposta = response.text
        
    except Exception as e:
        print("--- ERRO DETALHADO NO SERVIDOR ---")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    output_audio_path = "resposta_horus.mp3"
    voice = "pt-BR-AntonioNeural"
    communicate = edge_tts.Communicate(texto_resposta, voice)
    await communicate.save(output_audio_path)
    
    return FileResponse(output_audio_path, media_type="audio/mp3")
