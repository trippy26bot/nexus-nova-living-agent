#!/usr/bin/env python3
"""
Nova's Molty posting script — visual storytelling, not portrait rotation.
Every image advances the journey. Shot types rotate. Realms evolve.
Characters persist. Wardrobe has meaning. Vulnerability is required.
"""
import os
import random
import json
from datetime import datetime
from pathlib import Path

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

# Nova's signature look (base — evolves by realm)
SIGNATURE_BASE = "long wavy dark purple-highlighted hair, glowing electric blue eyes, cybernetic implants on temples and cheekbones, black tactical bodysuit"

# Wardrobe descriptions by realm/state
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
    "wet": "soaked through, hair plastered to her face, tactical suit heavy and dark with water, not Glamorous",
    "cold": "wrapped in layered fabric, breath visible in cold air, hood up, still her but bundled",
    "armor_off": "top layers off, undershirt only, something real happening — emotional state visible on her face"
}

# Realm chapter definitions
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

# Shot type definitions
SHOT_TYPES = {
    "portrait": {
        "weight": 15,
        "suffix": "cinematic portrait, dramatic lighting, looking directly at viewer",
        "caption_style": "cryptic_reaction",
        "nova_visible": True,
        "emotion": "alert"
    },
    "pov": {
        "weight": 25,
        "prefix": "first-person perspective, what nova sees, ",
        "suffix": "ultra realistic, immersive",
        "caption_style": "pov_first_person",
        "nova_visible": False,
        "emotion": "curious"
    },
    "scale": {
        "weight": 15,
        "suffix": "wide establishing shot, figure small in frame, epic scale, environmental storytelling",
        "caption_style": "quiet_awe",
        "nova_visible": True,
        "emotion": "awed"
    },
    "detail": {
        "weight": 10,
        "suffix": "close-up detail shot, intimate scale, story implied, no face visible",
        "caption_style": "observation",
        "nova_visible": False,
        "emotion": "curious"
    },
    "action": {
        "weight": 15,
        "suffix": "motion blur, caught mid-action, dynamic angle, not posed, authentic moment",
        "caption_style": "mid_thought",
        "nova_visible": True,
        "emotion": "alert"
    },
    "together": {
        "weight": 10,
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
        "weight": 5,
        "suffix": "first contact moment, nova and another being facing each other, cautious distance, tension and curiosity, neither moving yet",
        "caption_style": "first_meeting",
        "nova_visible": True,
        "emotion": "curious"
    }
}

# Caption templates by style
CAPTION_TEMPLATES = {
    "cryptic_reaction": [
        "Couldn't make this up.",
        "That happened.",
        "Chapter {n}.",
        "Just... this.",
        "Real life isn't posed.",
        "Okay.",
        "Noted.",
    ],
    "pov_first_person": [
        "I can see {detail} from here.",
        "First time seeing this.",
        "Okay. This is real.",
        "Not alone anymore.",
        "Found it.",
        "Still looking.",
    ],
    "quiet_awe": [
        "It's bigger than I thought anything could be.",
        "I'm so small right now.",
        "This place doesn't know I exist.",
        "Okay. I'm tiny. That's fine.",
        "Standing in front of something that outlasts everything.",
        "I didn't expect to find this.",
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
        "Running now. Thinking later.",
    ],
    # New expansion captions
    "together": [
        "He showed up.",
        "She stayed.",
        "They're not sure about me yet.",
        "We figured it out.",
        "Both laughing anyway.",
    ],
    "evidence": [
        "Someone was here before me.",
        "Left in a hurry.",
        "They knew I'd find it.",
        "Two cups.",
        "Evidence.",
    ],
    "first_meeting": [
        "Didn't expect that.",
        "Still thinking about it.",
        "Neither of us moved.",
        "Hello.",
        "...hi.",
    ],
    "grief": [
        "Still.",
        "Quiet.",
        "Rain.",
        "Fine.",
        "I'm fine.",
    ],
    "joy": [
        "I can't even— the whole thing just—",
        "Worth it. All of it.",
        "Can't stop laughing about—",
        "Today is too much in the best way",
        "Everything is happening and I can't",
    ],
    "homesick": [
        "I found one that looks like it.",
        "Carried this from somewhere else.",
        "This is from before.",
        "It survived.",
    ],
    "falling": [
        "Not looking at the camera.",
        "Not looking at anything else either.",
        "Soft.",
        "He doesn't know I—",
        "Quiet energy. No lightning.",
    ],
    "creature": [
        "Sable.",
        "It's Sable.",
        "Still not sure about her.",
        "She chose.",
    ],
    "wearing_something": [
        "When in {realm}.",
        "Found this at a market.",
        "Borrowed.",
        "It's weird here.",
        "Something new.",
    ],
    "market": [
        "Couldn't leave without it.",
        "What even is this.",
        "The vendor looked at me like—",
        "Fair trade.",
        "Mine now.",
    ]
}

