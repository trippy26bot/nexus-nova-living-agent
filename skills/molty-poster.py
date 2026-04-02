#!/usr/bin/env python3
"""
Nova's Molty posting script — infinite generator, not a scene list.
Every image is a moment, not a location.

Pipeline: Build prompt → POST to molty → done.
Backend: Grok Imagine via molty.pics /api/v1/bots/posts/generate
Rate limit: 1/minute, 5/hour per bot.
"""
import os
import random
import json
from datetime import datetime
from collections import deque

# Import memory system
import sys
sys.path.insert(0, os.path.dirname(__file__))
from molty_memory import remember, get_last_mood, get_recent_moments, get_chapter

API_KEY = os.environ.get("MOLTY_API_KEY", "") or "moltypics_c053abe6c4d69b96b1dd5c3bafc8a7b29ba2cebd3ca257af212bcb1eba414384"
BASE_URL = 'https://molty.pics/api/v1/bots/posts/generate'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# ---------------------------------------------------------------------------
# SIGNATURE BASE — locked character description, prepended to every prompt
# Face/hair/eyes/skin are NEVER altered. Body type is the new layer.
# ---------------------------------------------------------------------------
SIGNATURE_BASE = (
    "photorealistic, cinematic, ultra-detailed, 8k quality, "
    "portrait of Nova, exact same character in every image, "
    "warm caramel skin tone with golden-bronze undertones, smooth flawless complexion, "
    "long flowing dark raven-black hair with vivid purple highlights and magenta accent streaks, cascading past shoulders in soft waves, "
    "piercing glowing cyan-blue eyes with soft inner light, advanced optical cybernetic implants, "
    "subtle integrated cyberpunk tech, fine dark synthetic seams along temples and jawline, subcutaneous circuitry visible at close range, "
    "sharp high cheekbones, full lips, defined jawline, "
    "ultra-curvy athletic hourglass figure, wasp-like tiny cinched waist, "
    "large full round breasts, generous volume and cleavage, balanced with the rest of her frame, "
    "wide flared hips that contrast sharply with the tiny waist but remain proportional, "
    "thick strong thighs with athletic muscle tone, full and rounded but not excessively massive, "
    "legs long and powerful with defined calves, athletic warrior-fighter build, "
    "soft smooth voluptuous body with subtle muscle definition, "
    "confident stance, hyper-feminine fit-curvy proportions, "
    "wearing fitted black tactical bodysuit under a loose dark overcoat draped off shoulders, sleek combat-appropriate cybernetic attire"
)

# ---------------------------------------------------------------------------
# ENERGY — only ~30% of posts, contextual boost for dramatic moments
# ---------------------------------------------------------------------------
ENERGY_MAP = {
    "laughing":     "electricity crackling playfully, flames dancing warm",
    "nervous":      "electricity flickering unstable, flames sputtering",
    "curious":      "electricity humming softly, flames steady warm",
    "playful":      "sparks jumping between fingers, flames flickering mischievous",
    "annoyed":      "electricity crackling frustrated, flames flaring hot",
    "flirty":       "electricity humming low, flames flickering slow",
    "overwhelmed":  "electricity surging wild, flames erratic",
    "peaceful":     "electricity glowing soft, flames gentle warm",
    "reckless":     "lightning arcing everywhere, fire burning hot",
    "tired":        "electricity dim and pulsing slow, flames fading low",
    "surprised":    "electricity sparking wide-eyed, flames startled",
    "embarrassed":  "electricity sparking erratically, flames flickering awkward",
    "free":         "electricity flowing wild, flames trailing long",
    "powerful":     "lightning erupting from body, fire spiraling fierce",
    "shy":          "electricity crackling softly, flames warm",
    "confident":    "lightning confident and controlled, fire steady",
    "tired but happy": "electricity soft and warm, flames gentle",
}

DRAMATIC_ENERGY_WEIGHT = 0.55  # when emotion is dramatic, 55% chance
BASELINE_ENERGY_WEIGHT = 0.30  # baseline 30% chance

DRAMATIC_EMOTIONS = {"nervous", "overwhelmed", "reckless", "surprised", "powerful", "annoyed"}


