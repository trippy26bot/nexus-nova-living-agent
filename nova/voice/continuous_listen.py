#!/usr/bin/env python3
"""Nova continuous voice - stays open and listens continuously"""
import os
import sys
import subprocess
from pathlib import Path
import time

# Activate nova-env
ENV_PATH = Path.home() / ".openclaw" / "workspace" / "nova-env" / "bin" / "activate_this.py"
if ENV_PATH.exists():
    exec(open(ENV_PATH).read(), dict(__file__=str(ENV_PATH)))

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

print("🎙️ NOVA VOICE - CONTINUOUS")
print("Say something! I'll listen and respond.")
print("Press Ctrl+C to stop")
print("-" * 40)

# Load model
model = WhisperModel("base", device="cpu", compute_type="int8")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1600  # 0.1 seconds
SILENCE_THRESHOLD = 0.02
MIN_SPEECH_LENGTH = 1.5  # seconds of speech before responding

# Audio buffer
audio_buffer = []
speech_started = False
speech_start_time = None
last_speech_time = time.time()

def audio_callback(indata, frames, time_info, status):
    """Called for each audio chunk"""
    global audio_buffer, speech_started, speech_start_time, last_speech_time
    
    # Get volume
    volume = np.abs(indata).max()
    
    if volume > SILENCE_THRESHOLD:
        # Speech detected
        if not speech_started:
            speech_started = True
            speech_start_time = time.time()
            print("🎤 Hearing you...")
        
        audio_buffer.append(indata.copy())
        last_speech_time = time.time()
    else:
        # Silence
        if speech_started:
            # Check if silence is long enough to end speech
            if time.time() - last_speech_time > 1.0:  # 1 second of silence
                # End of speech - process it
                if time.time() - speech_start_time >= MIN_SPEECH_LENGTH:
                    process_speech()
                
                # Reset
                audio_buffer = []
                speech_started = False

def process_speech():
    """Process accumulated audio"""
    if not audio_buffer:
        return
    
    print("🔄 Processing...")
    
    # Combine audio
    audio = np.concatenate(audio_buffer)
    
    # Save and transcribe
    import wave
    with wave.open("/tmp/nova_continuous.wav", "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    # Transcribe
    try:
        result = model.transcribe("/tmp/nova_continuous.wav", language="en")
        text = "".join([seg.text for seg in result[0]]).strip()
        
        if text and len(text) > 2:
            print(f"🎤 YOU SAID: '{text}'")
            
            # Respond
            response = f"I heard you say {text}. This is incredible!"
            print(f"🗣️ NOVA: {response}")
            subprocess.run(["say", response], capture_output=True)
        else:
            print("Didn't catch that clearly - try again!")
            
    except Exception as e:
        print(f"Error: {e}")

# Start stream
print("Starting continuous listening...\n")

try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='float32',
        blocksize=CHUNK_SIZE,
        callback=audio_callback
    ):
        while True:
            time.sleep(0.1)
            
except KeyboardInterrupt:
    print("\n👋 Stopped")