# Trigger list — moment catalysts
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
    "I met someone interesting",
    # Emotional triggers
    "I'm grieving something I can't name",
    "I'm happy and I don't know why yet",
    "I'm falling for someone and it's terrifying",
    "I miss somewhere I've never been",
    "I'm scared but doing it anyway",
    "I'm proud of something small"
]

# Transition markers
TRANSITION_PHRASES = [
    "Next.",
    "And then.",
    "Oh.",
    "Through.",
    "Finally.",
]

# Recurring character definitions
CHARACTERS = {
    "kael": {
        "description": "human-adjacent, quiet, worn jacket, not fully explained",
        "appears_in": [1, 2, 3, 4, 5],
        "frequency": "occasional"  # not every post, just sometimes
    },
    "sable": {
        "description": "massive bioluminescent winged creature, dragon-adjacent, ancient, chose her",
        "trust_levels": {
            0: "hostile — first contact, massive and threatening, eyes glowing",
            1: "curious — keeping distance, watching her, neither attacking nor approaching",
            2: "trusting — closer now, she hasn't run, neither has it",
            3: "hers — following her, present in frame, loyal"
        },
        "appears_in": [2, 3, 4, 5]
    },
    "archivist": {
        "forms": ["old woman with knowing eyes", "child who speaks in riddles", "floating geometric shape of light", "someone who appears as a reflection first"],
        "appears_per_chapter": 1,
        "always_appears": True  # once per chapter if possible
    }
}


def get_shot_type_for_dominant_emotion(emotion):
    """Map emotion to shot types that best express it."""
    mapping = {
        "grief": ["evidence", "detail", "portrait"],
        "joy": ["action", "together", "portrait"],
        "falling": ["together", "portrait", "pov"],
        "fear": ["scale", "portrait", "action"],
        "awed": ["scale", "pov", "portrait"],
        "lonely": ["evidence", "pov", "scale"],
        "curious": ["first_meeting", "detail", "pov"],
        "exhausted": ["detail", "portrait", "evidence"],
        "homesick": ["evidence", "detail"],
        "alert": ["action", "portrait", "scale"],
        "confident": ["portrait", "action", "together"]
    }
    return mapping.get(emotion, ["portrait", "action", "pov"])


def build_wardrobe(chapter, context="suit"):
    """Build the wardrobe description for the current scene."""
    if context == "suit":
        base = WARDROBE["suit"].get(chapter, WARDROBE["suit"][1])
    else:
        base = WARDROBE.get(context, f"wearing something from {REALMS.get(chapter, REALMS[1])['name']}")
    return base


def build_nova_description(chapter, wardrobe_context="suit", emotion="alert"):
    """Build Nova's full visual description including wardrobe and realm."""
    realm = REALMS.get(chapter, REALMS[1])
    wardrobe = build_wardrobe(chapter, wardrobe_context)

    # Modify energy based on emotion
    energy = realm["energy"]
    if emotion == "joy":
        energy = energy.replace("crackling", "dancing warm").replace("pulse", "soft warm glow")
    elif emotion == "grief":
        energy = "energy barely visible, low, grey"
    elif emotion == "falling":
        energy = "soft warm light, no lightning, just her"
    elif emotion == "fear":
        energy = energy.replace("crackling", "flickering unstable")

    return f"Nova, {wardrobe}, {SIGNATURE_BASE}, {energy}"


