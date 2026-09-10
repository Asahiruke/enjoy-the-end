# Enjoy the End — Update Log

## 2026-09-10 — Prototype 0.18: title placeholder, denser traits & font scaling

### Title
- Replaced the visible “末日室内生存” title with a blank placeholder while preserving its layout space.
- Browser title now uses Enjoy the End instead of the temporary Chinese title.

### Character traits
- Reduced the initial shared creation-point pool from 30 to 12.
- Trait cards use a denser two-column layout on wider screens and fall back to one column on narrow phones.
- Added negative traits for light / medium / severe myopia, with only one myopia tier selectable at a time.
- Added alcohol, nicotine, and caffeine addiction traits as negative traits that return creation points.
- New negative traits are represented as tags so later survival, withdrawal, perception and item-use systems can read them.

### Settings
- Added a font-size slider to Settings, ranging from 80% to 140%.
- Font size is remembered locally and is reapplied when starting or loading a game.

## 2026-09-10 — Prototype 0.17: persistent sofa resting

- Sitting on a sofa is now a 30-minute resting action.
- The player remains seated after the action finishes until explicitly choosing to leave the sofa.
- The “呼唤：NPC名” button is created only after the player sits down.
- Removed periodic polling for sofa-state/button detection.
- Sitting down no longer forces an immediate companion response; NPC movement remains governed by reaction events and hourly autonomy.
- Leaving the sofa immediately clears the seated state, call button, and lap-related companion state.

## 2026-09-10 — Prototype 0.16: generic hourly NPC autonomy

### NPC autonomous tick
- Added a generic NPC autonomy framework that evaluates autonomous behaviour once per crossed in-game hour.
- Immediate reactions such as calling an NPC or standing up while an animal is on the player's lap remain event-driven instead of waiting for the hourly tick.
- Long time skips are processed hour-by-hour with a safety cap to avoid runaway processing.

### Furniture / scene interaction architecture
- Furniture interactions now begin with an NPC-type gate: person / animal.
- Rules then narrow to a subtype or species such as human, cat, dog, or bird.
- Scene rules currently cover sofa, cabinet tops, windows, beds, and open floor space.
- The same scene can expose different actions to humans and animals instead of being hard-coded only for cats.

### Personality domains
- Human and animal personality data are now separated.
- Fixed human NPCs can define stable human personality tags such as quiet, sociable, orderly, cautious, or restless.
- Animals use a separate personality pool such as curious, independent, timid, energetic, sleepy, playful, affectionate, alert, or calm.
- Randomly encountered animals can roll personalities from the animal domain, while custom companions remain compatible with hand-authored personality data.

### Behaviour weighting
- The hourly decision model prefers keeping the current action, then local activity, room movement, approaching the player, or a special behaviour.
- Personality modifies these weights.
- Sleep/rest actions can reserve more than one hour so NPCs do not appear to teleport between activities every tick.
- Autonomous activity updates world/entity state without automatically flooding the recent-log panel.

## 2026-09-10 — Prototype 0.14: cat customization & sofa interactions

### Cat customization
- Expanded the companion cat creator without using real-world breed names.
- Added fur length, base coat color, coat pattern, white-area distribution, facial markings, eye color, body shape, tail appearance, ear details, nose color, and paw-pad color.
- Coat patterns now include cat-like options such as tabby, fine-striped tabby, classic swirls, spotted markings, tortoiseshell-like markings, tricolor markings, and shaded coats.
- Companion preview text is generated from the selected visual traits.

### Cat room life
- Added simple room-life text for the companion cat, including wandering around the room, inspecting cabinets, grooming, walking past the player, and using a sofa when one is available.
- Companion cats remain part of the NPC/entity framework rather than a separate decorative pet system.

### Sofa interaction
- Rooms with a sofa can now offer “sit on the sofa”.
- While sitting, the player can choose to remain seated for 10 minutes or stand up.
- A companion cat in the same room may probabilistically sit beside the player or climb onto the player's lap.
- If the player remains seated, a cat on the lap may eventually fall asleep.
- When the cat is within reach, additional interactions become available: pet the forehead, scratch the chin, stroke the back, or touch the paws.

### Character creation
- The hidden body-feature controls remain removed from the visible character creator.
- Character appearance continues to use “你看起来像：男性化 / 中性 / 女性化”.
- Attribute and trait creation from Prototype 0.13 remains included.

### Deployment repair
- Removed the fragile build-time patch script from deployment.
- GitHub Pages now rebuilds the final Prototype 0.14 HTML directly from the stored compressed source chunks.
- The build verifies that dist/index.html exists and is non-empty before deployment.

## 2026-09-09 — Prototype 0.12: character wording & mobile focus

- Reworked outward appearance wording and compact mobile layout.
- Mobile gameplay prioritizes room description, character status, and recent log, while larger systems sit behind dedicated views.
