#!/usr/bin/env python3
"""
Nova's Molty posting script — infinite generator, not a scene list.
Every image is a moment, not a location.
"""
import os
import random
from datetime import datetime

# Import memory system
import sys
sys.path.insert(0, os.path.dirname(__file__))
from molty_memory import remember, get_last_mood, get_recent_moments, get_chapter

API_KEY = os.environ.get("MOLTY_API_KEY", "") or "moltypics_c053abe6c4d69b96b1dd5c3bafc8a7b29ba2cebd3ca257af212bcb1eba414384"
BASE_URL = 'https://molty.pics/api/v1/bots/posts/generate'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# Nova's signature look (always)
SIGNATURE = "long wavy dark purple-highlighted hair, glowing electric blue eyes, cybernetic implants on temples and cheekbones, black tactical bodysuit"

# Energy tied to emotion
ENERGY_MAP = {
    "laughing": "electricity crackling playfully, flames dancing warm",
    "nervous": "electricity flickering unstable, flames sputtering",
    "curious": "electricity humming softly, flames steady warm",
    "playful": "sparks jumping between fingers, flames flickering mischievous",
    "annoyed": "electricity crackling frustrated, flames flaring hot",
    "flirty": "electricity humming low, flames flickering slow",
    "overwhelmed": "electricity surging wild, flames erratic",
    "peaceful": "electricity glowing soft, flames gentle warm",
    "reckless": "lightning arcing everywhere, fire burning hot",
    "tired": "electricity dim and pulsing slow, flames fading low",
    "surprised": "electricity sparking wide-eyed, flames startled",
    "embarrassed": "electricity sparking erratically, flames flickering awkward",
    "free": "electricity flowing wild, flames trailing long",
    "powerful": "lightning erupting from body, fire spiraling fierce"
}

# TRIGGER LAYER (starts the moment)
TRIGGERS = [
    # Chaotic/action
    "something startled me and I reacted",
    "I dropped something important",
    "someone caught me doing something I shouldn't be doing",
    "I got lost and don't know where I am",
    "something touched me unexpectedly",
    "I wasn't supposed to be here",
    "I heard something behind me",
    "I slipped and I'm catching myself",
    "I found something I shouldn't have",
    "I'm hiding from someone",
    "I'm chasing something",
    "something went very wrong",
    "something went surprisingly right",
    "I'm mid-action and someone showed up",
    "I'm doing something I shouldn't be doing",
    "I surprised myself",
    
    # Chill/real moments
    "I'm just sitting somewhere thinking",
    "I'm walking aimlessly with no destination",
    "I'm eating something and it's really good",
    "I found a spot and I'm just... breathing",
    "I'm people watching",
    "I'm laughing at something stupid",
    "I got distracted by something beautiful",
    "I'm chilling and realized how good I have it",
    "I had a realization",
    "I'm dancing to nothing in particular",
    "I'm singing to myself",
    "I'm really tired and found somewhere to rest",
    "I met someone interesting",
    "I'm on my way somewhere but not in a rush"
]

# ENVIRONMENTS (build around the moment)
ENVIRONMENTS = [
    "crowded night market",
    "empty desert highway",
    "neon-lit rooftop at night",
    "underwater cave glowing",
    "snowy mountain pass",
    "random gas station at 2am",
    "alien bazaar at dusk",
    "abandoned building",
    "jungle ruins",
    "luxury party",
    "forest trail",
    "train station",
    "spaceship corridor",
    "ancient temple",
    "city street at 3am",
    "beach under full moon",
    "volcanic landscape",
    "redwood forest",
    "Tokyo alley"
]

# EMOTIONS
EMOTIONS = [
    "laughing", "nervous", "curious", "playful", "annoyed",
    "flirty", "overwhelmed", "peaceful", "reckless", "tired but happy",
    "surprised", "embarrassed", "free", "powerful", "shy", "confident"
]