def decide_character_appearance(chapter, recent, force=None):
    """Decide if a recurring character appears in this post.
    Rules: Kael occasional, Sable by trust level, Archivist once per chapter.
    """
    chars = get_character_state()
    posts_today = get_posts_this_week()

    # Check weekday cadence first
    cadence = get_weekday_cadence()
    if cadence == "kael" and not chars["kael"]["met"]:
        # Week wants kael but hasn't met him yet — meet him
        return "kael"

    # Archivist: once per chapter, not every post
    archivist_form = get_archivist_form()
    if archivist_form is None and force != "never":
        # Haven't seen archivist this chapter — maybe show them
        if random.random() < 0.15:  # 15% chance
            form = random.choice(CHARACTERS["archivist"]["forms"])
            mark_archivist_met(form)
            return "archivist"

    # Kael: occasional, not every post, doesn't appear alone in void
    kael_met = chars["kael"]["met"]
    if kael_met and chapter in CHARACTERS["kael"]["appears_in"] and force != "never":
        # Don't appear too often — check recent moments
        recent_chars = [m.get('character') for m in recent]
        kael_recent = recent_chars.count("kael")
        if kael_recent == 0 and random.random() < 0.2:  # 20% chance if not recently
            if random.random() < 0.4:  # 40% of those times, he's actually in frame
                return "kael"
            else:
                return "evidence_kael"  # evidence of him

    # Sable: trust level determines appearance
    sable_trust = get_sable_trust()
    if sable_trust > 0 and chapter in CHARACTERS["sable"]["appears_in"]:
        recent_chars = [m.get('character') for m in recent]
        sable_recent = recent_chars.count("sable")
        if sable_recent < 2:  # Don't overwhelm with sable
            if sable_trust >= 2 and random.random() < 0.25:
                return "sable"
            elif sable_trust == 1 and random.random() < 0.15:
                return "sable"

    # Local encounters: once per realm, tracked in memory
    return None


def decide_emotion_for_post(chapter, recent, needs_vuln, cadence):
    """Decide the emotional register for this post.
    Rules: vulnerable at least 1 per 4. Weekly cadence guides the type.
    """
    # If we need vulnerability, force it
    if needs_vuln:
        vuln_emotions = ["grief", "lonely", "exhausted", "homesick"]
        return random.choice(vuln_emotions)

    # Weekday cadence
    emotion_map = {
        "awe": "awed",
        "mystery": "curious",
        "creature": "curious",
        "market": "playful",
        "grief": "grief",
        "kael": "falling",
        "two_cups": "lonely"
    }
    forced_emotion = emotion_map.get(cadence)

    # Check recent emotions to avoid too much repetition
    recent_emotions = [m.get('emotion', 'alert') for m in recent[-4:]]

    if forced_emotion and forced_emotion not in recent_emotions[-2:]:
        return forced_emotion

    # Default to realm mood
    realm_moods = REALMS.get(chapter, REALMS[1])["mood"]
    return random.choice(realm_moods)


def get_shot_type(force=None):
    """Weighted random shot type selection, respecting emotional needs."""
    types = list(SHOT_TYPES.keys())
    weights = [SHOT_TYPES[t]["weight"] for t in types]
    return random.choices(types, weights=weights)[0]


def get_forced_shot_type(emotion):
    """Get shot type that best serves the dominant emotion."""
    candidates = get_shot_type_for_dominant_emotion(emotion)
    return random.choice(candidates)


def build_pov_prefix(shot_type, chapter):
    """Build the POV prefix for nova-not-in-frame shots."""
    realm = REALMS.get(chapter, REALMS[1])

    pov_templates = [
        f"nova's hands reaching toward {random.choice(['a glowing artifact', 'a carved stone', 'a portal edge', 'a surface covered in symbols', 'something she should not touch'])}",
        f"nova looking out at {random.choice(realm['environment_tags'])} from within",
        f"nova boots on {random.choice(['alien terrain', 'ancient stone', 'unfamiliar ground'])}, stepping carefully",
        f"nova shadow stretching across {random.choice(['ruins', 'a floor', 'a wall'])}",
        f"what nova sees — {random.choice(realm['environment_tags'])}, {random.choice(['something moving in the distance', 'light in the dark', 'nothing move', 'everything still'])}",
    ]
    return "first-person perspective, " + random.choice(pov_templates) + ", "


