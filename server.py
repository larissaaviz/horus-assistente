from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from google import genai
from google.genai import types
import edge_tts
import os

app = FastAPI()

# Inicializa o cliente do Gemini
client = genai.Client()

@app.post("/process")
async def processar_dados(audio: UploadFile = File(...), image: UploadFile = File(None)):
    try:
        # 1. Ler os bytes do áudio
        audio_bytes = await audio.read()
        
        contents = [
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/3gp",
            )
        ]
        
        # 2. Só adiciona a imagem se ela realmente existir e tiver tamanho maior que zero (evita ficheiros vazios)
        if image:
            image_bytes = await image.read()
            if len(image_bytes) > 100: # Garante que não é um ficheiro vazio/dummy
                contents.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg",
                    )
                )
        
        contents.append("Responde de forma concisa e direta em português como o assistente Hórus, ajudando a tua criadora com base no que ouviste.")
        
        # 3. Gerar resposta inteligente com o Gemini 3.8-flash
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents
        )
        
        texto_resposta = response.text
        
    except Exception as e:
        texto_resposta = "Desculpa, criadora, ocorreu um erro ao processar os dados no servidor."
        print(f"Erro detalhado: {e}")
    
    # 4. Converter a resposta em voz natural usando o Edge-TTS
    output_audio_path = "resposta_horus.mp3"
    voice = "pt-BR-AntonioNeural" 
    communicate = edge_tts.Communicate(texto_resposta, voice)
    await communicate.save(output_audio_path)
    
    # 5. Devolver o áudio natural para o Android reproduzir
    return FileResponse(output_audio_path, media_type="audio/mp3")