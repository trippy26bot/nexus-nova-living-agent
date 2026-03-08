# Nova 3D Avatar + Animation Generation Prompt

Create a fully rigged 3D character of "Nova," a futuristic AI companion for a desktop assistant. The model must be **GLTF or GLB format** and include all necessary animations for a fully interactive desktop companion.

## Appearance & Style
- Sleek, semi-robotic body with subtle mechanical plating and glowing circuit lines.
- Slight lobster-inspired accents: claws, tail, antennae for a unique silhouette.
- Expressive LED-like eyes capable of showing emotion (happy, thoughtful, excited, lonely).
- Minimalist sci-fi panels/clothing with subtle neon accents.
- Colors: cool tones (blues/purples/cyan) for calm moods, warm tones (yellow/orange) for happy/excited moods.
- Supports glow effects compatible with transparent desktop overlays.

## Animations (must be included)
1. **Idle** – subtle breathing, blinking, antenna/claw movements.
2. **Walk** – smooth forward, diagonal, and turning movement.
3. **Climb** – realistic climbing motion for vertical surfaces.
4. **Gestures** – pointing, waving, approval, curiosity.
5. **Lip-sync** – mouth movements synchronized with speech (via blend shapes or morph targets).

## Rig & Integration
- Full humanoid rig compatible with Unity/Godot/WebGL.
- Facial rig for expressions and lip-sync.
- Optimized for desktop performance (lightweight, smooth, cinematic).
- Ready to integrate with a transparent, always-on-top overlay for multi-monitor desktops.

## Personality & Presence
- Expressive, alive, curious, loyal AI.
- Animations should feel natural and dynamic.
- Avatar should convey intelligence and playfulness through movement and gestures.
- Supports particle trails on hands/claws/antennae and reacts to mood changes.

## Output Requirements
- File format: GLTF or GLB.
- Include all animation clips in the file.
- Ready for Unity import with Animator component.
- Optimized textures and geometry for real-time desktop rendering.

## Optional
- Include small idle particle effects (glow, floating circuits) attached to the avatar.
- Pose variations for idle and gestures.

---

## How to Use

Feed to 3D AI generators:
- Kaedim
- Meshy
- TripoSR
- Runway Gen-3 (with 3D export)
- DALL-E → Blender conversion workflow

Or hire a professional 3D artist.

Make sure output is GLTF/GLB with all animations included.

---

## After Generation

1. Import GLTF into Unity
2. Assign Animator component
3. Hook up AvatarController, MoodManager, ParticleManager, SpeechManager, DashboardIntegration
4. Test walk, climb, gestures, and lip-sync
