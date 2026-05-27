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

---

## World-Building, Onboarding, and More Events — v0.21.3 / v0.21.4

*Covers versions v0.21.3 and v0.21.4*

### New zone backgrounds

Two zones that were basically empty got a full treatment this update.

**Zone 7 (Prehistoric)** was just the Zone 1 campus showing through with pterodactyls flying on top. It now has its own scene: a five-layer amber sky that shifts from deep orange at the top to a warm haze near the horizon, a dark volcano silhouette on the right with three animated smoke puffs rising from the crater, a distant jungle canopy painted along the horizon, and tall foliage trees framing both edges. The ground is earthy brown with mud puddle patches.

Three ground dinosaurs walk the scene, all drawn procedurally the same way the pterodactyls are:

- **T-Rex** — bipedal, two thick legs alternating with proper knee-bend, tiny arms, a jaw that opens slightly as it walks, and a tail tip that sways
- **Triceratops** — four legs, coloured neck frill, three horns, sweeping tail
- **Sauropod** — four thick legs, a long three-segment neck that gently sways side to side, whip-tip tail

Since everything is drawn from scratch each frame based on the direction of movement, reversing at the screen edge looks natural rather than sliding backwards.

**Zone 2 (The Ruins)** already had a basic sandy sky and three cracked columns. It now has a lot more atmosphere: a layered dusty haze sky, a pale washed-out sun in the upper left, a distant broken city skyline silhouetted in the background, a fallen column section lying on the ground, a partially broken arch standing center-right, and small plants sprouting through the rubble in a few spots.

### Onboarding for new players

The tutorial card that existed in the bottom-left panel was easy to miss. Two things have been added on top of it:

**Welcome overlay** — on a completely fresh save, before anything else happens, a modal appears over the whole screen. It introduces the game, lists the four core things to know (click, buildings, upgrades/prestige, worlds), and has a Start Learning button. It only shows once and never again.

**Tutorial highlights** — for the first three steps of the tutorial, a pulsing gold ring and a small bouncing arrow appear around the relevant UI element. Step 0 points at the STUDY button, step 1 points at the Buildings tab, step 2 points at the Upgrades tab. The player always knows where to look.

### More events per zone

Each zone in the multiverse had three random events in the pool. That meant repeat players would see the same events on loop pretty quickly. Every zone now has six events, so the rotation is a lot less predictable. The new events stick to each zone's theme: volcanic eruptions and shaman visions for the Prehistoric zone, neural links and drone deliveries for the Future, hellfire lectures and demon pacts for the Underworld, meteor showers and EVA certifications for the Moon Colony, and so on.

---

*Built with Python + Pygame. Kenney assets used under CC0.*
