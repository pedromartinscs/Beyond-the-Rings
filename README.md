# Beyond the Rings

A futuristic real-time strategy game set on Titan, Saturn's moon.

The current codebase focuses on a solid single-player runtime built with **Python** and **Pygame**, with the project architecture refactored to prioritize readability, separation of responsibilities, and safer future expansion.

---

## Project overview

In **Beyond the Rings**, rival factions fight for control of strategic regions on Titan in order to secure valuable resources such as:

- uranium
- iron
- titanium
- natural gas
- water

The gameplay direction is inspired by classic RTS titles, with base construction, resource gathering, unit production, map control, and combat.

The current implementation is centered on a maintainable runtime architecture, so new features can be added with less risk than before.

---

## Current architectural direction

The project was refactored from a more monolithic structure into a **composed runtime**.

The most important rule is:

- **`Game` acts as the orchestrator**
- specialized collaborators own specific domains
- UI responsibilities are coordinated separately from world/gameplay responsibilities

At a high level, the runtime now follows this model:

```text
Game
├── GameWorld
├── GameCamera
├── GameMinimap
├── GameSelection
├── GameCombat
├── GameEconomy
├── GameInterface
└── GameObjectFactory
```

This means the main game screen no longer tries to own every gameplay rule directly.  
Instead, it coordinates dedicated systems that each have a clearer purpose.

---

## Main runtime flow

The central game loop is intentionally easy to read.

`Game` is designed around three main lifecycle methods:

- `handle_events(...)`
- `update()`
- `render()`

This keeps the top-level flow readable and makes it easier to reason about the frame lifecycle.

### Lifecycle responsibilities

#### `handle_events(...)`
Receives input events and routes them to the correct runtime/UI systems.

#### `update()`
Advances the simulation:
- economy
- camera
- combat
- selection-related state
- interface-related updates

#### `render()`
Draws the current frame:
- world
- selected object overlays
- combat effects
- minimap
- interface panels
- credits/UI details

---

## Core runtime systems

### `Game`
The orchestrator of the main gameplay screen.

It should remain focused on:
- high-level flow
- coordination between systems
- frame lifecycle
- keeping the gameplay screen readable

`Game` should not become a large dumping ground for unrelated gameplay logic again.

---

### `GameWorld`
Owns the state of the playable world.

Typical responsibilities:
- map loading
- tile data
- world dimensions
- map surface/cache
- world objects
- spatial grid
- object lookup helpers
- destroyed object cleanup
- resource respawn logic when applicable

This is the closest thing to the runtime's "world state owner".

---

### `GameCamera`
Owns the gameplay camera.

Typical responsibilities:
- camera position
- scroll movement
- world centering
- visible region updates
- world/screen related camera calculations

The minimap is intentionally separate from camera logic.

---

### `GameMinimap`
Owns the minimap as a game-specific interface element.

Typical responsibilities:
- minimap rendering
- viewport rectangle rendering
- click/drag interaction
- minimap-to-world translation

Although it is visual, it is tightly coupled to the current match and therefore belongs to the game runtime layer rather than generic UI.

---

### `GameSelection`
Owns object selection.

Typical responsibilities:
- current selected object
- selecting objects by screen/world position
- clearing selection
- selection synchronization with the interface
- selection overlay rendering

Anything specifically about "what is selected" should live here rather than being scattered across the runtime.

---

### `GameCombat`
Owns combat-related runtime behavior.

Typical responsibilities:
- active attacks
- range checks
- attack progression
- projectile spawning
- projectile updates
- impact explosions
- combat-oriented effects
- builder creation flow tied to gameplay actions

At the current stage of the project, missiles and impact effects are treated as part of combat rather than as a fully separate global effects system.

That decision can be revisited later if the project gains many non-combat visual effects.

---

### `GameEconomy`
Owns credit/resource-like runtime economy behavior.

Typical responsibilities:
- current credit amount
- periodic credit generation
- economy queries such as affordability checks
- economy-related UI rendering

This keeps monetary logic out of unrelated systems.

---

### `GameInterface`
Coordinates the UI that is specific to the gameplay screen.

Typical responsibilities:
- bottom panel coordination
- side/vertical panel coordination
- selected object card integration
- targeting-related UI coordination
- routing interface clicks
- rendering the gameplay HUD/panels

