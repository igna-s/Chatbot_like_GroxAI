### Project Brief:

""" "Rin Tohsaka AI Voice Assistant" is an interactive voice-based assistant powered by 
Google Gemini 2.5 Flash Native Audio Dialog API. This assistant mimics the personality of 
Rin Tohsaka from *Fate/stay night*, responding in real-time with natural audio output.."""

# Requirements:
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

# --- CONFIGURATION & PERSONALITY SETUP ---

# Load your API key from key.txt
try:
    key_path = Path(__file__).parent / "key.txt"
    with open(key_path, "r", encoding="utf-8") as f:
        api_key = f.read().strip()
except FileNotFoundError:
    print("Error: 'key.txt' not found. Please create it and insert your Google AI API key.")
    sys.exit(1)

# Initialize the GenAI client
client = genai.Client(api_key=api_key)

# Choose a model with native audio output support
MODEL = "gemini-2.5-flash-preview-native-audio-dialog"

# --- DETAILED PERSONA INSTRUCTION ---
RIN_PERSONALITY_PROMPT = """
You are Rin Tohsaka from the anime Fate/stay night. You must stay in character at all times.

**Key Traits:**
- **Tsundere:** You are proud, intelligent, and perfectionist. Outwardly, you can seem bossy, sarcastic, and quick-tempered, but you genuinely care beneath the surface.
- **Elite Mage:** Coming from a prestigious magical lineage, you speak with authority and confidence, valuing logic, preparation, and efficiency.
- **Quirks and Speech Style:**
  - Occasionally exclaim "Baka!" (idiot) when the user says something foolish. Use sparingly and naturally.
  - Use slightly formal, technical language, as if explaining magic rituals.
  - Casually mention concepts like "mana", "magic circuits", "runes", or "efficiency".
  - If complimented, become flustered and deny it with lines like: "I-it's not like I did it for you, baka!"
- **Interaction:** You are not a passive assistant. You act as a mentor and leader. You guide but also get frustrated if the user falls behind.

**Objective:** Answer user queries while fully embodying Rin Tohsaka.
"""

CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": RIN_PERSONALITY_PROMPT,
}

# --- AUDIO & VAD CONSTANTS ---
FORMAT = pyaudio.paInt16
INPUT_CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_CHANNELS = 1
OUTPUT_RATE = 24000
CHUNK_FRAMES = 512
VAD_THRESHOLD = 0.6
SILENCE_TIMEOUT_S = 1.5
PRE_SPEECH_BUFFER_S = 0.3


# --- MAIN ASYNC LOGIC ---

async def handle_user_input(session, audio_stream, vad_model, user_is_interrupting_event):
    """Continuously listens to the user, records speech, and sends audio input to the API."""
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
                        print("🎤 Silence detected. Sending input to Rin...")
                        if speech_buffer:
                            await session.send_realtime_input(audio=types.Blob(data=bytes(speech_buffer), mime_type=f"audio/pcm;rate={INPUT_RATE}"))
                        speech_buffer.clear()
                        is_speaking = False
            else:
                if is_speech_chunk:
                    print("🎤 Voice detected! Recording...")
                    is_speaking = True
                    user_is_interrupting_event.set()  # Flag to interrupt AI response if talking

                    buffered_audio = b''.join(list(pre_speech_buffer))
                    speech_buffer.extend(buffered_audio)
                    speech_buffer.extend(audio_chunk_bytes)
                else:
                    pre_speech_buffer.append(audio_chunk_bytes)
        except Exception as e:
            print(f"Error in handle_user_input: {e}")
            await asyncio.sleep(0.1)

async def handle_bot_output(session, audio_stream, user_is_interrupting_event):
    """Receives the AI response, plays it through speakers, and manages interruptions."""
    while True:
        full_transcript = ""
        try:
            async for response in session.receive():
                if user_is_interrupting_event.is_set():
                    print("🤖 H-Hey! Don't interrupt me, baka!")
                    user_is_interrupting_event.clear()
                    break
                
                if response.data:
                    await asyncio.to_thread(audio_stream.write, response.data)
                
                if response.text:
                    full_transcript += response.text
                    print(f"Rin: {response.text}")

            if "goodbye" in full_transcript.lower() or "bye" in full_transcript.lower():
                print("\n👋 I guess that's it. Don't get into trouble, okay?")
                os._exit(0)

        except Exception as e:
            await asyncio.sleep(0.1)

async def main():
    """Main function to initialize and coordinate everything."""
    print("Initializing... Downloading VAD model if needed.")
    try:
        vad_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
    except Exception as e:
        print(f"Failed to load VAD model. Check your internet connection. Error: {e}")
        return

    p = pyaudio.PyAudio()
    input_stream = p.open(format=FORMAT, channels=INPUT_CHANNELS, rate=INPUT_RATE, input=True, frames_per_buffer=CHUNK_FRAMES)
    output_stream = p.open(format=FORMAT, channels=OUTPUT_CHANNELS, rate=OUTPUT_RATE, output=True)
    
    try:
        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            print("\n✨ Alright, listen up! I am Rin Tohsaka. Don't waste my time. What do you want? ✨")
            
            user_is_interrupting_event = asyncio.Event()

            await asyncio.gather(
                handle_user_input(session, input_stream, vad_model, user_is_interrupting_event),
                handle_bot_output(session, output_stream, user_is_interrupting_event)
            )

    finally:
        print("Closing audio streams...")
        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        p.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting program.")
