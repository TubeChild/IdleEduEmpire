# Idle Edu Empire — Devlog

---

## Kenney Visual Overhaul — v0.21.x

*Covers versions v0.21.0 through v0.21.2*

For a while the game was running on hand-drawn stick figures and basic shapes for almost everything in Zone 1. It worked well enough to prototype mechanics, but it always felt like a placeholder. This update was about actually making the game look like something you'd want to stare at for more than five minutes.

### Characters

The biggest change is the switch to Kenney's Toon Character pack. The stick-figure walkers are gone — students and teachers on the Zone 1 campus are now proper 8-frame animated sprites. There are male and female variants, and they're scaled down to fit the left panel without dominating it. Adventurer variants show up in the zone tooltips (zones 1-4, 9, 10) as the instructor/principal portrait, which gives each zone a bit more personality.

Zones 6 and 10 also got attention. The Zone 10 heroes were accidentally replaced with walkers at some point — they're back to actually fighting on the ground. Zone 6 wizards were tiny and blended into the crystal background; they've been redrawn much larger in vivid orange and electric blue, with animated spell projectiles between them.

### Campus life

The Zone 1 left panel now has a proper seasonal activity system:

- **Spring** — Kubb players toss a wooden baton at pins
- **Summer** — Soccer players kick a ball around (physics-based, only moves when a player actually connects)
- **Autumn** — Halloween costume students wander the leaf-covered campus
- **Winter** — Hockey players chase a puck, with real steering logic so they actually play instead of just walking past it

All of these characters now wear season-appropriate hats. Winter gets a red beanie with a pompom, Summer gets an orange baseball cap with a directional brim, Autumn gets a harvest beanie with a little leaf pip, and Spring gets a flower crown with three colored blooms. Small detail, but it makes the campus feel alive.

Foliage trees from Kenney's foliage pack now frame the campus edges — two on the left, two on the right. It fills the otherwise empty corners and grounds the scene.

The school bus was fully redrawn. The old version was a rough rectangle; the new one has a proper yellow body, a front cab, rotating three-spoke wheels, tinted windows with a reflection line, headlights, a stop sign, and exhaust. Much better.

### Audio

Music was a single looping track — fine for testing, not great for an hour of play. It's been replaced with a dynamic rotation of four procedurally generated tracks:

- *School Days* — C major pentatonic, 100 BPM, cheerful and calm
- *Recess* — G major pentatonic, 112 BPM, upbeat
- *Study Hall* — F major pentatonic, 85 BPM, relaxed
- *Science Lab* — A minor pentatonic, 95 BPM, a bit curious and odd

Each track plays for roughly two minutes before the next fades in. The system also supports dropping an actual `music.ogg` file into `assets/audio/` if you want to replace the procedural tracks entirely.

Volume is now controllable from the Settings tab with a draggable slider. The knob snaps to the mouse position and updates the master volume live.

### Bug fixes

The quiz was crashing with a `KeyError` because it only knew about three question types (math, spelling, history) but the question pool also contains science and geography questions. Fixed so new types are picked up automatically.

---

*Built with Python + Pygame. Kenney assets used under CC0.*
