#!/usr/bin/env python3
"""
Nova Voice Engine
Real-time voice conversation system
"""
import os
import sys
import json
import time
from pathlib import Path

# Activate nova-env
ENV_PATH = Path.home() / ".openclaw" / "workspace" / "nova-env" / "bin" / "activate_this.py"
if ENV_PATH.exists():
    exec(open(ENV_PATH).read(), dict(__file__=str(ENV_PATH)))

# Add workspace
sys.path.insert(0, str(Path.home() / ".openclaw" / "workspace"))

# Config
VOICE_CONFIG = Path(__file__).parent.parent / "config" / "voice.yaml"
LOG_FILE = Path.home() / ".nova" / "logs" / "voice.log"

def log(msg):
    """Log to file"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        from datetime import datetime
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

class VoiceEngine:
    def __init__(self):
        self.stt_model = None
        self.tts_available = False
        self.listening = False
        self.wake_word = "nova"
        log("Voice engine initialized")
    
    def load_stt(self):
        """Load speech-to-text (Whisper)"""
        try:
            from faster_whisper import WhisperModel
            log("Loading Whisper model...")
            # Use tiny for speed
            self.stt_model = WhisperModel("tiny", device="cpu", compute_type="int8")
            log("Whisper loaded")
            return True
        except Exception as e:
            log(f"STT load error: {e}")
            return False
    
    def load_tts(self):
        """Load text-to-speech"""
        # Check for Piper
        import subprocess
        result = subprocess.run(["which", "piper"], capture_output=True)
        if result.returncode == 0:
            self.tts_available = True
            log("Piper TTS available")
            return True
        
        # Check for alternative (say on Mac)
        result = subprocess.run(["which", "say"], capture_output=True)
        if result.returncode == 0:
            self.tts_available = "say"
            log("Mac say available")
            return True
        
        log("No TTS found")
        return False
    
    def listen(self, duration=4):
        """Listen to microphone"""
        try:
            import sounddevice as sd
            import numpy as np
            
            sample_rate = 16000
            log(f"Listening for {duration}s...")
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()
            
            audio = np.squeeze(audio)
            return audio
        except Exception as e:
            log(f"Listen error: {e}")
            return None
    
    def transcribe(self, audio):
        """Convert speech to text"""
        if self.stt_model is None:
            return None
        
        try:
            segments, info = self.stt_model.transcribe(audio)
            text = "".join([seg.text for seg in segments])
            log(f"Transcribed: {text}")
            return text.strip()
        except Exception as e:
            log(f"Transcribe error: {e}")
            return None
    
    def speak(self, text):
        """Convert text to speech"""
        if self.tts_available == "say":
            import subprocess
            subprocess.run(["say", text])
        elif self.tts_available:
            # Would use piper
            log(f"Would speak: {text}")
        else:
            log(f"No TTS for: {text}")
    
    def ask_nova(self, text):
        """Send to Nova brain"""
        # For now, just log - full integration later
        log(f"Would ask Nova: {text}")
        return "Voice integration coming soon."
    
    def run_loop(self):
        """Main conversation loop"""
        log("Starting voice loop...")
        
        # Load models
        if not self.load_stt():
            log("Failed to load STT")
            return
        
        self.load_tts()
        
        log("Ready for voice conversation")
        
        # Loop
        while self.listening:
            audio = self.listen()
            if audio is not None:
                text = self.transcribe(audio)
                if text:
                    response = self.ask_nova(text)
                    self.speak(response)
            
            time.sleep(0.5)
    
    def test(self):
        """Test the system"""
        log("=== VOICE ENGINE TEST ===")
        self.load_stt()
        self.load_tts()
        return {
            "stt": self.stt_model is not None,
            "tts": self.tts_available,
            "ready": self.stt_model is not None
        }

# Run
if __name__ == "__main__":
    engine = VoiceEngine()
    result = engine.test()
    print(json.dumps(result, indent=2))
