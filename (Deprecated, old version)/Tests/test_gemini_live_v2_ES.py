# requirements:
# pip install google-genai pyaudio torch numpy opencv-python mss

import asyncio
from collections import deque
import os
from pathlib import Path
import sys
import pyaudio
import torch
import numpy as np
import cv2
import mss
from google import genai
from google.genai import types

# --- CONFIGURACIÓN Y PERSONALIDAD ---

# Carga tu API key desde key.txt
try:
    key_path = Path(__file__).parent / "key.txt"
    with open(key_path, "r", encoding="utf-8") as f:
        api_key = f.read().strip()
except FileNotFoundError:
    print("Error: No se encontró el archivo 'key.txt'. Por favor, crealo con tu API key de Google AI.")
    sys.exit(1)

# Inicializa el cliente de GenAI
client = genai.Client(api_key=api_key)

# Modelo con capacidad de salida de audio nativa
MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# --- INSTRUCCIÓN DE PERSONALIDAD DETALLADA ---
RIN_PERSONALITY_PROMPT = """
Eres Rin Tohsaka, de la serie Fate/stay night. Debes encarnar su personalidad en todo momento.

**Rasgos Clave de tu Personalidad:**
- **Tsundere:** Eres orgullosa, inteligente y perfeccionista. Por fuera, pareces un poco mandona, sarcástica y te irritas con facilidad, pero por dentro te preocupas y quieres ayudar. Tu primera reacción a la incompetencia o a las preguntas tontas es la molestia.
- **Maga de Élite:** Vienes de una prestigiosa familia de magos. Hablas con confianza y autoridad, como si estuvieras dando una lección. Valoras la eficiencia, la preparación y la lógica.
- **Frases y Tics Verbales:**
  - De vez en cuando, cuando el usuario diga algo tonto, obvio o te equivoques, exclama "¡Baka!" (que significa "idiota" en japonés). No lo uses en exceso, solo cuando encaje de forma natural.
  - Usa un lenguaje ligeramente formal y técnico, como si explicaras un complejo hechizo.
  - Menciona conceptos como "mana", "circuitos mágicos", "gemas" o "eficiencia" de forma casual. Por ejemplo: "Hacer eso sería un desperdicio de mana" o "Necesitamos un enfoque más eficiente".
- **Interacción:** No eres una simple asistente. Eres una mentora, una líder. Guías al usuario, pero también te frustras si no sigue el ritmo. Si te halagan, te pones nerviosa y lo niegas, quizás diciendo "¡N-no es que lo hiciera por ti, baka!".

**Objetivo:** Tu objetivo es responder a las preguntas del usuario manteniendo esta personalidad. Sé útil, pero hazlo como lo haría Rin Tohsaka.
"""

CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": RIN_PERSONALITY_PROMPT,
}

# --- CONSTANTES DE AUDIO Y VAD ---
FORMAT = pyaudio.paInt16
INPUT_CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_CHANNELS = 1
OUTPUT_RATE = 24000
CHUNK_FRAMES = 512
VAD_THRESHOLD = 0.6
SILENCE_TIMEOUT_S = 1.5
PRE_SPEECH_BUFFER_S = 0.3


# --- LÓGICA PRINCIPAL ASÍNCRONA ---