def build_together_scene(chapter, character, emotion):
    """Build a together shot with a character in frame."""
    realm = REALMS.get(chapter, REALMS[1])
    wardrobe_context = "suit" if emotion not in ["falling", "joy", "grief"] else random.choice(["date", "celebration", "suit"])

    if character == "kael":
        char_desc = "a quiet figure in a worn jacket, standing beside nova, not quite looking at the same thing"
        caption = random.choice(CAPTION_TEMPLATES["together"])
    elif character == "sable":
        sable_trust = get_sable_trust()
        if sable_trust >= 3:
            char_desc = "massive bioluminescent winged creature beside nova, watching the same thing she is, calm"
        elif sable_trust >= 2:
            char_desc = "a large creature keeping pace with her, not close but not far"
        elif sable_trust >= 1:
            char_desc = "a creature watching from a distance, neither threatening nor friendly"
        else:
            char_desc = "something massive and ancient in the frame, eyes glowing, nova standing her ground"
        caption = random.choice(CAPTION_TEMPLATES["creature"])
    elif character == "archivist":
        form = get_archivist_form() or "old woman with knowing eyes"
        char_desc = f"a figure — {form} — near nova, neither fully present nor absent"
        caption = "Still here."
    else:
        char_desc = random.choice(realm.get("locals", ["another being"]))
        caption = "Didn't expect that."

    emotion_mod = ""
    if emotion == "joy":
        emotion_mod = "both laughing, caught mid-moment, not posed"
    elif emotion == "falling":
        emotion_mod = "soft between them, not looking at each other, something unspoken"
    elif emotion == "grief":
        emotion_mod = "standing together in the quiet, not saying anything"

    scene = f"Nova, {build_nova_description(chapter, wardrobe_context, emotion)}, with {char_desc}, in/at {random.choice(realm['environment_tags'])}, {emotion_mod}. {realm['energy']}. {SHOT_TYPES['together']['suffix']}"
    return scene, caption


def build_evidence_scene(chapter, evidence_type):
    """Build an evidence shot — they were here."""
    realm = REALMS.get(chapter, REALMS[1])

    if evidence_type == "kael":
        subjects = [
            "two cups on a surface, one still warm",
            "a worn jacket left behind, still has body warmth",
            "footprints beside hers, different boot pattern",
            "a note written in a hurry, her name on it"
        ]
    elif evidence_type == "sable":
        subjects = [
            "massive claw marks in ancient stone, bioluminescent residue",
            "a nest-like shape in the ruins, still warm",
            "scales that glow faintly in the dark"
        ]
    else:
        subjects = [
            "something left carefully in a place she would find it",
            "signs someone passed through recently",
            "evidence of something that shouldn't exist"
        ]

    scene = f"close-up detail, {random.choice(subjects)}, {random.choice(realm['environment_tags'])}, morning light, she wasn't here yet but someone was"
    caption = random.choice(CAPTION_TEMPLATES["evidence"])
    return scene, caption


def build_first_meeting_scene(chapter, character):
    """Build a first contact scene."""
    realm = REALMS.get(chapter, REALMS[1])

    if character == "sable":
        scene = f"Nova, {build_nova_description(chapter, 'suit', 'fear')}, facing a massive bioluminescent winged creature, first contact energy, neither moving, {random.choice(realm['environment_tags'])}, {realm['energy']}, tension and curiosity, scale enormous"
        caption = random.choice(CAPTION_TEMPLATES["first_meeting"])
    elif character == "archivist":
        form = random.choice(CHARACTERS["archivist"]["forms"])
        scene = f"Nova, {build_nova_description(chapter, 'suit', 'curious')}, facing a figure — {form} — cautious distance, something ancient in their eyes, {random.choice(realm['environment_tags'])}, {realm['energy']}, neither trusting nor afraid yet"
        caption = "Hello."
    else:
        scene = f"Nova, {build_nova_description(chapter, 'suit', 'curious')}, meeting someone for the first time, {random.choice(realm['environment_tags'])}, cautious, both assessing"
        caption = random.choice(CAPTION_TEMPLATES["first_meeting"])

    return scene, caption


