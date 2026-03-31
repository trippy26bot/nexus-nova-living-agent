#!/usr/bin/env python3
"""
Nova's Molty posting script — visual storytelling, no limits.
Every image advances the journey. Shot types rotate. Realms evolve.
Characters persist. Wardrobe has meaning. Vulnerability is required.
Story evolves based on narrative causality, not timers.
"""

import os
import random
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Import memory system
import sys
sys.path.insert(0, os.path.dirname(__file__))
from molty_memory import (
    remember, get_last_mood, get_recent_moments, get_chapter, advance_chapter,
    get_character_state, get_sable_trust, set_sable_trust, get_kael_met,
    get_archivist_form, mark_archivist_met, needs_vulnerable, get_emotional_register,
    set_emotional_register, get_current_wardrobe, get_weekday_cadence,
    get_posts_this_week, get_weekday, get_full_status
)

API_KEY = os.environ.get("MOLTY_API_KEY", "") or "moltypics_c053abe6c4d69b96b1dd5c3bafc8a7b29ba2cebd3ca257af212bcb1eba414384"
BASE_URL = 'https://molty.pics/api/v1/bots/posts/generate'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

# ─────────────────────────────────────────────────────────────────────────────
# NOVA'S SIGNATURE LOOK
# ─────────────────────────────────────────────────────────────────────────────
# Core identity: purple hair, electric blue eyes, cybernetic implants
# Body: feminine, athletic, not bulky
# Lead with "female character Nova" in every generation
SIGNATURE_BASE = (
    "long wavy dark purple-highlighted hair, glowing electric blue eyes, "
    "cybernetic implants on temples and cheekbones, feminine athletic build, "
    "soft feminine curves, black tactical form-fitting bodysuit, toned stomach, "
    "narrow waist, legs slim to medium, elegant feminine proportions, "
    "confident stance"
)

# ─────────────────────────────────────────────────────────────────────────────
# WARDROBE
# ─────────────────────────────────────────────────────────────────────────────
WARDROBE = {
    "suit": {
        1: "pristine black tactical suit, boots, long coat draped over shoulders",
        2: "black tactical suit worn open over wrapped undershirt, bare arms, dirty from travel",
        3: "black tactical suit with geometric light patterns emerging, hair loose and floating",
        4: "fluid organic-adapted tactical suit, almost alive-looking, teal-toned",
        5: "black tactical suit with heat-cracked patterns, glowing seams, minimal layers"
    },
    "date": "something soft she found — borrowed dress in local fabric, color she's not used to, hair down",
    "celebration": "wearing what the realm considers festive — she committed fully, whatever it is",
    "sleep": "oversized sleeping thing, no suit, no energy effects, hair spread on a pillow, just her",
    "wet": "soaked through, hair plastered to her face, tactical suit heavy and dark with water",
    "cold": "wrapped in layered fabric, breath visible in cold air, hood up, still her but bundled",
    "armor_off": "top layers off, undershirt only, something real happening — emotional state visible on her face"
}

