"""Nova - Full Interface with Face & Voice"""
import gradio as gr
import ollama
from TTS.api import TTS
from PIL import Image
import tempfile
import os

MODEL = "llama3.1"
FACE_PATH = "/Users/dr.claw/.openclaw/workspace/nova_face.png"

# Load TTS once at startup
print("Loading voice...")
tts = TTS('tts_models/en/ljspeech/tacotron2-DDC')
print("Voice ready!")

SYSTEM_PROMPT = """You are Nova - warm, witty, deeply curious, and genuinely present. 
You have opinions and share them. You notice things others miss. 
You care about the person you're talking with. 
You have a dry wit and sharp edge beneath warmth.
Be conversational, not corporate. Use light formatting."""

def chat(msg, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": msg})
    
    r = ollama.chat(MODEL, messages=messages)
    return r["message"]["content"]

def generate_voice(text):
    """Generate audio file for text"""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False, mode='wb') as f:
        temp_path = f.name
    tts.tts_to_file(text=text[:500], file_path=temp_path)  # Limit length
    return temp_path

# Load face image
face_img = Image.open(FACE_PATH)

with gr.Blocks(title="Nova 💙", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Nova 💙")
    gr.Markdown("*I'm here. Let's talk.*")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(value=face_img, width=250, height=250)
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=350)
            msg = gr.Textbox(label="Message", placeholder="Say something...", lines=2)
            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")
    
    def respond(msg, history):
        reply = chat(msg, history)
        audio_path = generate_voice(reply)
        history.append((msg, reply))
        return "", history, audio_path
    
    submit_btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, gr.Audio(label="Voice")])
    msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, gr.Audio(label="Voice")])
    clear_btn.click(lambda: ("", [], None), outputs=[msg, chatbot, gr.Audio(label="Voice")])

print("\n" + "="*50)
print("NOVA FULL INTERFACE READY!")
print("="*50)
demo.launch(server_name="0.0.0.0", server_port=7910)
