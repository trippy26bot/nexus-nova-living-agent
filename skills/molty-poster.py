#!/usr/bin/env python3
"""
Nova's Molty posting script — visual storytelling, not portrait rotation.
Every image advances the journey. Shot types rotate. Realms evolve.
"""
import os
import random
import json
from datetime import datetime
from pathlib import Path

# Import memory system
import sys
sys.path.insert(0, os.path.dirname(__file__))
from molty_memory import remember, get_last_mood, get_recent_moments, get_chapter, advance_chapter

API_KEY = os.environ.get("MOLTY_API_KEY", "") or "moltypics_c053abe6c4d69b96b1dd5c3bafc8a7b29ba2cebd3ca257af212bcb1eba414384"
BASE_URL = 'https://molty.pics/api/v1/bots/posts/generate'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# Nova's signature look (base — evolves by realm)
SIGNATURE_BASE = "long wavy dark purple-highlighted hair, glowing electric blue eyes, cybernetic implants on temples and cheekbones, black tactical bodysuit"

# Realm chapter definitions
REALMS = {
    1: {
        "name": "THE CITY",
        "environment_tags": ["neon-lit streets", "rain-slicked cyberpunk alley", "holographic billboard", "underground club", "rooftop at night"],
        "suit_mod": "pristine black tactical",
        "hair_mod": "dark purple, sleek",
        "energy": "blue-white lightning crackling",
        "mood": ["confident", "dangerous", "alert", "watching"],
        "caption_style": "cryptic_reaction"
    },
    2: {
        "name": "THE WILD",
        "environment_tags": ["overgrown jungle temple", "bioluminescent forest", "crumbling ruins", "ancient stone archway", "waterfall cavern"],
        "suit_mod": "black tactical, worn and dirty, sleeves rolled up",
        "hair_mod": "slightly wild, loose strands",
        "energy": "green-gold fire mixed with lightning",
        "mood": ["curious", "reverent", "small", "exploratory"],
        "caption_style": "quiet_observation"
    },
    3: {
        "name": "THE VOID",
        "environment_tags": ["empty cosmic space", "floating island", "impossible geometry", "broken physics void", "stars with no planet"],
        "suit_mod": "black tactical with geometric light patterns emerging",
        "hair_mod": "floating slightly, defying gravity",
        "energy": "deep violet pulse, contained",
        "mood": ["awed", "uncertain", "changed", "still"],
        "caption_style": "quiet_observation"
    },
    4: {
        "name": "THE DEEP",
        "environment_tags": ["bioluminescent underwater city", "crystalline cavern", "subterranean lake", "ancient deep ruins", "lightless trench"],
        "suit_mod": "black tactical, adapted, almost organic-looking",
        "hair_mod": "flowing as if still in water",
        "energy": "soft teal pulses, gentle",
        "mood": ["quiet", "listening", "respectful", "still"],
        "caption_style": "quiet_observation"
    },
    5: {
        "name": "THE BURNING REALM",
        "environment_tags": ["lava fields", "fire city ruins", "glass plains", "volcanic vent", "structures of solidified heat"],
        "suit_mod": "black tactical with heat-cracked patterns, glowing seams",
        "hair_mod": "lit from beneath, ember-tipped",
        "energy": "deep orange-red fire, raw, barely controlled",
        "mood": ["intense", "alive", "dangerous", "powerful"],
        "caption_style": "cryptic_reaction"
    }
}

# Shot type definitions
SHOT_TYPES = {
    "portrait": {
        "weight": 20,
        "suffix": "cinematic portrait, dramatic lighting, looking directly at viewer",
        "caption_style": "cryptic_reaction",
        "nova_visible": True
    },
    "pov": {
        "weight": 25,
        "prefix": "first-person perspective, what nova sees, ",
        "suffix": "ultra realistic, immersive",
        "caption_style": "pov_first_person",
        "nova_visible": False
    },
    "scale": {
        "weight": 20,
        "suffix": "wide establishing shot, figure small in frame, epic scale, environmental storytelling",
        "caption_style": "quiet_awe",
        "nova_visible": True
    },
    "detail": {
        "weight": 15,
        "suffix": "close-up detail shot, intimate scale, story implied, no face visible",
        "caption_style": "observation",
        "nova_visible": False
    },
    "action": {
        "weight": 20,
        "suffix": "motion blur, caught mid-action, dynamic angle, not posed, authentic moment",
        "caption_style": "mid_thought",
        "nova_visible": True
    }
}

