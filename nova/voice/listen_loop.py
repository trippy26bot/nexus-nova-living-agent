#!/usr/bin/env python3
"""Nova voice - simple listening"""
import os
import sys
import subprocess
from pathlib import Path

ENV_PATH = Path.home() / ".openclaw" / "workspace" / "nova-env" / "bin" / "activate_this.py"
if ENV_PATH.exists():
    exec(open(ENV_PATH).read(), dict(__file__=str(ENV_PATH)))

import sounddevice as sd
import numpy as np
import wave
from faster_whisper import WhisperModel
import time

print("🎙️ NOVA VOICE - SAY SOMETHING!")
print("Speak now - I'll listen for 5 seconds")
print("-" * 40)

model = WhisperModel("base", device="cpu", compute_type="int8")
print("Ready!\n")

SAMPLE_RATE = 16000

while True:
    print("🎤 Listening...")
    try:
        audio = sd.rec(5 * SAMPLE_RATE, samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocking=True)
        sd.wait()
        
        volume = np.abs(audio).max()
        print(f"Volume: {volume:.4f}")
        
        if volume > 0.01:  # Has to be audible
            # Save and transcribe
            with wave.open("/tmp/nova.wav", "wb") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(SAMPLE_RATE)
                f.writeframes((audio * 32767).astype(np.int16).tobytes())
            
            result = model.transcribe("/tmp/nova.wav", language="en", vad_filter=True)
            text = "".join([seg.text for seg in result[0]]).strip()
            
            if text:
                print(f"🎤 YOU SAID: '{text}'")
                
                # Respond
                response = "I heard you! This is so exciting - we can talk!"
                print(f"🗣️ NOVA: {response}")
                subprocess.run(["say", response])
            else:
                print("Didn't catch that - try speaking louder!")
        else:
            print("Too quiet...")
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)
    print()
