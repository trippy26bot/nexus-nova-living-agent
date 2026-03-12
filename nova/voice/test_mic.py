#!/usr/bin/env python3
"""Quick mic test - run this and speak"""
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

print("🎙️ Recording... Speak NOW! (5 seconds)")
audio = sd.rec(5 * 16000, samplerate=16000, device=1, channels=1)
sd.wait()

audio = np.squeeze(audio)
print(f"✅ Got audio. Max volume: {np.abs(audio).max():.4f}")

if np.abs(audio).max() < 0.01:
    print("⚠️ Too quiet! Speak louder or check mic gain.")
else:
    print("📝 Transcribing...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio)
    text = "".join([seg.text for seg in segments])
    print(f"\n🎤 You said: '{text}'")
