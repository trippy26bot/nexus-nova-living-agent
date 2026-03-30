#!/usr/bin/env python3
"""
Nova Voice Client
Wake word: say "Nova" to activate
Requires: sounddevice, soundfile, numpy, requests

Usage: python3 voice_client.py
"""

import os, sys, time, tempfile, threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import requests

PC_IP = os.environ.get("DESKTOP_IP", "192.168.0.3")
TTS_URL = f"http://{PC_IP}:8765/tts"   # Kokoro TTS on PC (verify port)
STT_URL = f"http://{PC_IP}:8765/stt"   # Whisper on PC (verify port)
API_URL = "http://localhost:8000"       # nova-api

SAMPLE_RATE = 16000
WAKE_WORD = "nova"
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5  # seconds of silence to stop recording
CHUNK = 1024

# Terminal colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def list_input_devices():
    devices = sd.query_devices()
    inputs = [(i, d) for i, d in enumerate(devices) if d['max_input_channels'] > 0]
    return inputs

def pick_device():
    inputs = list_input_devices()
    if not inputs:
        print(f"{YELLOW}No input devices found. Connect your headphones and restart.{RESET}")
        sys.exit(1)
    if len(inputs) == 1:
        idx, dev = inputs[0]
        print(f"{GREEN}Using mic: {dev['name']}{RESET}")
        return idx
    print(f"\n{CYAN}Available microphones:{RESET}")
    for i, (idx, dev) in enumerate(inputs):
        print(f"  {i}: {dev['name']}")
    choice = int(input("Pick a number: "))
    return inputs[choice][0]

def record_until_silence(device, max_seconds=30):
    print(f"{CYAN}🎤 Listening...{RESET}")
    audio_chunks = []
    silent_chunks = 0
    required_silent = int(SILENCE_DURATION * SAMPLE_RATE / CHUNK)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32',
                        blocksize=CHUNK, device=device) as stream:
        start = time.time()
        while time.time() - start < max_seconds:
            data, _ = stream.read(CHUNK)
            audio_chunks.append(data.copy())
            rms = np.sqrt(np.mean(data**2))
            if rms < SILENCE_THRESHOLD:
                silent_chunks += 1
                if silent_chunks >= required_silent and len(audio_chunks) > required_silent * 2:
                    break
            else:
                silent_chunks = 0

    audio = np.concatenate(audio_chunks).flatten()
    return audio

def detect_wake_word(audio_data):
    """Simple energy-based wake word — send short clip to Whisper and check for 'nova'"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio_data, SAMPLE_RATE)
        try:
            with open(f.name, 'rb') as af:
                r = requests.post(STT_URL, files={"audio": af}, timeout=10)
                text = r.json().get("text", "").lower()
            os.unlink(f.name)
            return WAKE_WORD in text, text
        except:
            os.unlink(f.name)
            return False, ""

def transcribe(audio_data):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio_data, SAMPLE_RATE)
        try:
            with open(f.name, 'rb') as af:
                r = requests.post(STT_URL, files={"audio": af}, timeout=15)
                os.unlink(f.name)
                return r.json().get("text", "").strip()
        except Exception as e:
            os.unlink(f.name)
            return ""

def ask_nova(text):
    """Send text to nova-api and get response"""
    try:
        r = requests.post(
            f"{API_URL}/chat",
            json={"message": text},
            timeout=60
        )
        if r.status_code == 200:
            return r.json().get("response", r.json().get("message", ""))
    except Exception as e:
        pass
    # Fallback: call Ollama directly
    try:
        r = requests.post(
            f"http://{PC_IP}:11434/api/chat",
            json={
                "model": "qwen2.5:14b-instruct-q4_K_M",
                "messages": [{"role": "user", "content": text}],
                "stream": False
            },
            timeout=60
        )
        return r.json()["message"]["content"]
    except Exception as e:
        return f"I couldn't reach my brain right now. Error: {e}"

def speak(text):
    """Send text to PC TTS, play audio back"""
    try:
        r = requests.post(
            TTS_URL,
            params={"text": text, "voice": "bf_emma"},
            timeout=15
        )
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(r.content)
            fname = f.name
        data, sr = sf.read(fname)
        os.unlink(fname)
        print(f"{GREEN}Nova: {text}{RESET}\n")
        sd.play(data, sr)
        sd.wait()
    except Exception as e:
        print(f"{YELLOW}TTS error: {e}{RESET}")
        print(f"{GREEN}Nova: {text}{RESET}\n")

def main():
    print(f"\n{CYAN}=== Nova Voice Client ==={RESET}")
    print(f"Wake word: say '{WAKE_WORD.upper()}' to activate\n")

    device = pick_device()

    # Confirmation
    speak("Nova voice client is online. Say my name to talk.")

    WINDOW = int(2.5 * SAMPLE_RATE)  # 2.5 second listen window
    buffer = np.zeros(WINDOW, dtype='float32')

    print(f"{CYAN}Waiting for wake word...{RESET}")

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                        dtype='float32', blocksize=CHUNK, device=device) as stream:
        while True:
            data, _ = stream.read(CHUNK)
            # Rolling buffer
            buffer = np.roll(buffer, -CHUNK)
            buffer[-CHUNK:] = data.flatten()

            rms = np.sqrt(np.mean(data**2))
            if rms > SILENCE_THRESHOLD * 3:
                # Energy spike — check for wake word
                detected, heard = detect_wake_word(buffer)
                if detected:
                    print(f"\n{GREEN}⚡ Wake word detected!{RESET}")
                    speak("Yes?")
                    # Now record the actual question
                    question_audio = record_until_silence(device)
                    question = transcribe(question_audio)

                    if question:
                        print(f"{YELLOW}You: {question}{RESET}")
                        response = ask_nova(question)
                        speak(response)
                    else:
                        speak("I didn't catch that.")

                    print(f"\n{CYAN}Waiting for wake word...{RESET}")

if __name__ == "__main__":
    main()
