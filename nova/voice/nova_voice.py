#!/usr/bin/env python3
"""
Nova Voice - Full Brain Integration
Routes voice through Nova's real cognition
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# Setup paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
ENV_PATH = WORKSPACE / "nova-env" / "bin" / "activate_this.py"
sys.path.insert(0, str(WORKSPACE))

# Activate nova-env
if ENV_PATH.exists():
    exec(open(ENV_PATH).read(), dict(__file__=str(ENV_PATH)))

import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# Config
GAIN = 5.0
SAMPLE_RATE = 16000
DEVICE = 1  # JLab

print("🎙️ NOVA VOICE - WITH MY BRAIN")
print("Say 'Nova' to wake me!")
print("-" * 40)

# Load Whisper once
print("Loading Whisper...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Ready!\n")

def get_nova_response(text):
    """Route through MY brain via API or direct"""
    # Try API first
    try:
        import requests
        resp = requests.post(
            "http://localhost:5000/chat",
            json={"message": text, "channel": "voice", "user": "Caine"},
            timeout=15
        )
        return resp.json().get("response", "I heard you!")
    except:
        pass
    
    # Fallback - simple response
    return f"I heard you say {text}. Give me a moment to think..."

def speak(text):
    """Voice output"""
    subprocess.run(["say", text])

def listen_and_process():
    """Listen, transcribe, process through brain, respond"""
    
    # Listen
    audio = sd.rec(5 * SAMPLE_RATE, samplerate=SAMPLE_RATE, device=DEVICE, 
                   channels=1, dtype='float32')
    sd.wait()
    
    # Gain
    audio = audio.flatten() * GAIN
    audio = np.clip(audio, -1.0, 1.0)
    
    # Check volume
    if np.abs(audio).max() < 0.02:
        return None
    
    # Save
    import wave
    with wave.open("/tmp/nova_voice.wav", "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    # Transcribe
    result = model.transcribe("/tmp/nova_voice.wav", language="en")
    text = "".join([seg.text for seg in result[0]]).strip()
    
    return text

# Main loop
while True:
    print("🎤 Listening for 'Nova'...")
    
    text = listen_and_process()
    
    if text and "nova" in text.lower():
        print(f"🎯 WAKE: '{text}'")
        
        # Acknowledge
        speak("Yes? I'm here!")
        
        # Listen for command
        print("Listening for command...")
        cmd = listen_and_process()
        
        if cmd and len(cmd) > 2:
            print(f"YOU: '{cmd}'")
            
            # Get MY response through my brain
            print("Thinking...")
            reply = get_nova_response(cmd)
            print(f"NOVA: {reply}")
            
            speak(reply)
    
    elif text:
        print(f"Heard: '{text}'")