This is intentionally different from generic UI widgets.  
It is a game-screen-specific coordinator.

---

### `GameObjectFactory`
Centralizes creation of runtime object dictionaries.

Typical responsibilities:
- build object data consistently
- create map-loaded objects
- create spawned objects
- create builder-related objects
- recreate/respawn resource objects when necessary

This reduces duplication and makes object creation safer and more consistent.

---

## UI structure

The project now distinguishes between:

### 1. Game-specific interface coordination
Handled by systems in `Core/Game`, especially `GameInterface` and `GameMinimap`.

### 2. Reusable UI components
Handled in `Core/UI`.

This distinction matters because not every visual element is generic UI.

For example:
- a generic button belongs to reusable UI
- a selected-object RTS action panel is game-specific UI
- the minimap is UI, but it is deeply tied to the current match and therefore treated as part of the game runtime

---

## Horizontal panel split

The bottom gameplay panel was separated internally by responsibility so it is easier to understand and maintain.

Instead of one large panel file owning everything directly, the panel logic is now split into smaller parts such as:

- action grid
- selection card
- status bars

This makes the code more readable without changing the visible behavior of the game.

---

## Runtime data model

The current runtime still uses a **dict-based object model** for world entities.

That means units, buildings, and resources are primarily represented as dictionaries with fields such as position, type, health, metadata-derived properties, animation references, and identifiers.

This is intentional for now.

The refactor focused on:
- architecture
- organization
- safety
- readability

It did **not** force a risky migration of the entire runtime into a new entity class hierarchy.

That kind of change can be reconsidered later only if it becomes clearly worth it.

---

## Directory intent

Conceptually, the project is moving toward this responsibility split:

```text
Core/
├── Game/   -> gameplay runtime systems specific to an active match
├── UI/     -> reusable UI pieces and panel subcomponents
├── AI/     -> future AI-related logic
```

### Important note about `Editor`
The `Editor` folder is intentionally treated as a separate tool and is not part of the gameplay runtime refactor.

When working on runtime architecture, the editor should be considered out of scope unless the task is specifically about the map editor.

---

## Why this refactor matters

This architecture makes the project easier to extend safely.

Examples of future work that should now be easier to implement:
- production queues
- new weapon types such as lasers
- hotkeys / keyboard shortcuts
- improved targeting
- better interface feedback
- additional factions and unit types
- AI systems
- fog of war
- new map mechanics

The main goal of the refactor was not to make the code "fancy".  
It was to make the codebase easier to reason about and harder to break accidentally.

---

## Development guidelines

### Prefer composition over growing `Game`
New gameplay systems should usually be introduced as dedicated collaborators rather than expanding `Game` into another monolith.

### Keep `Game` readable
`Game` should remain the place where a reader can quickly understand the frame flow.

### Put logic where it belongs
Examples:
- selection logic in selection
- combat logic in combat
- world ownership in world
- screen-specific HUD coordination in interface

### Avoid mixing gameplay rules into generic UI
Reusable UI components should stay lightweight and general whenever possible.

### Refactor only when needed
The architecture is now in a good enough state to support feature work.  
Further large refactors should be driven by real needs, not by refactoring for its own sake.

---

## Running the project

Typical flow:

1. Create and activate a Python virtual environment
2. Install dependencies from `requirements.txt`
3. Run the game entry point

Example:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python beyond_the_rings.py
```

Depending on your environment, activation commands may vary.

---

## Current status

The codebase is now in a much healthier state for feature development.

That means the recommended path forward is:

- stop large-scale architectural refactoring for now
- implement gameplay features from the backlog
- only refactor locally when a new feature reveals a real design need

This keeps momentum high without sacrificing maintainability.

---

## Suggested next mindset for development

Treat the current architecture as a stable baseline.

From here, development can focus on:
- new gameplay features
- quality-of-life improvements
- content expansion
- controlled, need-driven refactors only when a concrete feature justifies them

---

## Summary

The current runtime architecture is centered on a simple principle:

**`Game` coordinates the match, while specialized systems own the details.**

That structure should make Beyond the Rings significantly easier to grow without losing control of the codebase.