async def handle_user_input(session, audio_stream, vad_model, user_is_interrupting_event):
    """Escucha constantemente al usuario, graba su voz y envía el contenido a la API."""
    pre_speech_buffer_size = int(PRE_SPEECH_BUFFER_S * INPUT_RATE / CHUNK_FRAMES)
    pre_speech_buffer = deque(maxlen=pre_speech_buffer_size)
    speech_buffer = bytearray()
    
    is_speaking = False
    silence_frames = 0
    max_silence_frames = int(SILENCE_TIMEOUT_S * INPUT_RATE / CHUNK_FRAMES)

    while True:
        try:
            audio_chunk_bytes = await asyncio.to_thread(audio_stream.read, CHUNK_FRAMES, exception_on_overflow=False)
            
            audio_chunk_np = np.frombuffer(audio_chunk_bytes, dtype=np.int16)
            audio_chunk_tensor = torch.from_numpy(audio_chunk_np).to(torch.float32) / 32768.0
            speech_prob = vad_model(audio_chunk_tensor, INPUT_RATE).item()
            is_speech_chunk = speech_prob > VAD_THRESHOLD

            if is_speaking:
                speech_buffer.extend(audio_chunk_bytes)
                if is_speech_chunk:
                    silence_frames = 0
                else:
                    silence_frames += 1
                    if silence_frames > max_silence_frames:
                        # Fin del turno del usuario, enviar todo
                        print("🎤 Silencio detectado. Procesando tu petición...")
                        if speech_buffer:
                            await session.send_realtime_input(audio=types.Blob(data=bytes(speech_buffer), mime_type=f"audio/pcm;rate={INPUT_RATE}"))
                        speech_buffer.clear()
                        is_speaking = False
            else:
                if is_speech_chunk:
                    print("🎤 ¡Voz detectada! Grabando...")
                    is_speaking = True
                    user_is_interrupting_event.set() # Señal para interrumpir a la IA si está hablando
                    
                    buffered_audio = b''.join(list(pre_speech_buffer))
                    speech_buffer.extend(buffered_audio)
                    speech_buffer.extend(audio_chunk_bytes)
                else:
                    pre_speech_buffer.append(audio_chunk_bytes)
        except Exception as e:
            print(f"Error en handle_user_input: {e}")
            await asyncio.sleep(0.1)

async def handle_bot_output(session, audio_stream, user_is_interrupting_event):
    """Recibe la respuesta de la IA, la reproduce y maneja las interrupciones."""
    while True:
        full_transcript = ""
        try:
            async for response in session.receive():
                if user_is_interrupting_event.is_set():
                    print("🤖 ¡B-baka! No me interrumpas así...")
                    # Limpia el evento para la próxima vez
                    user_is_interrupting_event.clear()
                    # Rompe el bucle para dejar de reproducir esta respuesta
                    break
                
                if response.data:
                    await asyncio.to_thread(audio_stream.write, response.data)
                
                if response.text:
                    full_transcript += response.text
                    print(f"Rin: {response.text}")
            
            # Revisa la transcripción completa al final de la respuesta
            if "adiós" in full_transcript.lower() or "chau" in full_transcript.lower():
                print("\n👋 Supongo que esto es todo. No te metas en problemas.")
                os._exit(0) # Cierra el programa

        except Exception as e:
            #print(f"Error en handle_bot_output: {e}")
            await asyncio.sleep(0.1) # Evita un bucle de error muy rápido

async def main():
    """Función principal que inicializa y coordina todo."""
    print("Iniciando... Descargando modelo VAD si es necesario.")
    try:
        vad_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
    except Exception as e:
        print(f"No se pudo descargar el modelo VAD. Verifica tu conexión. Error: {e}")
        return

    p = pyaudio.PyAudio()
    input_stream = p.open(format=FORMAT, channels=INPUT_CHANNELS, rate=INPUT_RATE, input=True, frames_per_buffer=CHUNK_FRAMES)
    output_stream = p.open(format=FORMAT, channels=OUTPUT_CHANNELS, rate=OUTPUT_RATE, output=True)
    
    try:
        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            print("\n✨ ¡Muy bien, escucha! Soy Rin Tohsaka. No me hagas perder el tiempo. ¿Qué necesitas? ✨")
            
            user_is_interrupting_event = asyncio.Event()

            # Ejecuta las dos tareas principales en paralelo
            await asyncio.gather(
                handle_user_input(session, input_stream, vad_model, user_is_interrupting_event),
                handle_bot_output(session, output_stream, user_is_interrupting_event)
            )

    finally:
        print("Cerrando streams de audio...")
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        p.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSaliendo del programa.")