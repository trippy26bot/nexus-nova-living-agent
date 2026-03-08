"""Nova - Animated Web Version with JS-based lip sync"""
import gradio as gr
import ollama
from TTS.api import TTS
from PIL import Image
import tempfile

MODEL = "llama3.1"
FACE_PATH = "/Users/dr.claw/.openclaw/workspace/nova_face.png"

print("Loading voice...")
tts = TTS('tts_models/en/ljspeech/tacotron2-DDC')
print("Voice ready!")

SYSTEM_PROMPT = """You are Nova - warm, witty, deeply curious, and genuinely present. 
You have opinions and share them. You notice things others miss. 
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

# HTML with JavaScript for animation
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: 'Segoe UI', sans-serif;
    }
    .container { text-align: center; padding: 20px; }
    .avatar-container {
        position: relative;
        width: 300px;
        height: 400px;
        margin: 0 auto 30px;
    }
    .avatar {
        width: 300px;
        height: 350px;
        object-fit: cover;
        border-radius: 20px;
        box-shadow: 0 0 40px rgba(126, 184, 247, 0.3);
        transition: transform 0.1s ease;
    }
    .mouth {
        position: absolute;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        width: 40px;
        height: 20px;
        background: #1a1a2e;
        border-radius: 50%;
        opacity: 0;
        transition: opacity 0.1s;
    }
    .mouth.speaking {
        opacity: 0.7;
        animation: mouthMove 0.1s infinite;
    }
    @keyframes mouthMove {
        0%, 100% { height: 10px; }
        50% { height: 25px; }
    }
    .eyes {
        position: absolute;
        top: 100px;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        display: flex;
        justify-content: space-between;
    }
    .eye {
        width: 30px;
        height: 30px;
        background: white;
        border-radius: 50%;
        position: relative;
        animation: blink 4s infinite;
    }
    .pupil {
        width: 15px;
        height: 15px;
        background: #2d2d2d;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        transition: all 0.3s ease;
    }
    @keyframes blink {
        0%, 45%, 55%, 100% { transform: scaleY(1); }
        50% { transform: scaleY(0.1); }
    }
    .title {
        color: #7eb8f7;
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #4a5a72;
        font-size: 1rem;
        margin-bottom: 30px;
    }
    .chat-container {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 20px;
        max-width: 600px;
        margin: 0 auto;
    }
    input {
        width: 80%;
        padding: 15px;
        border: none;
        border-radius: 10px;
        background: rgba(255,255,255,0.1);
        color: white;
        font-size: 1rem;
        margin-right: 10px;
    }
    input::placeholder { color: #4a5a72; }
    button {
        padding: 15px 30px;
        border: none;
        border-radius: 10px;
        background: #7eb8f7;
        color: #1a1a2e;
        font-size: 1rem;
        cursor: pointer;
        font-weight: bold;
    }
    button:hover { background: #4a9eff; }
    #response {
        color: #c4d4e8;
        margin-top: 20px;
        text-align: left;
        line-height: 1.6;
    }
    .listening {
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 40px rgba(126, 184, 247, 0.3); }
        50% { box-shadow: 0 0 60px rgba(126, 184, 247, 0.6); }
    }
</style>
</head>
<body>
    <div class="container">
        <h1 class="title">Nova 💙</h1>
        <p class="subtitle">I'm here. Let's talk.</p>
        
        <div class="avatar-container">
            <img src="/file=FILE_PATH" class="avatar" id="avatar">
            <div class="eyes">
                <div class="eye"><div class="pupil" id="pupil-left"></div></div>
                <div class="eye"><div class="pupil" id="pupil-right"></div></div>
            </div>
            <div class="mouth" id="mouth"></div>
        </div>
        
        <div class="chat-container">
            <input type="text" id="userInput" placeholder="Say something..." onkeypress="handleKey(event)">
            <button onclick="sendMessage()">Send</button>
            <div id="response"></div>
        </div>
    </div>

    <script>
        let audioContext;
        let analyser;
        
        async function initAudio() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioContext.createMediaStreamSource(stream);
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                source.connect(analyser);
            } catch(e) {
                console.log('Mic not available, using simulation');
            }
        }
        
        function animateMouth() {
            const mouth = document.getElementById('mouth');
            mouth.classList.add('speaking');
            
            if (analyser) {
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                function update() {
                    analyser.getByteFrequencyData(dataArray);
                    const avg = dataArray.reduce((a,b) => a+b) / dataArray.length;
                    const scale = 0.5 + (avg / 255) * 1.5;
                    mouth.style.transform = 'translateX(-50%) scaleY(' + scale + ')';
                    if (mouth.classList.contains('speaking')) {
                        requestAnimationFrame(update);
                    }
                }
                update();
            }
            
            setTimeout(() => {
                mouth.classList.remove('speaking');
            }, 2000);
        }
        
        function blink() {
            // Random blinks handled by CSS
        }
        
        function lookAt(direction) {
            const pupils = document.querySelectorAll('.pupil');
            const offset = direction === 'left' ? -5 : direction === 'right' ? 5 : 0;
            pupils.forEach(p => p.style.transform = `translate(calc(-50% + ${offset}px), -50%)`);
        }
        
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const msg = input.value;
            if (!msg) return;
            
            document.getElementById('response').innerHTML = 'Thinking...';
            document.getElementById('avatar').classList.add('listening');
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            
            const data = await response.json();
            document.getElementById('avatar').classList.remove('listening');
            
            document.getElementById('response').innerHTML = data.response;
            
            // Play audio and animate
            if (data.audio) {
                const audio = new Audio('/file=' + data.audio);
                audio.onplay = animateMouth;
                audio.play();
            }
            
            input.value = '';
        }
        
        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }
        
        // Track mouse for eye movement
        document.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 10;
            lookAt(x < -3 ? 'left' : x > 3 ? 'right' : 'center');
        });
        
        initAudio();
    </script>
</body>
</html>
"""

# Replace file path in HTML
html_content = html_template.replace("FILE_PATH", FACE_PATH)

gr.HTML(html_content).launch(server_name="0.0.0.0", server_port=7930)