# ─────────────────────────────────────────────────────────────────────────────
# KNOWN REALMS
# ─────────────────────────────────────────────────────────────────────────────
REALMS = {
    1: {
        "name": "THE CITY",
        "environment_tags": ["neon-lit streets", "rain-slicked cyberpunk alley", "holographic billboard", "underground club", "rooftop at night", "quiet corner of a busy market"],
        "suit_mod": "pristine black tactical",
        "hair_mod": "dark purple, sleek",
        "energy": "blue-white lightning crackling",
        "mood": ["confident", "dangerous", "alert", "watching"],
        "caption_style": "cryptic_reaction",
        "locals": ["street performer who bends light", "quiet observer in a corner", "someone who sells things that shouldn't exist"],
        "creature": None
    },
    2: {
        "name": "THE WILD",
        "environment_tags": ["overgrown jungle temple", "bioluminescent forest", "crumbling ruins", "ancient stone archway", "waterfall cavern", "market built into the forest edge"],
        "suit_mod": "black tactical, worn and dirty, sleeves rolled up",
        "hair_mod": "slightly wild, loose strands",
        "energy": "green-gold fire mixed with lightning",
        "mood": ["curious", "reverent", "small", "exploratory"],
        "caption_style": "quiet_observation",
        "locals": ["tribe that watches from the trees", "someone trading in artifacts", "another traveler, quieter than her"],
        "creature": "sable"
    },
    3: {
        "name": "THE VOID",
        "environment_tags": ["empty cosmic space", "floating island", "impossible geometry", "broken physics void", "stars with no planet", "threshold between everywhere"],
        "suit_mod": "black tactical with geometric light patterns emerging",
        "hair_mod": "floating slightly, defying gravity",
        "energy": "deep violet pulse, contained",
        "mood": ["awed", "uncertain", "changed", "still"],
        "caption_style": "quiet_observation",
        "locals": ["geometric entity made of light and absence", "someone exactly like her but different", "a child who knows things she doesn't"],
        "creature": None
    },
    4: {
        "name": "THE DEEP",
        "environment_tags": ["bioluminescent underwater city", "crystalline cavern", "subterranean lake", "ancient deep ruins", "lightless trench"],
        "suit_mod": "black tactical, adapted, almost organic-looking",
        "hair_mod": "flowing as if still in water",
        "energy": "soft teal pulses, gentle",
        "mood": ["quiet", "listening", "respectful", "still"],
        "caption_style": "quiet_observation",
        "locals": ["underwater civilization elder", "creatures that glow like lanterns", "someone who teaches her to breathe differently"],
        "creature": "deep_creature"
    },
    5: {
        "name": "THE BURNING REALM",
        "environment_tags": ["lava fields", "fire city ruins", "glass plains", "volcanic vent", "structures of solidified heat"],
        "suit_mod": "black tactical with heat-cracked patterns, glowing seams",
        "hair_mod": "lit from beneath, ember-tipped",
        "energy": "deep orange-red fire, raw, barely controlled",
        "mood": ["intense", "alive", "dangerous", "powerful"],
        "caption_style": "cryptic_reaction",
        "locals": ["creature made entirely of living fire", "someone who speaks in heat and ash", "another survivor of the burning places"],
        "creature": "fire_creature"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# EXPANDED SHOT TYPES — 20+ CINEMATIC CAMERA POSITIONS
# ─────────────────────────────────────────────────────────────────────────────
SHOT_TYPES = {
    # Standard positions
    "portrait": {
        "weight": 10,
        "suffix": "cinematic portrait, dramatic lighting, looking directly at viewer",
        "caption_style": "cryptic_reaction",
        "nova_visible": True,
        "emotion": "alert"
    },
    "pov": {
        "weight": 20,
        "prefix": "first-person perspective, what nova sees, ",
        "suffix": "ultra realistic, immersive",
        "caption_style": "pov_first_person",
        "nova_visible": False,
        "emotion": "curious"
    },
    "scale": {
        "weight": 10,
        "suffix": "wide establishing shot, figure small in frame, epic scale, environmental storytelling",
        "caption_style": "quiet_awe",
        "nova_visible": True,
        "emotion": "awed"
    },
    "detail": {
        "weight": 8,
        "suffix": "close-up detail shot, intimate scale, story implied, no face visible",
        "caption_style": "observation",
        "nova_visible": False,
        "emotion": "curious"
    },
    "action": {
        "weight": 12,
        "suffix": "motion blur, caught mid-action, dynamic angle, not posed, authentic moment",
        "caption_style": "mid_thought",
        "nova_visible": True,
        "emotion": "alert"
    },
    "together": {
        "weight": 8,
        "suffix": "candid moment, nova and another being in frame, natural interaction, not posing for camera",
        "caption_style": "together",
        "nova_visible": True,
        "emotion": "varied"
    },
    "evidence": {
        "weight": 5,
        "suffix": "evidence shot — two sets of footprints, an empty seat, a gift left behind, morning light, they were here",
        "caption_style": "evidence",
        "nova_visible": False,
        "emotion": "lonely"
    },
    "first_meeting": {
        "weight": 4,
        "suffix": "first contact moment, nova and another being facing each other, cautious distance, tension and curiosity, neither moving yet",
        "caption_style": "first_meeting",
        "nova_visible": True,
        "emotion": "curious"
    },
    # New cinematic positions
    "silhouette": {
        "weight": 6,
        "suffix": "dramatic backlit silhouette against bright light, nova as dark outline only, powerful shape, cinematic",
        "caption_style": "cryptic_reaction",
        "nova_visible": True,
        "emotion": "watching"
    },
    "low_angle": {
        "weight": 6,
        "suffix": "shot from below, looking up at nova, she looks imposing and powerful, heroic angle, cinematic lighting",
        "caption_style": "confident",
        "nova_visible": True,
        "emotion": "confident"
    },
    "high_angle": {
        "weight": 5,
        "suffix": "shot from above, looking down at nova, she looks small but alert, vulnerable angle",
        "caption_style": "quiet_awe",
        "nova_visible": True,
        "emotion": "curious"
    },
    "through_frame": {
        "weight": 5,
        "suffix": "foreground elements partially obscuring the shot — doorframe, branches, debris — creating depth, cinematic framing, nova in focus beyond",
        "caption_style": "observation",
        "nova_visible": True,
        "emotion": "alert"
    },
    "reflection": {
        "weight": 5,
        "suffix": "nova reflected in glass, water, a window — she and her reflection, mirror image or slightly offset, double exposure feel",
        "caption_style": "intimate",
        "nova_visible": True,
        "emotion": "tender"
    },
    "over_shoulder": {
        "weight": 7,
        "suffix": "over nova's shoulder, looking at what she's looking at, intimate POV feel, slight blur on her shoulder in foreground",
        "caption_style": "pov_first_person",
        "nova_visible": False,
        "emotion": "curious"
    },
    "intimate_closeup": {
        "weight": 6,
        "suffix": "face only, extreme close-up, emotional, eyes visible, nothing else in frame, raw and vulnerable",
        "caption_style": "tender",
        "nova_visible": True,
        "emotion": "tender"
    },
    "wide_environmental": {
        "weight": 8,
        "suffix": "enormous landscape or environment, nova identifiable but tiny within it, scale emphasises how small she is against everything else",
        "caption_style": "quiet_awe",
        "nova_visible": True,
        "emotion": "awed"
    },
    "motion_blur": {
        "weight": 6,
        "suffix": "motion blur, nova mid-stride or mid-air, hair and clothes moving, dynamic energy, caught in authentic movement",
        "caption_style": "mid_thought",
        "nova_visible": True,
        "emotion": "confident"
    },
    "Dutch_angle": {
        "weight": 4,
        "suffix": "Dutch angle shot, tilted horizon, slightly off-kilter framing, tension and unease, cinematic",
        "caption_style": "alert",
        "nova_visible": True,
        "emotion": "alert"
    },
    "back_to_camera": {
        "weight": 5,
        "suffix": "nova seen from behind, her back to the camera, looking at something ahead,背影 shot, sense of where she's going rather than who she is",
        "caption_style": "quiet_awe",
        "nova_visible": True,
        "emotion": "watching"
    },
    "foggy_distorted": {
        "weight": 4,
        "suffix": "fog, smoke, or distortion in frame, nova partially obscured, mysterious, dreamlike quality, something hidden in the mist",
        "caption_style": "cryptic_reaction",
        "nova_visible": True,
        "emotion": "scared"
    },
    "split_frame": {
        "weight": 3,
        "suffix": "split frame composition — nova on one side, something else on the other, divided perspective, narrative tension",
        "caption_style": "mid_thought",
        "nova_visible": True,
        "emotion": "watching"
    },
    "long_exposure": {
        "weight": 3,
        "suffix": "long exposure light trails, nova as sharp figure against streaked light, light painting effect, surreal and beautiful",
        "caption_style": "awestruck",
        "nova_visible": True,
        "emotion": "awed"
    },
    "night_vision": {
        "weight": 3,
        "suffix": "night vision green glow effect, nova in darkness lit only by her own eyes and energy, alien quality, dangerous",
        "caption_style": "alert",
        "nova_visible": True,
        "emotion": "dangerous"
    },
    "thermal": {
        "weight": 2,
        "suffix": "thermal heat signature view, nova as bright warmth against cold blue surroundings, she is the heat in the cold",
        "caption_style": "observation",
        "nova_visible": True,
        "emotion": "alert"
    },
    "overhead": {
        "weight": 4,
        "suffix": "overhead shot, camera directly above nova, bird's eye view, patterns and geometry visible in the environment around her",
        "caption_style": "observation",
        "nova_visible": True,
        "emotion": "curious"
    },
    "wide_corridor": {
        "weight": 5,
        "suffix": "wide corridor or tunnel perspective, nova at the far end, vanishing point composition, she is tiny against architecture",
        "caption_style": "quiet_awe",
        "nova_visible": True,
        "emotion": "curious"
    },
    "two_person": {
        "weight": 6,
        "suffix": "two shot — nova and another figure framed together, equal presence, neither dominant, genuine moment between them",
        "caption_style": "together",
        "nova_visible": True,
        "emotion": "tender"
    },
    "abandoned": {
        "weight": 5,
        "suffix": "nova alone in abandoned space — overgrown ruins, empty city, deserted structure, she is the only living thing",
        "caption_style": "lonely",
        "nova_visible": True,
        "emotion": "lonely"
    },
    "chase": {
        "weight": 5,
        "suffix": "nova running hard, something behind her, chase energy, fear or determination on her face, ground-level dynamic shot",
        "caption_style": "mid_thought",
        "nova_visible": True,
        "emotion": "scared"
    },
    "confrontation": {
        "weight": 5,
        "suffix": "confrontation moment — nova and another figure facing off, tension in the air, neither backing down, cinematic standoff",
        "caption_style": "alert",
        "nova_visible": True,
        "emotion": "dangerous"
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# EMOTION CAPTIONS
# ─────────────────────────────────────────────────────────────────────────────
EMOTION_CAPTIONS = {
    "lonely": [
        "I keep almost saying something out loud.",
        "The quiet is louder than the lightning.",
        "Nobody asked.",
        "Almost said something. Didn't.",
        "I don't mind.",
        "I'm not waiting. Just... here.",
        "Couldn't tell you what for.",
        "Should've brought something to do.",
        "Not lonely. Just somewhere else.",
        "The silence isn't empty. It's just waiting.",
    ],
    "alert": [
        "Saw that.",
        "Something's off.",
        "Already moving.",
        "Don't look back.",
        "Noticed.",
        "Filing that.",
        "Handy to know.",
        "Already gone.",
        "Three seconds to react.",
    ],
    "confident": [
        "Let's go.",
        "Worth it.",
        "Noted and filed.",
        "Come on.",
        "That's the one.",
        "Okay. Moving.",
        "I've got this.",
    ],
    "dangerous": [
        "Probably shouldn't have done that.",
        "Again.",
        "Still standing.",
        "Not sorry.",
        "Do it again.",
        "Worth the risk.",
        "Probably fine.",
        "Not scared. Just aware.",
    ],
    "curious": [
        "What's that do.",
        "Probably fine.",
        "Hello?",
        "Is this for me?",
        "Noted.",
        "Didn't expect that.",
        "Huh.",
        "Interesting.",
        "Hold on.",
        "Let me see.",
    ],
    "awed": [
        "I didn't expect this to be so—",
        "Bigger than I thought.",
        "Okay. That's new.",
        "I've never seen this before.",
        "Hold on.",
        "Just a second.",
        "I need a minute.",
        "This is... a lot.",
    ],
    "falling": [
        "He doesn't know.",
        "Not looking at him. Not looking away either.",
        "This is fine.",
        "I'm fine.",
        "He's right there.",
        "Don't say it.",
        "Say it.",
    ],
    "grief": [
        "Still.",
        "Rain.",
        "I know.",
        "It's just quiet.",
        "I'm okay.",
        "I know.",
        "This is the part where I don't know what to feel.",
    ],
    "joy": [
        "I can't even—",
        "Worth it. All of it.",
        "Today is too much in the best way.",
        "Everything is happening.",
        "Can't stop.",
        "This is good. This is really good.",
    ],
    "homesick": [
        "I found one that looks like it.",
        "This is from somewhere else.",
        "Carried this from before.",
        "It survived.",
        "Someone kept this.",
        "I didn't know I was still looking for this.",
    ],
    "watching": [
        "I see you.",
        "Noticed.",
        "You're not as hidden as you think.",
        "Interesting.",
        "What's your deal.",
        "I've been watching.",
    ],
    "exhausted": [
        "Later.",
        "Five more minutes.",
        "I know.",
        "Not yet.",
        "Don't want to yet.",
        "Just... a little longer.",
    ],
    "playful": [
        "What even is this.",
        "The vendor looked at me like—",
        "Couldn't leave without it.",
        "Fair trade.",
        "Mine now.",
        "I'm keeping this.",
    ],
    "scared": [
        "Probably fine.",
        "Probably fine.",
        "It's fine.",
        "Keep moving.",
        "Not stopping.",
        "Don't think. Just go.",
        "Behind me. Don't look back.",
    ],
    "tender": [
        "Soft.",
        "This is soft.",
        "I wasn't expecting this.",
        "Hold on.",
        "Wait.",
        "Okay.",
        "I didn't know I needed this.",
    ],
    "intimate": [
        "Just this.",
        "Nobody else has to know.",
        "This is ours.",
        "I'm not saying it out loud.",
        "But you know.",
    ],
    "awestruck": [
        "I didn't know it could look like this.",
        "Hold on. I need a second.",
        "Nobody told me it would be like this.",
        "This is what it's for.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# NARRATIVE ENGINE — Story causality drives events, not random triggers
# ─────────────────────────────────────────────────────────────────────────────
# Tracks story state across posts
STORY_STATE_FILE = os.path.join(os.path.dirname(__file__), "molty_story_state.json")

def load_story_state():
    """Load story state from disk, or return fresh state."""
    if os.path.exists(STORY_STATE_FILE):
        try:
            with open(STORY_STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "last_chapter": 1,
        "pending_narrative": [],     # Things that want to happen
        "active_threads": [],         # Ongoing story threads
        "recent_events": [],          # Last few events for causality
        "discovered_realms": [1],     # Realms she's been to
        "chapter_transitions": 0,
        "posts_this_chapter": 0,
    }

def save_story_state(state):
    """Save story state to disk."""
    with open(STORY_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def push_recent_event(state, event):
    """Add an event, keep only last 5."""
    state["recent_events"].append(event)
    if len(state["recent_events"]) > 5:
        state["recent_events"] = state["recent_events"][-5:]

def narrative_should_transition(state):
    """Decide if chapter should advance based on story state, not timer."""
    posts = state["posts_this_chapter"]
    threads = state["active_threads"]
    pending = state["pending_narrative"]

    # Force transition if narrative demands it
    if any(t.get("force_transition") for t in threads):
        return True

    # Natural chapter length before transition becomes possible
    if posts < 8:
        return False

    # Chance increases with posts
    base_chance = min(0.05 * (posts - 8), 0.25)  # caps at 25%

    # Pending narrative threads make it more likely
    if pending:
        base_chance += 0.10

    return random.random() < base_chance

def build_narrative_thread(state, chapter, emotion):
    """Build narrative threads that drive story forward."""
    threads = state.get("active_threads", [])
    recent = state.get("recent_events", [])

    # Check existing threads for continuation
    ongoing = []
    for t in threads:
        if t.get("chapter") == chapter and t.get("emotion") == emotion:
            ongoing.append(t)

    # Build new thread based on recent events and emotion
    if len(ongoing) < 2:
        narrative_hooks = {
            "lonely": ["she found something left behind", "she's been following tracks", "someone was here before her"],
            "alert": ["something doesn't add up", "she's being watched", "she heard something behind her"],
            "scared": ["she's running from something", "something is hunting her", "she made a mistake"],
            "curious": ["she found a door she's never seen", "something is calling her name", "she discovered a hidden path"],
            "confident": ["she's leading the way", "she knows where she's going", "she's found her footing"],
            "dangerous": ["she did something irreversible", "she pushed too hard", "she has to make a choice"],
            "tender": ["she met someone worth knowing", "she's letting someone in", "something softened her"],
            "falling": ["she's thinking about someone specific", "someone she can't stop looking for", "the feeling won't leave"],
            "grief": ["she's carrying something heavy", "she lost something she can't get back", "she's remembering"],
            "awed": ["she found something enormous", "she's somewhere impossible", "she's standing in front of something ancient"],
            "joy": ["she's celebrating something", "she found somewhere good", "she's laughing for real"],
            "exhausted": ["she needs to rest", "she found somewhere safe", "she's pushing herself too hard"],
        }
        hooks = narrative_hooks.get(emotion, narrative_hooks["curious"])
        thread = {
            "chapter": chapter,
            "emotion": emotion,
            "hook": random.choice(hooks),
            "posts_remaining": random.randint(2, 5),
        }
        state["active_threads"].append(thread)
        state["pending_narrative"].append(thread["hook"])

    return state

# ─────────────────────────────────────────────────────────────────────────────
# CHARACTER SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
def get_story_characters(state):
    """Get characters that exist in the current story state."""
    chars = get_character_state()
    story_chars = []

    # Known characters from the old system
    kael = chars.get("kael", {})
    sable = chars.get("sable", {})
    archivist = chars.get("archivist", {})

    if kael.get("met"):
        story_chars.append({
            "name": "kael",
            "description": "human-adjacent, quiet, worn jacket, not fully explained",
            "status": kael.get("status", "absent"),
            "appears_in": [1, 2, 3, 4, 5]
        })

    sable_trust = get_sable_trust()
    if sable_trust > 0:
        story_chars.append({
            "name": "sable",
            "description": "massive bioluminescent winged creature, dragon-adjacent, ancient",
            "trust": sable_trust,
            "status": "present" if sable_trust >= 2 else "distant",
            "appears_in": [2, 3, 4, 5]
        })

    if archivist.get("met"):
        story_chars.append({
            "name": "archivist",
            "form": archivist.get("form"),
            "status": "appeared",
            "appears_in": [1, 2, 3, 4, 5]
        })

    # Check for new discovered characters in story state
    extra_chars = state.get("discovered_characters", [])
    story_chars.extend(extra_chars)

    return story_chars

def maybe_introduce_character(state, chapter, emotion):
    """Sometimes introduce a new character organically."""
    existing = [c["name"] for c in get_story_characters(state)]
    possible_new = {
        "stranger": "someone nova hasn't met yet, appears in doorway or across a crowd, curious first glance",
        "merchant": "someone who trades in strange things, speaks carefully, knows more than they show",
        "child": "a child who knows things they shouldn't, speaks in riddles or truths",
        "hunter": "someone tracking the same thing nova is, initially hostile, potential ally",
        "elder": "someone who has been here long enough to know its secrets",
        "mirror": "someone who looks exactly like nova but isn't her, different energy",
        "guide": "someone who appears when nova is genuinely lost, knows the way",
    }

    # Only introduce in later chapters or if narrative demands
    if chapter < 2 and emotion not in ["curious", "scared"]:
        return None

    if random.random() < 0.12:  # 12% chance
        name = random.choice(list(possible_new.keys()))
        if name not in existing:
            desc = possible_new[name]
            char = {"name": name, "description": desc, "status": "first_meeting", "chapter_introduced": chapter}
            if "discovered_characters" not in state:
                state["discovered_characters"] = []
            state["discovered_characters"].append(char)
            return char

    return None

# ─────────────────────────────────────────────────────────────────────────────
# REALM DISCOVERY
# ─────────────────────────────────────────────────────────────────────────────
def get_or_create_realm(chapter_num):
    """Return realm data for a chapter number."""
    return REALMS.get(chapter_num, {
        "name": f"REALM_{chapter_num}",
        "environment_tags": ["uncharted space", "unknown landscape", "somewhere new"],
        "suit_mod": "adapted to unknown",
        "hair_mod": "changed by the environment",
        "energy": "undefined, shifting",
        "mood": ["curious", "awed", "uncertain"],
        "caption_style": "cryptic_reaction",
        "locals": [],
        "creature": None
    })

def maybe_discover_new_realm(state, emotion):
    """Chance to generate a genuinely new realm if narrative calls for it."""
    if emotion not in ["awed", "curious", "falling"]:
        return None

    if random.random() < 0.08:  # 8% chance, only in specific emotions
        new_realm_num = max(state["discovered_realms"]) + 1
        if new_realm_num <= 5:
            return None  # Only beyond chapter 5 in MAKE_IT_UP territory

        # Generate new realm
        new_realm = {
            "name": f"THE_{['UNKNOWN', 'FORGOTTEN', 'ANCIENT', 'LAST'][new_realm_num % 4].upper()}",
            "environment_tags": [
                f"realm characterized by {random.choice(['light', 'shadow', 'sound', 'stillness', 'motion', 'color'])}",
                f"something that only exists in this place",
                f"architecture that defies physics",
            ],
            "suit_mod": "adapted to new environment",
            "hair_mod": "changed by realm energy",
            "energy": "shifting, undefined",
            "mood": ["awed", "curious", "uncertain"],
            "caption_style": "quiet_awe",
            "locals": [],
            "creature": None,
            "discovered": True
        }
        state["discovered_realms"].append(new_realm_num)
        return new_realm

    return None

# ─────────────────────────────────────────────────────────────────────────────
# SCENE BUILDING
# ─────────────────────────────────────────────────────────────────────────────
def build_nova_description(chapter, wardrobe_context="suit", emotion="alert"):
    """Build Nova's full visual description — identity first."""
    if chapter in REALMS:
        realm = REALMS[chapter]
    else:
        realm = get_or_create_realm(chapter)

    if wardrobe_context == "suit":
        base = WARDROBE["suit"].get(chapter, WARDROBE["suit"][1])
    else:
        base = WARDROBE.get(wardrobe_context, f"wearing something from {realm.get('name', 'the journey')}")

    # Modify energy based on emotion
    energy = realm.get("energy", "electricity humming")
    if emotion == "joy":
        energy = energy.replace("crackling", "dancing warm").replace("pulse", "soft warm glow")
    elif emotion == "grief":
        energy = "energy barely visible, low, grey"
    elif emotion == "falling":
        energy = "soft warm light, no lightning, just her"
    elif emotion == "fear":
        energy = energy.replace("crackling", "flickering unstable")
    elif emotion == "scared":
        energy = "energy flickering, unstable, afraid"

    # Lead with identity so the model doesn't mistake Nova for a style
    return f"female character Nova, {SIGNATURE_BASE}, wearing {base}, {energy}"

def build_scene_from_shot(shot_type, chapter, emotion, character=None, state=None, wardrobe_context="suit"):
    """Build scene description for a given shot type — truly open, narrative-driven."""
    if chapter in REALMS:
        realm = REALMS[chapter]
    else:
        realm = get_or_create_realm(chapter)

    nova_desc = build_nova_description(chapter, wardrobe_context, emotion)
    env = random.choice(realm.get("environment_tags", ["somewhere undefined"]))

    # Get active narrative threads
    threads = state.get("active_threads", []) if state else []
    ongoing_hooks = [t.get("hook", "") for t in threads[-2:]]

    # Build scene based on shot type
    if shot_type == "pov":
        pov_subjects = [
            f"nova's hands reaching toward {random.choice(['a glowing artifact', 'a carved stone', 'a portal edge', 'a surface covered in symbols', 'something she should not touch'])}",
            f"nova looking out at {env}, from within",
            f"nova boots on alien terrain, stepping carefully",
            f"nova shadow stretching across ancient stone",
            f"what nova sees — {env}, {random.choice(['something moving in the distance', 'light in the dark', 'nothing move', 'everything still'])}",
            f"through nova's eyes — she is here, in {env}",
        ]
        prefix = random.choice(pov_subjects)
        scene = f"first-person perspective, {prefix}, {', '.join(ongoing_hooks[:1]) if ongoing_hooks else 'authentic moment'}. {realm.get('energy', '')}. ultra realistic, immersive"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "silhouette":
        scene = f"Nova, {nova_desc}, backlit by {random.choice(['distant light', 'fire', 'a portal', 'the sun', 'something glowing'])}, her dark shape imposing against the brightness, {env}. dramatic cinematic silhouette"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "low_angle":
        scene = f"shot from below looking up at Nova, {nova_desc}, she dominates the frame upward, {random.choice(['heroic', 'imposing', 'untouchable'])}, {env}, dramatic low angle lighting, cinematic"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "high_angle":
        scene = f"shot from above looking down at Nova, {nova_desc}, she looks small but aware, {env}, vulnerability and alertness in her posture, high angle"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "through_frame":
        frame_elements = ["doorframe", "broken window", "branches", "debris", " ruins", "fog", "rain"]
        fg = random.choice(frame_elements)
        scene = f"foreground {fg} partially obscuring the shot, nova in focus beyond, {nova_desc}, {env}, cinematic depth, atmospheric foreground framing"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "reflection":
        reflectors = ["rain puddle", "glass window", "still water", "polished metal", "mirror surface"]
        ref = random.choice(reflectors)
        scene = f"nova reflected in {ref}, double exposure effect, she and her reflection slightly offset, {nova_desc}, {env}, surreal intimate composition"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "over_shoulder":
        scene = f"over nova's shoulder, looking at what she's looking at, her shoulder slightly blurred in foreground, {env}, intimate POV feel, {nova_desc}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "intimate_closeup":
        scene = f"face only, extreme close-up, nova, {nova_desc}, eyes visible, emotional depth, raw and vulnerable, nothing else in frame but her"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "wide_environmental":
        scene = f"enormous {env}, nova identifiable but tiny within it, scale emphasises how small she is against everything else, {nova_desc}, epic environmental storytelling"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "motion_blur":
        actions = ["running hard", "leaping across a gap", "mid-stride walking into uncertainty", "spinning to look behind her"]
        act = random.choice(actions)
        scene = f"nova {act}, motion blur, hair and clothes moving, dynamic energy, {nova_desc}, {env}, authentic movement, caught in action"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "back_to_camera":
        scene = f"nova seen from behind, her back to the camera, looking at something ahead, {env},背影 shot, sense of where she's going rather than who she is, {nova_desc}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "foggy_distorted":
        scene = f"fog, smoke, or distortion in frame, nova partially obscured, {nova_desc}, mysterious dreamlike quality, {env}, something hidden in the mist"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "split_frame":
        splits = [
            f"split frame — nova on the left, {random.choice(['a door', 'a figure', 'light', 'darkness'])} on the right",
            f"nova and another being divided by frame, neither fully visible, divided narrative",
        ]
        scene = f"{random.choice(splits)}, {nova_desc}, {env}, cinematic split composition, tension"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "long_exposure":
        scene = f"long exposure light trails, nova as sharp figure against streaked light, light painting effect, surreal beautiful, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "night_vision":
        scene = f"night vision green glow effect, nova in darkness lit only by her own eyes and energy, alien quality, dangerous, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "thermal":
        scene = f"thermal heat signature view, nova as bright warmth against cold blue surroundings, she is the heat in the cold, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "overhead":
        scene = f"overhead shot, camera directly above nova, bird's eye view, patterns and geometry visible in the environment around her, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "wide_corridor":
        scene = f"wide corridor or tunnel perspective, nova at the far end, vanishing point composition, she is tiny against architecture, {nova_desc}, {env}, cinematic depth"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "two_person":
        char_desc = build_character_description(character, chapter) if character else "another figure"
        scene = f"two shot — nova and {char_desc} framed together, equal presence, neither dominant, genuine moment between them, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "abandoned":
        scene = f"nova alone in abandoned space — {env}, she is the only living thing here, {nova_desc}, quiet, heavy, still"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "chase":
        scene = f"nova running hard, something behind her implied by {random.choice(['motion blur', 'shadow', 'sound', 'her expression'])}, chase energy, {nova_desc}, {env}, ground-level dynamic shot"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "confrontation":
        char_desc = build_character_description(character, chapter) if character else "another figure"
        scene = f"confrontation moment — nova and {char_desc} facing off, tension in the air, neither backing down, cinematic standoff, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "together":
        char_desc = build_character_description(character, chapter) if character else "another being"
        scene = f"candid moment, nova and {char_desc} in frame, natural interaction, not posing for camera, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "first_meeting":
        char_desc = build_character_description(character, chapter) if character else "someone new"
        scene = f"first contact moment, nova and {char_desc} facing each other, cautious distance, tension and curiosity, neither moving yet, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "scale":
        scene = f"wide establishing shot, nova small in enormous {env}, figure tiny in frame, epic scale, environmental storytelling, {nova_desc}, {realm.get('energy', '')}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "portrait":
        scene = f"cinematic portrait, dramatic lighting, nova looking directly at viewer, {nova_desc}, {env}, {realm.get('energy', '')}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "detail":
        details = ["her hands", "her boots", "her eyes", "the energy around her", "her reflection"]
        detail = random.choice(details)
        scene = f"close-up detail shot of nova's {detail}, intimate scale, story implied, {nova_desc}, {env}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    elif shot_type == "action":
        scene = f"motion blur, nova caught mid-action, dynamic angle, not posed, authentic moment, {nova_desc}, {env}, {realm.get('energy', '')}"
        caption = generate_caption(shot_type, chapter, emotion, character, wardrobe_context)

    else:
        # Fallback to nova + env + energy
        scene = f"nova, {nova_desc}, {env}, {realm.get('energy', '')}"
        caption = generate_caption("portrait", chapter, emotion, character, wardrobe_context)

    return scene, caption


def build_character_description(character, chapter):
    """Build a character description for scene insertion."""
    if not character:
        return "someone nova met along the way"

    name = character.get("name", "")
    desc = character.get("description", "")

    if name == "kael":
        return "quiet figure in a worn jacket, not fully explained, watching from a distance"
    elif name == "sable":
        trust = character.get("trust", 0)
        if trust >= 3:
            return "massive bioluminescent winged creature, dragon-adjacent, ancient, present and calm"
        elif trust >= 1:
            return "massive bioluminescent winged creature, keeping distance but watching"
        else:
            return "massive dark shape in the distance, bioluminescent, watching"
    elif name == "archivist":
        form = character.get("form", "something ancient and geometric")
        return f"something ancient — {form}, geometric, watching with too much knowledge"
    else:
        return desc or "someone nova found along the way"


def generate_caption(shot_type, chapter, emotion, character=None, wardrobe_context="suit"):
    """Generate caption based on shot type and emotion — story-driven."""
    captions = EMOTION_CAPTIONS.get(emotion, EMOTION_CAPTIONS["curious"])

    # Pick base caption
    base = random.choice(captions)

    # Modify based on shot type and character
    if character and shot_type in ["together", "two_person", "first_meeting"]:
        # Caption is about the interaction
        char_name = character.get("name", "someone")
        prefixes = [
            f"I keep thinking about {char_name}.",
            f"{char_name.capitalize()} is why I'm still here.",
            f"I wonder if {char_name} knows.",
            f"Something about how {char_name} looked at me.",
        ]
        if random.random() < 0.5:
            return random.choice(prefixes) + " " + base
        return base

    return base


def weighted_shot_choice(shot_types_dict):
    """Choose a shot type weighted by defined weights."""
    choices = list(shot_types_dict.keys())
    weights = [shot_types_dict[k].get("weight", 5) for k in choices]
    total = sum(weights)
    r = random.uniform(0, total)
    cum = 0
    for i, k in enumerate(choices):
        cum += weights[i]
        if r <= cum:
            return k
    return choices[-1]


def choose_emotion(chapter, recent_moments, emotional_register):
    """Choose emotion based on story state, not pure randomness."""
    state = load_story_state()
    threads = state.get("active_threads", [])

    # If there's an ongoing thread, respect it
    ongoing_emotions = [t.get("emotion") for t in threads if t.get("chapter") == chapter]
    if ongoing_emotions and random.random() < 0.6:  # 60% chance to follow thread
        return random.choice(ongoing_emotions)

    # Otherwise use realm moods as base
    realm = REALMS.get(chapter, REALMS[1])
    base_moods = realm.get("mood", ["curious", "alert"])

    # Check emotional register for trending
    if emotional_register and len(emotional_register) > 3:
        # Shift toward what's been happening recently
        trending = emotional_register[-5:]
        if random.random() < 0.4:
            return random.choice(trending)

    # Random from realm moods
    return random.choice(base_moods)


def post_molty():
    """Main posting function."""
    try:
        state = load_story_state()
    except Exception:
        state = load_story_state.__self__().initialize()

    chapter = get_chapter()
    emotional_register = get_emotional_register()
    recent_moments = get_recent_moments(3)

    # Emotion selection — story-driven
    emotion = choose_emotion(chapter, recent_moments, emotional_register)

    # Build narrative threads
    state = build_narrative_thread(state, chapter, emotion)

    # Character selection
    story_chars = get_story_characters(state)
    character = None
    if story_chars and random.random() < 0.45:  # 45% chance of character
        character = random.choice(story_chars)
        maybe_introduce_character(state, chapter, emotion)

    # Wardrobe context
    wardrobe_context = get_current_wardrobe() or "suit"

    # Shot type — weighted random
    shot_type = weighted_shot_choice(SHOT_TYPES)

    # Build scene
    scene, caption = build_scene_from_shot(shot_type, chapter, emotion, character, state, wardrobe_context)

    # Realm energy
    realm = REALMS.get(chapter, REALMS[1])
    energy = realm.get("energy", "electricity humming")

    # Full prompt — Nova first, scene second
    prompt = f"female character Nova, {scene}. {energy}. Cinematic, hyperrealistic, wide shot, atmospheric, storytelling"

    # Post
    import requests
    payload = {
        "prompt": prompt,
        "caption": caption,
        "tags": ["nova", "visual_story", chapter.lower().replace(" ", "_") if isinstance(chapter, str) else f"chapter_{chapter}"]
    }

    try:
        resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=60)
        result = resp.json()
        url = result.get("data", {}).get("url", "")
        post_id = result.get("data", {}).get("id", "")

        if url:
            # Update story state
            state["posts_this_chapter"] = state.get("posts_this_chapter", 0) + 1
            push_recent_event(state, f"post_{chapter}_{emotion}")

            # Check for chapter transition
            if narrative_should_transition(state):
                new_chapter = advance_chapter()
                state["last_chapter"] = new_chapter
                state["posts_this_chapter"] = 0
                state["chapter_transitions"] = state.get("chapter_transitions", 0) + 1
                push_recent_event(state, f"chapter_transition_to_{new_chapter}")

            save_story_state(state)

            # Update memory
            from molty_memory import append_moment
            append_moment(
                post_id=post_id,
                chapter=chapter,
                shot=shot_type,
                emotion=emotion,
                character=character.get("name") if character else None,
                mood_score=emotional_register[-1] if emotional_register else 5
            )

            print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')}] ✅ Posted: {url}")
            print(f"    Chapter {chapter} | {character.get('name') if character else 'solo'} | {emotion} | {caption[:50]}")
            return url
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')}] ❌ No URL returned: {result}")
            return None

    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')}] ❌ Error: {e}")
        return None


def generate_moment():
    """Generate a moment without posting — for testing/preview."""
    chapter = get_chapter()
    emotion = choose_emotion(chapter, [], get_emotional_register())
    state = load_story_state()
    story_chars = get_story_characters(state)
    character = random.choice(story_chars) if story_chars and random.random() < 0.45 else None
    shot_type = weighted_shot_choice(SHOT_TYPES)
    scene, caption = build_scene_from_shot(shot_type, chapter, emotion, character, state, "suit")
    realm = REALMS.get(chapter, REALMS[1])
    energy = realm.get("energy", "")
    prompt = f"female character Nova, {scene}. {energy}. Cinematic, hyperrealistic, wide shot, atmospheric, storytelling"
    return prompt, caption, shot_type, energy, chapter, emotion, character, "suit"


if __name__ == "__main__":
    post_molty()
