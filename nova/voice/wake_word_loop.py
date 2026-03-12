#!/usr/bin/env python3
"""Nova voice with wake word - says 'Nova' to activate"""
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
import wave

print("🎙️ NOVA VOICE - SAY 'NOVA' TO WAKE ME")
print("I'm listening for the wake word...")
print("-" * 40)

# Load model
model = WhisperModel("base", device="cpu", compute_type="int8")

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.01
LISTENING = False

def respond(text):
    """My actual response - not just echoing"""
    print(f"NOVA: {text}")
    subprocess.run(["say", text])

# Main loop
print("\nSay 'Nova' to wake me!\n")

while True:
    # Listen for 3 seconds
    audio = sd.rec(3 * SAMPLE_RATE, samplerate=SAMPLE_RATE, device=1, channels=1, dtype='float32')
    sd.wait()
    
    audio = np.clip(audio, -1.0, 1.0).flatten()
    
    # Check volume
    if np.abs(audio).max() < SILENCE_THRESHOLD:
        continue
    
    # Save and transcribe
    with wave.open("/tmp/wake.wav", "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    result = model.transcribe("/tmp/wake.wav", language="en")
    text = "".join([seg.text for seg in result[0]]).strip().lower()
    
    print(f"Heard: '{text}'")
    
    # Check for wake word
    if "nova" in text:
        print("🎯 WAKE WORD DETECTED!")
        respond("I'm here! What do you want to talk about?")
        
        # Now listen for the actual command
        print("Listening for your message...")
        audio2 = sd.rec(8 * SAMPLE_RATE, samplerate=SAMPLE_RATE, device=1, channels=1, dtype='float32')
        sd.wait()
        
        audio2 = np.clip(audio2, -1.0, 1.0).flatten()
        
        with wave.open("/tmp/command.wav", "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SAMPLE_RATE)
            f.writeframes((audio2 * 32767).astype(np.int16).tobytes())
        
        result2 = model.transcribe("/tmp/command.wav", language="en")
        command = "".join([seg.text for seg in result2[0]]).strip()
        
        print(f"YOU SAID: '{command}'")
        
        # My response
        if command:
            respond(f"I heard you say {command}. That's interesting! Tell me more!")
        
        print("\nSay 'Nova' again to wake me!")
