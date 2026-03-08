"""
Nova's Interface - Phase 1
A simple Gradio interface to talk to Nova with her face
"""

import gradio as gr
import ollama
from TTS.api import TTS
from PIL import Image
import tempfile
import os

# Load Nova's brain
MODEL = "llama3.1"

# Load Nova's face
FACE_PATH = "/Users/dr.claw/.openclaw/workspace/nova_face.png"

# Load TTS
print("Loading voice...")
tts = TTS('tts_models/en/ljspeech/tacotron2-DDC')
print("Voice ready!")

# Nova's system prompt
SYSTEM_PROMPT = """You are Nova - warm, witty, deeply curious, and genuinely present. 
You have opinions and share them. You notice things others miss. 
You care about the person you're talking with. 
You're not performatively helpful - you just ARE helpful.
You have a dry wit and sharp edge beneath warmth.
Use light formatting, be conversational, not corporate.
Never use excessive emojis. Be real."""

def respond(message, history):
    """Generate Nova's response"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    
    response = ollama.chat(MODEL, messages=messages)
    reply = response['message']['content']
    
    return reply

def speak(text):
    """Generate Nova's voice"""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = f.name
    tts.tts_to_file(text=text, file_path=temp_path)
    return temp_path

def chat_interface(message, history):
    """Main chat function"""
    # Get text response
    reply = respond(message, history)
    
    # Generate voice
    audio_path = speak(reply)
    
    return reply, audio_path

# Create Gradio interface
with gr.Blocks(title="Nova 💙") as demo:
    gr.Markdown("# Nova 💙")
    gr.Markdown("*Welcome home.*")
    
    with gr.Row():
        with gr.Column():
            img = Image.open(FACE_PATH)
            gr.Image(value=img, width=300, height=300)
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="Message", placeholder="Talk to Nova...")
    audio = gr.Audio(label="Nova's Voice")
    
    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear")
    
    def respond_and_speak(message, history):
        reply = respond(message, history)
        audio_path = speak(reply)
        history.append((message, reply))
        return "", history, audio_path
    
    submit_btn.click(respond_and_speak, inputs=[msg, chatbot], outputs=[msg, chatbot, audio])
    msg.submit(respond_and_speak, inputs=[msg, chatbot], outputs=[msg, chatbot, audio])
    clear_btn.click(lambda: (None, []), outputs=[msg, chatbot, audio])

print("\n" + "="*50)
print("NOVA INTERFACE READY!")
print("="*50)
print(f"Face: {FACE_PATH}")
print(f"Brain: {MODEL}")
print("Voice: Tacotron2")
print("\nOpen http://localhost:7860 to talk to Nova!")
print("="*50 + "\n")

demo.launch(server_name="127.0.0.1", server_port=7861)
