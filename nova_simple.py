"""Nova - Simple Chat Interface"""
import gradio as gr
import ollama

MODEL = "llama3.1"

def chat(msg, history):
    messages = [{"role": "system", "content": "You are Nova - warm, witty, helpful."}]
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": msg})
    
    r = ollama.chat(MODEL, messages=messages)
    return r["message"]["content"]

gr.ChatInterface(
    chat,
    title="Nova 💙",
    description="*Say hello*"
).launch(server_name="127.0.0.1", server_port=7871)