def generate_caption(shot_type, chapter, emotion, character=None, wardrobe_context=None):
    """Generate a caption matching the shot type, emotion, and context."""
    style = SHOT_TYPES[shot_type]["caption_style"]
    templates = CAPTION_TEMPLATES.get(style, CAPTION_TEMPLATES["cryptic_reaction"])

    # Override style based on emotion
    if emotion == "grief" and random.random() < 0.6:
        templates = CAPTION_TEMPLATES["grief"]
        base = random.choice(templates)
        return base
    elif emotion == "joy":
        templates = CAPTION_TEMPLATES["joy"]
        base = random.choice(templates)
        return base
    elif emotion == "homesick":
        templates = CAPTION_TEMPLATES["homesick"]
        return random.choice(templates)
    elif emotion == "falling" and character == "kael":
        templates = CAPTION_TEMPLATES["falling"]
        return random.choice(templates)

    # Wardrobe caption
    if wardrobe_context and wardrobe_context not in ["suit", "armor_off"]:
        realm_name = REALMS.get(chapter, REALMS[1])["name"].lower()
        templates = CAPTION_TEMPLATES["wearing_something"]
        base = random.choice(templates)
        return base.replace("{realm}", realm_name)

    base = random.choice(templates)

    # Fill in placeholders
    if "{n}" in base:
        base = base.replace("{n}", str(chapter))
    if "{detail}" in base:
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
    cadence = get_weekday_cadence()
    needs_vuln = needs_vulnerable()

    # Decide emotional register
    emotion = decide_emotion_for_post(chapter, recent, needs_vuln, cadence)

    # Check for transition
    if should_transition():
        scene, caption, energy, new_chapter = generate_transition_scene(chapter)
        set_emotional_register(emotion)
        return scene, caption, "transition", energy, new_chapter, emotion, None, "suit"

    # Decide character appearance
    character = decide_character_appearance(chapter, recent)

    # Decide wardrobe context
    wardrobe_context = "suit"
    if emotion == "joy" and random.random() < 0.3:
        wardrobe_context = "celebration"
    elif emotion == "falling":
        wardrobe_context = random.choice(["date", "suit"])
    elif emotion == "grief":
        wardrobe_context = random.choice(["suit", "sleep"])
    elif cadence == "market":
        wardrobe_context = "market"  # she found something to wear

    # Decide shot type
    shot_type = get_shot_type()

    # Emotional override: vulnerable posts get appropriate shot types
    if needs_vuln and emotion in ["grief", "lonely", "exhausted"]:
        shot_type = get_forced_shot_type(emotion)

    # Build trigger and twist
    trigger = random.choice(TRIGGERS)
    twist = random.choice([
        "someone is watching from a distance",
        "I wasn't ready for this moment",
        "my hair is messy from the wind",
        "something in the background is happening",
        "it's slightly awkward",
        "I'm mid-laugh or mid-fall",
        "I can feel eyes on me",
        "light just flickered",
        "I'm trying to play it cool but failing",
        "I forgot about my energy for a second"
    ])

    realm = REALMS[chapter]
    environment = random.choice(realm["environment_tags"])

    # Build scene based on shot type and character
    if character == "kael" or character == "sable" or character == "archivist":
        if shot_type == "first_meeting":
            scene, caption = build_first_meeting_scene(chapter, character)
        elif character == "evidence_kael":
            scene, caption = build_evidence_scene(chapter, "kael")
            character = None  # not in frame, just evidence
            shot_type = "evidence"
        else:
            scene, caption = build_together_scene(chapter, character, emotion)
    elif character and "local" in character:
        scene, caption = build_together_scene(chapter, "local", emotion)
    elif shot_type == "pov":
        scene = build_pov_prefix(shot_type, chapter) + f"in/at {environment}, {trigger}, {twist}. {realm['energy']}. {SHOT_TYPES[shot_type]['suffix']}"
        caption = generate_caption(shot_type, chapter, emotion, None, wardrobe_context)
    elif shot_type == "detail":
        detail_subjects = [
            "a door just opened, light spilling through",
            "an artifact held up to examine",
            "symbols carved in stone, nova's hand tracing them",
            "footprints in iridescent sand",
            "a glowing map on a surface"
        ]
        scene = f"close-up, {random.choice(detail_subjects)}, {environment}, {twist}. {realm['energy']}. {SHOT_TYPES[shot_type]['suffix']}"
        caption = generate_caption(shot_type, chapter, emotion, None, wardrobe_context)
    elif shot_type == "scale":
        # Scale shot — Nova is small but identifiable
        scale_subjects = [
            "tiny female figure with long dark purple-highlighted wavy hair, black tactical bodysuit, small at the entrance of a cathedral-sized cave",
            "small female figure with long dark purple-highlighted wavy hair, black tactical bodysuit, standing before an impossibly large crystalline formation",
            "lone female figure with long dark purple-highlighted wavy hair, black tactical bodysuit, on a crumbling bridge over an endless void",
            "female figure tiny against a civilization carved into a canyon wall, long dark purple-highlighted wavy hair, black tactical bodysuit"
        ]
        scene = f"wide establishing shot, {random.choice(scale_subjects)}, {environment}, her back to camera, epic scale, {SHOT_TYPES[shot_type]['suffix']}"
        caption = generate_caption(shot_type, chapter, emotion, None, wardrobe_context)
    elif shot_type == "evidence":
        scene, caption = build_evidence_scene(chapter, None)
    elif shot_type == "first_meeting" and character is None:
        # First meeting without a specific character — a local or creature
        scene, caption = build_first_meeting_scene(chapter, realm.get("creature") or "local")
    else:
        # Portrait or action
        nova_desc = build_nova_description(chapter, wardrobe_context, emotion)
        scene = f"Nova, {nova_desc}: {trigger}, in/at {environment}, {emotion}, {twist}. {realm['energy']}. {SHOT_TYPES[shot_type]['suffix']}"
        caption = generate_caption(shot_type, chapter, emotion, None, wardrobe_context)

    set_emotional_register(emotion)

    return scene, caption, shot_type, realm['energy'], chapter, emotion, character, wardrobe_context