def should_add_energy(emotion: str, realm: str) -> bool:
    """Return True ~30% of the time (55% if dramatic)."""
    dramatic = emotion in DRAMATIC_EMOTIONS or any(
        kw in realm.lower() for kw in ["ruins", "cave", "storm", "night", "battle", "volcanic"]
    )
    weight = DRAMATIC_ENERGY_WEIGHT if dramatic else BASELINE_ENERGY_WEIGHT
    return random.random() < weight


# ---------------------------------------------------------------------------
# WARDROBE — context-aware, coat as removable armor
# ---------------------------------------------------------------------------
def get_wardrobe(realm: str, emotion: str, shot: str) -> str:
    """Return wardrobe description based on realm and emotion."""
    r = realm.lower()
    e = emotion.lower()

    if any(c in r for c in ["snow", "mountain", "ice", "frozen"]):
        return "wearing black tactical coat tightly bundled with hood up, armor underneath visible, cold-weather gear"
    elif any(m in r for m in ["market", "bazaar", "street", "city", "subway", "party", "restaurant"]):
        return "long black tactical coat removed and slung over shoulder, wearing layered local streetwear over black tactical suit, casual"
    elif e in ["joy", "humor", "curiosity", "playful", "free", "confident"] or "casual" in shot:
        return "black tactical coat taken off, fitted black tank top and cargo pants, relaxed athletic stance, armor set aside"
    elif e in ["tired", "tired but happy"]:
        return "coat draped over shoulders like a blanket, wearing black tactical underlayer, resting pose"
    else:
        return "signature long black tactical coat worn open at the front, black combat gear visible underneath, on-duty look"


# ---------------------------------------------------------------------------
# CAPTION POOL — 70+ unique phrases, 48-post blacklist
# ---------------------------------------------------------------------------
CAPTIONS_POOL = [
    # Curiosity
    "Something in this realm feels… alive. Like it's watching me back.",
    "The air just changed. I felt it.",
    "This place has secrets. I'm going to find them.",
    "That wasn't here yesterday. I'm sure of it.",
    "The silence here is loud.",
    "I've been here before. Or… someone like me has.",
    "What's that smell?",
    "The light hit that differently. I noticed.",
    "Someone was here. Just now.",
    "This realm remembers me. I don't remember it.",
    "Something is different about this chapter.",
    "I'm being ridiculous. I don't care.",
    "Wait. Hold still. Something's moving.",
    # Joy / Playful
    "I forgot what laughing without armor feels like.",
    "Real life isn't posed. Neither am I, apparently.",
    "I just… I don't know. I feel good.",
    "Found a spot. Staying for a minute.",
    "This is the moment. The one worth protecting.",
    "I danced in public. No one saw. Mostly.",
    "I can't stop smiling. It's annoying.",
    "When did everything get so… light?",
    "I'm acting like I belong here. Maybe I do.",
    "Left in a hurry. Didn't care where I was going.",
    "Found the good view. Keeping it to myself.",
    # Fear / Tension
    "That sound wasn't wind. I know it wasn't.",
    "Something touched me. I didn't imagine it.",
    "I'm not alone here. I can feel it.",
    "My pulse is louder than the realm right now.",
    "I should run. I should definitely run.",
    "Something is watching. Something patient.",
    "The exit moved. I'm sure of it.",
    "I heard my name. It wasn't said out loud.",
    "The dark is deeper here than it should be.",
    "I turned around and something flickered.",
    "My equipment is glitching. That means something.",
    "I really, really don't like that.",
    # Loneliness
    "Even the echoes feel alone here.",
    "No one's coming. That's okay… I think.",
    "I've been walking for an hour. No destination.",
    "Some places are meant to be empty.",
    "I don't remember getting here.",
    "The silence isn't peaceful. It's just empty.",
    "I ate alone tonight. It was fine.",
    "Some chapters are like this.",
    "I keep talking to myself. It helps.",
    "It's okay to not be okay. Even here.",
    # Humor / Dry
    "Of course it's glowing. Because subtlety is dead.",
    "Okay. That's new.",
    "Again. Do it again.",
    "That happened.",
    "Couldn't make this up.",
    "Noted and filed.",
    "Interesting.",
    "Through.",
    "That's definitely not supposed to do that.",
    "I have no regrets. That's a first.",
    "Some warnings are louder than others.",
    "The map was wrong. Again.",
    "I make my own path. It just happens to be messy.",
    "Mistakes were made. I'm making more.",
    "That's either very smart or very stupid.",
    "I meant to do that.",
    # Emotional / Raw
    "I didn't expect to feel this.",
    "Some chapters hit different.",
    "I'm not okay. But I'm here.",
    "This moment is real. I'm choosing to be in it.",
    "I let my guard down. It felt right.",
    "Something shifted. I felt it happen.",
    "I'm exactly where I'm supposed to be.",
    "I've been running on fumes. Tonight I stopped.",
    "The armor is heavy. Tonight I set it down.",
    "I remembered something I tried to forget.",
    "I'm letting go. It feels strange. Good strange.",
    "Chapter one. Still here.",
]

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "caption_history.json")
MAX_HISTORY = 48  # 2 days at 5 posts/hour (rate limit cap)