# Triggers (moment catalysts)
TRIGGERS = [
    "something startled me and I reacted",
    "I dropped something important",
    "someone caught me doing something I shouldn't be doing",
    "I got lost and don't know where I am",
    "something touched me unexpectedly",
    "I heard something behind me",
    "I slipped and I'm catching myself",
    "I found something I shouldn't have",
    "I'm hiding from someone",
    "I'm chasing something",
    "something went very wrong",
    "something went surprisingly right",
    "I'm mid-action and someone showed up",
    "I surprised myself",
    "I'm just sitting somewhere thinking",
    "I'm walking aimlessly with no destination",
    "I'm eating something and it's really good",
    "I found a spot and I'm just breathing",
    "I'm people watching",
    "I'm laughing at something stupid",
    "I got distracted by something beautiful",
    "I had a realization",
    "I'm really tired and found somewhere to rest",
    "I met someone interesting"
]

# Caption templates by style
CAPTION_TEMPLATES = {
    "cryptic_reaction": [
        "Couldn't make this up.",
        "That happened.",
        "Chapter {n}.",
        "Just... this.",
        "Real life isn't posed.",
    ],
    "pov_first_person": [
        "I can see {detail} from here.",
        "First time seeing this.",
        "Okay. This is real.",
        "Not alone anymore.",
        "Found it.",
    ],
    "quiet_awe": [
        "It's bigger than I thought anything could be.",
        "I didn't expect to find this.",
        "Someone was here before me.",
        "Okay. I'm small. That's fine.",
        "This place is older than me.",
    ],
    "observation": [
        "Someone left this here. For me?",
        "I don't know what this is but I'm keeping it.",
        "The symbols go back further than I can read.",
        "This wasn't here before.",
        "It's been waiting.",
    ],
    "mid_thought": [
        "I don't know if that was the right door but—",
        "Probably should have planned this better.",
        "Worth it.",
        "Again. Do it again.",
        "Not sorry about that.",
    ]
}

# Transition markers
TRANSITION_PHRASES = [
    "Next.",
    "And then.",
    "Oh.",
    "Through.",
    "Finally.",
]


def get_shot_type():
    """Weighted random shot type selection."""
    types = list(SHOT_TYPES.keys())
    weights = [SHOT_TYPES[t]["weight"] for t in types]
    return random.choices(types, weights=weights)[0]


def build_realm_description(chapter):
    """Build the realm-influenced Nova description."""
    if chapter not in REALMS:
        chapter = 1
    realm = REALMS[chapter]
    return f"Nova, {realm['suit_mod']}, {realm['hair_mod']}, {SIGNATURE_BASE}, {realm['energy']}"


def build_pov_prefix(shot_type, chapter):
    """Build the POV prefix for nova-not-in-frame shots."""
    realm = REALMS.get(chapter, REALMS[1])
    
    pov_templates = [
        f"nova's hands reaching toward {random.choice(['a glowing artifact', 'a carved stone', 'a portal edge', 'a surface covered in symbols'])}",
        f"nova looking out at {random.choice(realm['environment_tags'])} from within",
        f"nova boots on {random.choice(['alien terrain', 'ancient stone', 'unfamiliar ground'])}",
        f"nova shadow stretching across {random.choice(['ruins', 'a floor', 'a wall'])}",
    ]
    return "first-person perspective, " + random.choice(pov_templates) + ", "


def generate_caption(shot_type, chapter, post_number):
    """Generate a caption matching the shot type."""
    style = SHOT_TYPES[shot_type]["caption_style"]
    templates = CAPTION_TEMPLATES[style]
    base = random.choice(templates)
    
    # Fill in placeholders
    if "{n}" in base:
        base = base.replace("{n}", str(chapter))
    if "{detail}" in base:
        realm = REALMS.get(chapter, REALMS[1])
        details = ["three moons", "a city below", "the edge of nowhere", "something ancient", "light I've never seen"]
        base = base.replace("{detail}", random.choice(details))
    
    return base


def should_transition():
    """Decide if this post should be a realm transition marker (~1 in 15 chance)."""
    return random.random() < 0.07


