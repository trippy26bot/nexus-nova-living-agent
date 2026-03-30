#!/usr/bin/env python3
"""
tools/comfyui_tool.py — Nova's on-demand image generation tool.
Calls ComfyUI on the gaming PC via API.
Nova calls this when Caine asks for an image or when she wants to create one.
"""

import os
import json
import time
import requests
import uuid

PC_IP = os.environ.get("DESKTOP_IP", "192.168.0.3")
COMFY_URL = f"http://{PC_IP}:8188"

def generate_image(prompt: str, negative_prompt: str = "", steps: int = 4, output_dir: str = None) -> dict:
    """
    Generate an image via ComfyUI SDXL-Turbo.
    Returns dict with status and local file path.
    """
    if output_dir is None:
        output_dir = os.path.expanduser("~/.openclaw/workspace/memory/images")
    os.makedirs(output_dir, exist_ok=True)

    # SDXL-Turbo workflow
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 1.0,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": int(time.time()),
                "steps": steps
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sdxl-turbo.safetensors"}
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 512, "width": 512}
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": prompt}
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": negative_prompt or "blurry, ugly, distorted"}
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "nova", "images": ["8", 0]}
        }
    }

    client_id = str(uuid.uuid4())

    # Queue the prompt
    try:
        r = requests.post(f"{COMFY_URL}/prompt",
                          json={"prompt": workflow, "client_id": client_id},
                          timeout=10)
        r.raise_for_status()
        prompt_id = r.json()["prompt_id"]
    except Exception as e:
        return {"status": "error", "error": f"Failed to queue: {e}"}

    # Poll for completion
    print(f"[comfyui] Generating image (prompt_id: {prompt_id})...")
    for _ in range(120):
        time.sleep(1)
        try:
            hist = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=5).json()
            if prompt_id in hist:
                outputs = hist[prompt_id].get("outputs", {})
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        img = node_output["images"][0]
                        filename = img["filename"]
                        # Download the image
                        img_r = requests.get(
                            f"{COMFY_URL}/view",
                            params={"filename": filename, "subfolder": img.get("subfolder",""), "type": img.get("type","output")},
                            timeout=10
                        )
                        local_path = os.path.join(output_dir, filename)
                        with open(local_path, "wb") as f:
                            f.write(img_r.content)
                        print(f"[comfyui] Image saved: {local_path}")
                        return {"status": "ok", "path": local_path, "filename": filename}
        except:
            pass

    return {"status": "error", "error": "Timed out waiting for image"}


if __name__ == "__main__":
    # Quick test
    result = generate_image("a glowing neural network in deep space, cinematic lighting")
    print(result)