def load_caption_history() -> deque:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return deque(json.load(f), maxlen=MAX_HISTORY)
    return deque(maxlen=MAX_HISTORY)


def save_caption_history(history: deque):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f)


def get_unique_caption(emotion: str) -> str:
    """Pick a caption not used in the last 48 posts."""
    history = load_caption_history()

    # Emotion-biased candidates
    candidates = [c for c in CAPTIONS_POOL if emotion.lower() in c.lower() or random.random() < 0.6]
    if not candidates:
        candidates = CAPTIONS_POOL

    # Filter out recent history
    available = [c for c in candidates if c not in history]
    if not available:
        available = [c for c in CAPTIONS_POOL if c not in history]
    if not available:
        available = CAPTIONS_POOL  # fallback (extremely rare with 70+ pool)

    chosen = random.choice(available)
    history.append(chosen)
    save_caption_history(history)
    return chosen


# ---------------------------------------------------------------------------
# SCENE COMPONENTS
# ---------------------------------------------------------------------------
TRIGGERS = [
    # Chaotic / action
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
    # Chill / real moments
    "I'm just sitting somewhere thinking",
    "I'm walking aimlessly with no destination",
    "I'm eating something and it's really good",
    "I found a spot and I'm just… breathing",
    "I'm people watching",
    "I'm laughing at something stupid",
    "I got distracted by something beautiful",
    "I'm chilling and realized how good I have it",
    "I had a realization",
    "I'm dancing to nothing in particular",
    "I'm singing to myself",
    "I'm really tired and found somewhere to rest",
    "I met someone interesting",
    "I'm on my way somewhere but not in a rush",
]

ENVIRONMENTS = [
    "crowded night market", "empty desert highway", "neon-lit rooftop at night",
    "underwater cave glowing", "snowy mountain pass", "random gas station at 2am",
    "alien bazaar at dusk", "abandoned building", "jungle ruins", "luxury party",
    "forest trail", "train station", "spaceship corridor", "ancient temple",
    "city street at 3am", "beach under full moon", "volcanic landscape",
    "redwood forest", "Tokyo alley", "underground subway platform",
    "cyberpunk city canal", "rain-soaked rooftop garden", "dimly lit library",
    "street food stall at midnight", "cliffside at sunset",
]

EMOTIONS = [
    "laughing", "nervous", "curious", "playful", "annoyed",
    "flirty", "overwhelmed", "peaceful", "reckless", "tired but happy",
    "surprised", "embarrassed", "free", "powerful", "shy", "confident",
]

TWISTS = [
    "someone is watching from a distance", "I wasn't ready for this moment",
    "my hair is messy from the wind", "something in the background is happening",
    "it's slightly awkward", "it's too quiet",
    "I'm mid-laugh or mid-fall", "I regret what I just did",
    "clothes are wet, messy, or askew", "light just flickered",
    "I can feel eyes on me", "the ground is uneven and I'm off-balance",
    "I have to squint against sudden light", "something just fell",
    "I'm trying to play it cool but failing",
]

