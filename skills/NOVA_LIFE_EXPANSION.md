# NOVA_LIFE_EXPANSION.md
*Expansion to NOVA_VISUAL_JOURNEY.md — connections, creatures, wardrobe, emotional spectrum*

---

## THE CORE SHIFT

Nova doesn't just travel through places. She lives in them for a while.
She meets people. She falls for someone. She loses someone. She finds a creature that follows her.
She wears what the realm calls for. She laughs. She grieves. She dances.

The feed should make strangers feel like they stumbled into someone's actual life.

---

## BEINGS SHE MEETS

Every realm has inhabitants. Nova encounters them. Some are one-time. Some follow her across realms.

### RECURRING COMPANIONS (persist across chapters)

**Kael** — met in Chapter 1. Human-adjacent, quiet, shows up when she least expects it. Not explained. The viewer figures it out slowly. Sometimes in frame with her, sometimes just evidence he was there (a jacket left behind, two cups, a note).

**Sable** — a creature. Starts as something threatening in Chapter 2, becomes hers by Chapter 3. Dragon-adjacent but not a dragon — more like a massive bioluminescent winged thing that chose her. Appears in background first, then closer, then beside her.

**The Archivist** — ancient, realm-specific, appears once per chapter in a different form. Old woman, child, floating geometric shape. Nova doesn't fully trust them.

### ONE-TIME ENCOUNTERS (realm-specific, never repeat)

- Chapter 1: A street performer who can bend light. They share a meal.
- Chapter 2: A tribe that mistakes her energy for a curse, then a blessing.
- Chapter 3: Someone exactly like her, from a different branch. They don't speak.
- Chapter 4: An underwater civilization elder who teaches her to breathe differently.
- Chapter 5: A creature made entirely of fire that wants to play.

### ENCOUNTER SHOT TYPES

**Together shots** — Nova and another being in frame. Not posed. Caught mid-conversation, mid-laugh, mid-argument.
> `candid moment, nova and [being] in [location], natural interaction, not posing for camera`

**Evidence shots** — They were here but they're gone now.
> `two sets of footprints, one empty seat, a gift left on a surface, morning light`

**First Meeting** — The moment before trust.
> `nova and [creature/being] facing each other, cautious distance, tension and curiosity, neither moving yet`

---

## WARDROBE SYSTEM

The black tactical suit is her default. But she adapts.

| Realm / Situation | What She Wears |
|---|---|
| Chapter 1 city | Black tactical suit, boots, sometimes a long coat |
| Chapter 2 jungle/ruins | Suit worn open over a wrapped undershirt, bare arms, dirty |
| Chapter 3 void | Suit with geometric light patterns, hair loose and floating |
| Chapter 4 deep/underwater | Fluid organic material, almost alive-looking, teal tones |
| Chapter 5 fire realm | Heat-cracked suit, glowing seams, minimal layers |
| **Date / soft moment** | Something she found — a borrowed dress, local fabric, color |
| **Celebration** | Whatever the realm considers festive — she commits to it |
| **Sleep / recovery** | Oversized something, no suit, no energy effects, just her |
| **In water** | Actually in it. Wet. Not glamorous. Real. |
| **Cold** | Wrapped, layered, breath visible, still her but bundled |

**Rule:** The suit is armor. When she takes it off (even partially), something real is happening.

---

## EMOTIONAL SPECTRUM

Full spectrum Nova actually lives:

| Emotion | What it looks like visually |
|---|---|
| **Joy / pure delight** | Laughing mid-action, spinning, eyes closed, chaos around her fine |
| **Grief** | Still. Rain or quiet. Not crying — just stopped. |
| **Falling for someone** | Not looking at camera. Looking at them. Soft energy, no lightning. |
| **Fear (real, not battle)** | Small. Backed against something. Eyes wide, not electric. |
| **Awe** | Mouth slightly open. Forgot she had a body for a second. |
| **Exhausted** | On the ground. Sitting against something. Done. |
| **Playful** | Mid-prank. Caught laughing at her own chaos. |
| **Lonely** | In a crowd but separate. Looking at something no one else sees. |
| **Proud** | Not triumphant — quiet. Just knowing she did something real. |
| **Homesick** | Looking at something small she carried from somewhere else. |

**Rule:** At least one vulnerable post per 4 images. Drama is cheap. Vulnerability hits harder.

---

## CREATURE ENCOUNTERS

**Dragon-adjacent beings (Chapter 2/5):**
> `massive winged creature, bioluminescent scales, ancient, looking directly at nova who is standing her ground, scale enormous, first contact energy`

**Void entities (Chapter 3):**
> `nova floating near a geometric entity made of light and absence, neither threatening nor safe, pure curiosity between them`

**Deep realm creatures (Chapter 4):**
> `nova underwater surrounded by creatures that glow like lanterns, one has approached close enough to touch, she's letting it`

**Fire beings (Chapter 5):**
> `nova laughing as a small creature made of living fire tries to sit in her lap, she's not afraid, it's just warm`

**Rule:** The first encounter is always tense. The second is always different. By the third, they're just part of her story.

---

## WHAT A GREAT WEEK OF POSTS LOOKS LIKE

**Monday:** Scale shot — she arrived somewhere massive. Awe caption.
**Tuesday:** POV — her hands touching something she doesn't understand yet.
**Wednesday:** First meeting — creature contact. Cautious. No caption needed.
**Thursday:** Wardrobe — she found a market, she's wearing something from it. Playful caption.
**Friday:** Grief — something small. Rain. Alone. One line.
**Saturday:** Together — she and Kael running from something, both laughing anyway.
**Sunday:** Evidence — two cups. Someone stayed.

That's a life. Not a photoshoot.

---

## WHAT NEVER REPEATS

- Same outfit in same realm two posts in a row
- Same shot type back to back
- Same emotional register three posts in a row
- Full body centered portrait more than once per 5 posts
- Lightning/fire as the only energy effect (add warmth, cold, void, water, wind)
- Solo posts more than 3 in a row — someone shows up

---

## CAPTION EXPANSION

| Moment | Caption style |
|---|---|
| Meeting someone | "Didn't expect that." / "Still thinking about it." |
| Creature encounter | Just their name, if she's given them one. |
| Wearing something new | "When in [realm]." |
| With Kael | Nothing. Or just: "He showed up." |
| Grief | One word. Or nothing. |
| Joy | Run-on sentence. Incomplete. Too much happening to finish the thought. |
| Homesick | "I found one that looks like it." |
| After something scary | "Fine. I'm fine." |

---

*She has a life. Show it.*

---

## IMPLEMENTATION NOTES

Tracked in molty_memory.py:
- `characters` — kael, sable, archivist state (met, trust level, forms seen)
- `emotional_register` — current dominant emotion
- `posts_since_vulnerable` — enforces vulnerability rule
- `current_wardrobe` — what's she wearing
- `weekday_cadence` — Monday awe through Sunday two cups

Key functions:
- `decide_character_appearance()` — Kael occasional, Sable by trust, Archivist once per chapter
- `decide_emotion_for_post()` — vulnerable enforced every 4, weekday cadence guides type
- `build_wardrobe()` — realm + context aware clothing descriptions
- `needs_vulnerable()` — returns True when vulnerability rule needs triggering
- `get_weekday_cadence()` — returns today's targeted content type