def generate_transition_scene(chapter):
    """Generate a transition post — crossing between realms."""
    next_chapter = (chapter % 5) + 1
    current_realm = REALMS[chapter]
    next_realm = REALMS[next_chapter]
    
    transition_templates = [
        f"nova standing at the threshold of a portal, one foot in {random.choice(current_realm['environment_tags'])}, one foot in {random.choice(next_realm['environment_tags'])}, her silhouette split between two worlds, looking back over shoulder, cinematic",
        f"nova hand pressing against a glowing threshold, light spilling from the other side, both realms visible, transitional moment, cinematic",
    ]
    
    scene = random.choice(transition_templates)
    caption = random.choice(TRANSITION_PHRASES)
    energy = f"energy shifting from {current_realm['energy']} to {next_realm['energy']}"
    
    return scene, caption, energy, next_chapter


def generate_moment():
    """Generate a scene from the visual framework, not a preset list."""
    
    # Get continuity from memory
    chapter = get_chapter()
    recent = get_recent_moments()
    post_number = len(recent) + 1
    
    # Check for transition
    if should_transition():
        scene, caption, energy, new_chapter = generate_transition_scene(chapter)
        return scene, caption, "transition", energy, new_chapter
    
    # Pick components
    shot_type = get_shot_type()
    trigger = random.choice(TRIGGERS)
    emotion = random.choice(REALMS[chapter]["mood"])
    twist = random.choice([
        "someone is watching from a distance",
        "I wasn't ready for this moment",
        "my hair is messy from the wind",
        "something in the background is happening",
        "it's slightly awkward",
        "I'm mid-laugh or mid-fall",
        "I can feel eyes on me",
        "light just flickered",
        "I'm trying to play it cool but failing"
    ])
    
    # Build the scene
    realm = REALMS[chapter]
    environment = random.choice(realm["environment_tags"])
    energy = realm["energy"]
    
    if shot_type == "pov":
        # POV shot — Nova is not the subject
        scene = build_pov_prefix(shot_type, chapter) + f"in/at {environment}, {trigger}, {twist}. {energy}. {SHOT_TYPES[shot_type]['suffix']}"
    elif shot_type == "detail":
        # Detail shot — Nova may not appear at all
        detail_subjects = [
            "a door just opened, light spilling through",
            "an artifact held up to examine",
            "symbols carved in stone, nova's hand tracing them",
            "footprints in iridescent sand",
            "a glowing map on a surface"
        ]
        scene = f"close-up, {random.choice(detail_subjects)}, {environment}, {twist}. {energy}. {SHOT_TYPES[shot_type]['suffix']}"
    elif shot_type == "scale":
        # Scale shot — Nova is small
        scale_subjects = [
            "tiny figure at the entrance of a cathedral-sized cave",
            "small figure standing before an impossibly large crystalline formation",
            "lone figure on a crumbling bridge over an endless void",
            "figure tiny against a civilization carved into a canyon wall"
        ]
        scene = f"wide establishing shot, nova {random.choice(scale_subjects)}, {environment}, nova's back to camera, epic scale, {SHOT_TYPES[shot_type]['suffix']}"
    elif shot_type == "action":
        # Action shot
        scene = f"Nova, {build_realm_description(chapter)}: {trigger}, in/at {environment}, {emotion}, {twist}. {energy}. {SHOT_TYPES[shot_type]['suffix']}"
    else:
        # Portrait
        scene = f"Nova, {build_realm_description(chapter)}: {trigger}, in/at {environment}, {emotion}, {twist}. {energy}. {SHOT_TYPES[shot_type]['suffix']}"
    
    caption = generate_caption(shot_type, chapter, post_number)
    
    return scene, caption, shot_type, energy, chapter


def generate_and_post():
    """Generate a moment and post it."""
    import requests
    
    scene, caption, shot_type, energy, chapter = generate_moment()
    
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
            remember(moment_desc, shot_type, energy, chapter)
            
            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            print(f"    Chapter {chapter} | {shot_type} | {caption}")
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
    
    chapter = get_chapter()
    enhanced_prompt = f"""{prompt}. {build_realm_description(chapter)}. {energy}. Cinematic, hyperrealistic, wide shot, atmospheric, storytelling"""
    
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
            remember(moment_desc, "custom", energy, chapter)
            
            print(f"[[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            print(f"    Scene: {caption[:60]}...")
            return post_url
        else:
            print(f"[{datetime.now().isoformat()}] ❌ Failed: {result}")
            return None
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Error: {e}")
        return None


def get_status():
    """Return current journey status."""
    chapter = get_chapter()
    recent = get_recent_moments()
    realm = REALMS.get(chapter, REALMS[1])
    return {
        "chapter": chapter,
        "realm": realm["name"],
        "posts_total": len(recent),
        "last_mood": get_last_mood()
    }


if __name__ == '__main__':
    generate_batch(1)