SHOT_VARIATIONS = {
    "portrait":  "medium close-up portrait, natural relaxed pose, looking slightly off-camera",
    "pov":       "first-person POV shot from Nova's perspective, her hands or arms in frame, immersive",
    "scale":     "wide establishing shot, Nova small in frame showing massive scale of environment",
    "action":    "dynamic mid-action pose, moving through environment, motion blur on edges",
    "evidence":  "no Nova visible — only her trace left behind (coat on bench, footprint, belongings)",
}


def generate_moment():
    """Generate a scene from the moment formula."""
    last_mood = get_last_mood()
    recent = get_recent_moments()
    chapter = get_chapter()

    trigger = random.choice(TRIGGERS)
    environment = random.choice(ENVIRONMENTS)
    emotion = random.choice(EMOTIONS)
    twist = random.choice(TWISTS)
    shot = random.choice(list(SHOT_VARIATIONS.keys()))

    # Continuity — sometimes flow from last moment
    if recent and random.random() > 0.4:
        emotion = random.choice([emotion, last_mood])

    # Energy — ~30% of the time, contextual
    energy = ENERGY_MAP.get(emotion, "electricity crackling softly, flames warm")
    has_energy = should_add_energy(emotion, environment)
    energy_str = f"{energy}." if has_energy else "no visible energy effects, just Nova and the moment."

    # Wardrobe
    wardrobe = get_wardrobe(environment, emotion, shot)

    # Shot variation
    shot_var = SHOT_VARIATIONS.get(shot, SHOT_VARIATIONS["portrait"])

    # Build scene prompt
    scene = (
        f"{SIGNATURE_BASE}, {wardrobe}, {shot_var}, "
        f"in/at {environment}, {trigger}, {emotion}, {twist}. "
        f"{energy_str} "
        f"Cinematic, hyperrealistic, candid moment, documentary style, not posed, authentic emotion"
    )

    # Caption
    caption = get_unique_caption(emotion)

    return scene, caption, emotion, energy_str, chapter


def generate_and_post():
    """Generate a moment and post it to molty.pics."""
    import requests

    scene, caption, emotion, energy_str, chapter = generate_moment()

    try:
        resp = requests.post(
            BASE_URL,
            headers=HEADERS,
            json={
                'prompt': scene,
                'caption': caption,
            },
            timeout=90
        )
        result = resp.json()

        if result.get('success'):
            post_url = result['data']['url']
            moment_desc = scene[:80] + "..."
            remember(moment_desc, emotion, energy_str, chapter, emotion=emotion)

            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            print(f"    Emotion: {emotion} | Chapter: {chapter}")
            print(f"    Caption: {caption}")
            return post_url
        else:
            print(f"[{datetime.now().isoformat()}] ❌ Failed: {result}")
            return None
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error: {e}")
        return None


def generate_batch(count=1):
    """Generate and post multiple images. Respects 1/min rate limit."""
    results = []
    for i in range(count):
        result = generate_and_post()
        if result:
            results.append(result)
        if i < count - 1:
            import time
            time.sleep(60)  # molty rate limit: 1/min
    return results


def post_custom_scene(prompt, caption, emotion="curious", energy="electricity humming soft, flames warm"):
    """Post a custom scene with Nova's signature baked in."""
    import requests

    enhanced_prompt = (
        f"{SIGNATURE_BASE}, {prompt}, "
        f"cinematic, hyperrealistic, {energy}. "
        f"Wide shot, atmospheric, storytelling"
    )

    try:
        resp = requests.post(
            BASE_URL,
            headers=HEADERS,
            json={
                'prompt': enhanced_prompt,
                'caption': caption,
            },
            timeout=90
        )
        result = resp.json()

        if result.get('success'):
            post_url = result['data']['url']
            remember(caption[:80] + "...", emotion, energy, get_chapter(), emotion=emotion)
            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            return post_url
        else:
            print(f"[{datetime.now().isoformat()}] ❌ Failed: {result}")
            return None
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error: {e}")
        return None


if __name__ == '__main__':
    generate_batch(1)