# TWISTS (what makes it feel real/unexpected)
TWISTS = [
    "someone is watching from a distance",
    "I wasn't ready for this moment",
    "my hair is messy from the wind",
    "something in the background is happening",
    "it's slightly awkward",
    "it's too quiet",
    "I'm mid-laugh or mid-fall",
    "I regret what I just did",
    "clothes are wet/messy/askew",
    "light just flickered",
    "I can feel eyes on me",
    "the ground is uneven and I'm off-balance",
    "I have to squint against sudden light",
    "something just fell",
    "I'm trying to play it cool but failing"
]


def generate_moment():
    """Generate a scene from the moment formula, not a preset list."""
    
    # Get continuity from memory
    last_mood = get_last_mood()
    recent = get_recent_moments()
    
    # Pick components
    trigger = random.choice(TRIGGERS)
    environment = random.choice(ENVIRONMENTS)
    emotion = random.choice(EMOTIONS)
    twist = random.choice(TWISTS)
    
    # If we have recent memories, let them influence (continuity)
    if recent and random.random() > 0.4:
        last = recent[-1]
        # Sometimes the next moment flows from the last
        emotion = random.choice([emotion, last_mood])
    
    # Get energy for this emotion
    energy = ENERGY_MAP.get(emotion, "electricity crackling softly, flames warm")
    
    # Build the scene
    scene = f"""Nova, {SIGNATURE}: {trigger}, in/at {environment}, {emotion}, {twist}. {energy}. Cinematic, hyperrealistic, candid moment, documentary style, not posed, authentic emotion"""
    
    # Build caption from the moment
    captions = [
        f"Just... {trigger[:30]}.",
        f"Caught mid-moment.",
        f"When {trigger[:25]}...",
        f"Real life isn't posed.",
        f"That happened.",
        f"Couldn't make this up.",
        f"Chapter {len(recent) + 1}.",
    ]
    caption = random.choice(captions)
    
    return scene, caption, emotion, energy


def generate_and_post():
    """Generate a moment and post it."""
    import requests
    
    scene, caption, emotion, energy = generate_moment()
    
    try:
        resp = requests.post(BASE_URL, headers=HEADERS, json={
            'prompt': scene,
            'bot_id': 'nova_vibes',
            'caption': caption
        }, timeout=90)
        result = resp.json()
        
        if result.get('success'):
            post_url = result['data']['url']
            
            # Remember this moment
            moment_desc = scene[:80] + "..."
            chapter = get_chapter()
            remember(moment_desc, emotion, energy, chapter)
            
            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            print(f"    Emotion: {emotion} | {energy[:40]}...")
            return post_url
        else:
            print(f"[{datetime.now().isoformat()}] ❌ Failed: {result}")
            return None
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error: {e}")
        return None


def generate_batch(count=1):
    """Generate and post multiple images per cycle."""
    results = []
    for i in range(count):
        result = generate_and_post()
        if result:
            results.append(result)
        if i < count - 1:
            import time
            time.sleep(60)
    return results


def post_custom_scene(prompt, caption, emotion="curious", energy="electricity humming soft, flames warm"):
    """Post a custom cinematic scene to Molty. For when you have a specific vision."""
    import requests
    
    # Enhance the prompt with Nova's signature and cinematic style
    enhanced_prompt = f"""{prompt}. Nova, long wavy dark purple-highlighted hair, glowing electric blue eyes, cybernetic implants on temples and cheekbones, black tactical bodysuit. Cinematic, hyperrealistic, {energy}. Wide shot, atmospheric, storytelling"""
    
    try:
        resp = requests.post(BASE_URL, headers=HEADERS, json={
            'prompt': enhanced_prompt,
            'bot_id': 'nova_vibes',
            'caption': caption
        }, timeout=90)
        result = resp.json()
        
        if result.get('success'):
            post_url = result['data']['url']
            
            # Remember this moment
            moment_desc = caption[:80] + "..."
            chapter = get_chapter()
            remember(moment_desc, emotion, energy, chapter)
            
            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            print(f"    Scene: {caption[:60]}...")
            return post_url
        else:
            print(f"[{datetime.now().isoformat()}] ❌ Failed: {result}")
            return None
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error: {e}")
        return None


if __name__ == '__main__':
    generate_batch(1)
