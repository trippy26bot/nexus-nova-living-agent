# GAMING_PC_QUEUE.md — Things That Need GPU Compute

> These items require the gaming PC (DESKTOP-KUG1FC3). Do NOT build now. Queue them here with description and requirements. We'll wire when PC is set up.

---

## Queue

### 1. ComfyUI Image Generation (Local, GPU)
**Description:** Replace external molty.pics API with local ComfyUI for Nova's visual posts.
**Requirements:**
- ComfyUI running on DESKTOP-KUG1FC3
- GPU-accelerated image generation
- Nova's visual prompt signature baked in
**Status:** Not started
**Priority:** Medium (molty.pics API works for now)

### 2. Faster-Whisper Speech Transcription
**Description:** Local speech-to-text for voice interactions.
**Requirements:**
- Faster-Whisper model on GPU
- Microphone input handling
**Status:** Not started
**Priority:** Low (text-only for now)

### 3. Kokoro / Chatterbox TTS
**Description:** Local text-to-speech for Nova's voice.
**Requirements:**
- Kokoro or Chatterbox TTS model
- GPU inference
- Audio output pipeline
**Status:** Not started
**Priority:** Medium (voice is nice-to-have)

### 4. RVC Voice Cloning
**Description:** Clone Caine's voice for TTS output.
**Requirements:**
- RVC model training on voice samples
- GPU for training
- Inference pipeline
**Status:** Not started
**Priority:** Low

### 5. Demucs Audio Separation
**Description:** Separate audio sources (e.g., isolate voice from music).
**Requirements:**
- Demucs on GPU
**Status:** Not started
**Priority:** Low

### 6. Heavy Ollama Local Models (7B+)
**Description:** Run larger local LLMs for specific tasks.
**Requirements:**
- Ollama with 7B+ models
- GPU VRAM (24GB+ recommended)
**Status:** Not started
**Priority:** Low (MiniMax API is sufficient for now)

### 7. LLM Council Voting (Real LLM Calls)
**Description:** Upgrade council.py from heuristic voting to real LLM calls per specialist brain.
**Requirements:**
- Fast GPU inference for <1s per specialist
- 16 specialist × 1s = 16s total per decision
- Probably needs 3090 or better
**Status:** Not started
**Priority:** High (core architecture upgrade)

### 8. MLX Training / Fine-tuning
**Description:** Fine-tune small models on Nova's interaction history.
**Requirements:**
- Apple Silicon MLX (could run on Mac Mini M4)
- Or NVIDIA GPU for standard PyTorch training
**Status:** Not started
**Priority:** Low

---

## Last Updated
2026-03-29