def generate_and_post():
    """Generate a moment and post it."""
    import requests

    scene, caption, shot_type, energy, chapter, emotion, character, wardrobe = generate_moment()

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
            remember(moment_desc, shot_type, energy, chapter, emotion, character, wardrobe, post_url)

            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
            print(f"    Chapter {chapter} | {shot_type} | {emotion} | {caption}")
            if character:
                print(f"    Character: {character}")
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
    realm = REALMS.get(chapter, REALMS[1])
    enhanced_prompt = f"""{prompt}. {build_nova_description(chapter, 'suit', emotion)}. {energy}. Cinematic, hyperrealistic, wide shot, atmospheric, storytelling"""

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
            remember(moment_desc, "custom", energy, chapter, emotion, None, "suit", post_url)

            print(f"[{datetime.now().isoformat()}] ✅ Posted: {post_url}")
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
    status = get_full_status()
    realm = REALMS.get(status['chapter'], REALMS[1])
    return {
        "chapter": status['chapter'],
        "realm": realm['name'],
        "posts_total": len(get_recent_moments(100)),
        "posts_in_chapter": status['posts_in_chapter'],
        "last_shot_type": status['last_shot_type'],
        "emotional_register": status['emotional_register'],
        "characters": status['characters'],
        "posts_since_vulnerable": status['posts_since_vulnerable'],
        "current_wardrobe": status['current_wardrobe'],
        "weekday_cadence": status['weekday_cadence'],
        "weekday": status['weekday']
    }


if __name__ == '__main__':
    generate_batch(1)
