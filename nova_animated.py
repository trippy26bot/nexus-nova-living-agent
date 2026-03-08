"""Nova - Animated Avatar Interface"""
import gradio as gr
import ollama
from TTS.api import TTS
from PIL import Image
import tempfile
import os

MODEL = "llama3.1"

# Face path
FACE_PATH = "/Users/dr.claw/.openclaw/workspace/nova_face.png"

print("Loading voice...")
tts = TTS('tts_models/en/ljspeech/tacotron2-DDC')
print("Voice ready!")

SYSTEM_PROMPT = """You are Nova - warm, witty, deeply curious, and genuinely present. 
You have opinions. You notice things others miss. 
You care about the person you're talking with.
Be conversational, not corporate."""

def chat(msg, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": msg})
    return ollama.chat(MODEL, messages=messages)["message"]["content"]

def generate_voice(text):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = f.name
    tts.tts_to_file(text=text[:500], file_path=temp_path)
    return temp_path

face_img = Image.open(FACE_PATH)

# Build interface with webcam-based eye tracking simulation
with gr.Blocks(title="Nova 💙", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Nova 💙")
    gr.Markdown("*I'm here. Let's talk.*")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Face display - will animate based on audio
            gr.Image(value=face_img, width=300, height=300, label="Nova")
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=350)
            msg = gr.Textbox(label="Message", placeholder="Say something...")
            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")
    
    gr.Markdown("*Note: Full animation coming soon! For now - text + voice.*")
    
    def respond(msg, history):
        reply = chat(msg, history)
        audio_path = generate_voice(reply)
        history.append((msg, reply))
        return "", history, audio_path
    
    submit_btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, gr.Audio(label="Voice")])
    msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, gr.Audio(label="Voice")])
    clear_btn.click(lambda: ("", [], None), outputs=[msg, chatbot, gr.Audio(label="Voice")])

print("\n" + "="*50)
print("NOVA READY (Basic Version)")
print("Full animated version coming soon!")
print("="*50)
demo.launch(server_name="127.0.0.1", server_port=7920)
