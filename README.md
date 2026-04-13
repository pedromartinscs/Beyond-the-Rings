# Beyond the Rings

> ⚙️ Developed entirely by Pedro Martins Costa de Souza — game programmer with experience in .NET, Python, AWS, Docker, and game systems.  
> 🚀 Currently open to remote opportunities in game development (full-time or freelance).  
> 📫 Contact: pedro@nancode.com.br | [LinkedIn](https://www.linkedin.com/in/pedromartinscosta/) | [Portfolio](https://github.com/pedromartinscs)

**Beyond the Rings** is a futuristic real-time strategy game set on Titan, one of Saturn's moons. Players control competing factions, gather strategic resources such as uranium, iron, titanium, natural gas, and water, expand their bases, and fight for dominance across the map.

This project is being developed in **Python** with **Pygame**, and serves both as an active game project and as a portfolio piece that showcases game architecture, gameplay systems, UI coordination, rendering flow, and RTS-style runtime organization.

---

## Features

- **Built with Python and Pygame**  
  The project showcases real-time gameplay systems, world rendering, UI flow, combat logic, resource generation, and game-state coordination.

- **Solo-developed**  
  This is a solo project, reflecting end-to-end ownership of architecture, gameplay logic, code organization, and technical decision-making.

- **Multiple factions**  
  The long-term direction includes playable factions such as the United States, China, Russia, Japan, India, the European Union, Brazil, South Africa, and unlockable factions like FrontierX, BioTech, Resistência Espacial, and ShadowAI.

- **Resource gathering and expansion**  
  The game is built around map control, strategic expansion, and resource-oriented growth.

- **Strategic combat**  
  Units and structures can engage in combat through attacks, projectiles, and faction-specific gameplay possibilities.

- **Open-ended future growth**  
  The architecture now supports future systems such as production queues, new weapons, improved UI feedback, AI, hotkeys, and more.

- **Open source direction**  
  The project is intended to remain open and extensible as development continues.

---

## Project overview

The core idea of **Beyond the Rings** is to deliver a futuristic RTS experience inspired by classic strategy games, but with a setting centered on Titan and a growing set of sci-fi factions and mechanics.

The current version emphasizes:

- a maintainable runtime architecture
- clear separation of responsibilities
- safer iteration for new gameplay features
- a more readable main game flow

This makes the codebase much better prepared for continued feature development than it was before the refactor.

---

## Current architectural direction

The project was refactored from a more monolithic structure into a **composed runtime**.

The main principle is:

- **`Game` acts as the orchestrator**
- specialized collaborators own specific domains
- UI-specific coordination is separated from world/gameplay responsibilities
- reusable UI concerns remain distinct from game-screen-specific HUD logic

At a high level, the runtime now follows this structure:

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

This means the main gameplay screen no longer tries to own every responsibility directly.  
Instead, it coordinates collaborators that each own a clearer slice of the runtime.

---

## Main runtime flow

The gameplay screen is intentionally organized around three main lifecycle methods:

- `handle_events(...)`
- `update()`
- `render()`

This keeps the top-level loop easier to read, easier to debug, and safer to extend.

### `handle_events(...)`
Routes user input to the correct systems, such as:
- gameplay interaction
- selection
- minimap interaction
- UI panels
- targeting flow

### `update()`
Advances the simulation, such as:
- economy progression
- camera movement
- combat state
- selection synchronization
- interface updates

### `render()`
Draws the current frame, such as:
- visible world
- selected object overlays
- projectiles and impact effects
- minimap
- gameplay interface
- credits and selected-object information

---

## Core runtime systems

### `Game`
The orchestrator of the active match.

Its role is to keep the frame flow readable and coordinate the runtime without becoming a monolithic owner of every rule again.

---

### `GameWorld`
Owns the playable world state.

Typical responsibilities:
- map loading
- tile data
- map dimensions
- world objects
- spatial grid
- world lookup helpers
- destroyed-object cleanup
- resource respawn behavior when needed
- world rendering

---

### `GameCamera`
Owns camera behavior.

Typical responsibilities:
- camera position
- scroll movement
- centering on world positions
- visible region calculations
- camera-related screen/world conversions

---

### `GameMinimap`
Owns the minimap as a game-specific interface element.

Typical responsibilities:
- minimap rendering
- viewport rectangle rendering
- click and drag interaction
- minimap-to-world translation

Although visual, it is tightly coupled to the current match and therefore belongs to the gameplay runtime layer rather than generic UI.

---

### `GameSelection`
Owns object selection.

Typical responsibilities:
- tracking the currently selected object
- selecting by position
- clearing selection
- synchronizing selection with the interface
- rendering selection overlays

---

### `GameCombat`
Owns combat behavior.

Typical responsibilities:
- active attacks
- range checks
- attack progression
- projectiles
- projectile smoke
- impact explosions
- builder creation flow tied to gameplay actions

At the current stage of development, missiles and impact effects are treated as part of combat rather than a separate global effects system.

---

### `GameEconomy`
Owns credit-related economy flow.

Typical responsibilities:
- current credits
- periodic credit generation
- affordability checks
- economy-related interface rendering

---

### `GameInterface`
Coordinates the UI that is specific to the gameplay screen.

Typical responsibilities:
- bottom panel coordination
- side/vertical panel coordination
- selected object card integration
- targeting-related interface coordination
- interface click routing
- gameplay HUD rendering

This is intentionally different from generic reusable UI widgets.

---

### `GameObjectFactory`
Centralizes object creation.

Typical responsibilities:
- creating map-loaded objects
- creating spawned objects
- builder-related creation
- resource recreation/respawn when needed
- keeping object dictionary creation consistent

---

## UI structure

The current direction distinguishes between two things:

### 1. Game-specific interface coordination
Handled in `Core/Game`, especially by:
- `GameInterface`
- `GameMinimap`

### 2. Reusable UI components
Handled in `Core/UI`.

This distinction matters because not every visual element is generic UI.

Examples:
- a generic button belongs to reusable UI
- a gameplay action panel is game-specific UI
- the minimap is interface, but it is deeply tied to the current match and therefore treated as part of the game runtime

---

## Horizontal panel split

The lower gameplay panel was refactored internally by responsibility.

Instead of one large panel file owning everything directly, the bottom panel now relies on smaller pieces such as:

- action grid
- selection card
- status bars

This preserved the visible behavior while improving code organization and readability.

---

## Runtime data model

The current runtime still uses a **dict-based object model** for most world entities.

That means units, buildings, and resources are primarily represented by dictionaries containing information such as:
- position
- type
- health
- identifiers
- animation references
- metadata-derived properties

This was kept intentionally.

The refactor focused on:
- architecture
- readability
- separation of responsibilities
- safer expansion

It did **not** force a risky migration to a full entity class hierarchy.

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
The `Editor` folder is intentionally treated as a separate tool and is outside the scope of the gameplay runtime refactor.

---

## Installation

### Prerequisites

Before running the game, make sure you have:

- Python 3.x
- Pygame
- any additional dependencies listed in `requirements.txt`, if present in your current branch/version

### Install dependencies

A typical setup flow is:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

If your branch does not yet rely on `requirements.txt`, you can install Pygame directly:

```bash
pip install pygame
```

### Running the game

From the project root, run:

```bash
python beyond_the_rings.py
```

If your local entry point differs in a specific branch, use that branch's main launcher accordingly.

---

## Gameplay

### Objective

The primary goal is to eliminate enemy structures while managing resources, expanding your base, and building the military strength needed to dominate the map.

### Core loop

1. **Select a faction**
2. **Explore and secure territory**
3. **Gather resources**
4. **Construct structures**
5. **Create units and expand**
6. **Engage in combat**
7. **Destroy enemy infrastructure and win the match**

---

## Why this refactor matters

This architecture makes the project easier to extend safely.

Examples of future work that should now be easier to implement:
- production queues
- additional weapon types such as lasers
- hotkeys and keyboard shortcuts
- improved targeting
- richer feedback and HUD behavior
- new factions and units
- AI systems
- fog of war
- more advanced map mechanics

The goal of the refactor was not to make the codebase look clever.  
It was to make it easier to reason about, safer to change, and more practical for continued development.

---

## Development guidelines

### Prefer composition over regrowing a monolith
New gameplay systems should usually be introduced as dedicated collaborators rather than pushed directly into `Game`.

### Keep `Game` readable
`Game` should remain the place where a reader can quickly understand the match lifecycle.

### Put logic where it belongs
Examples:
- selection logic in selection
- combat logic in combat
- world ownership in world
- screen-specific HUD coordination in interface

### Avoid mixing gameplay rules into generic UI
Reusable UI should stay lightweight and general whenever possible.

### Refactor when a feature justifies it
The architecture is now in a healthy enough state that feature development should lead, and refactors should happen only when real needs appear.

---

## Current status

The project is now in a much stronger position for feature development than it was before the architecture refactor.

The recommended path forward is:

- focus on gameplay features from the backlog
- improve quality-of-life systems
- expand content
- refactor locally only when a concrete feature justifies it

---

## Contributing

Contributions are welcome.

If you would like to contribute to **Beyond the Rings**, a good default flow is:

1. Fork the repository
2. Create a branch for your change
3. Implement and test your update
4. Commit with a clear message
5. Push your branch
6. Open a pull request

Please try to keep contributions aligned with the current architectural direction and coding style.

---

## License

**Beyond the Rings** is open-source and released under the [MIT License](LICENSE).

---

## Contact

If you have any questions, suggestions, or professional interest in the project, feel free to reach out:

- Email: pedro@nancode.com.br
- LinkedIn: [Pedro Martins Costa de Souza](https://www.linkedin.com/in/pedromartinscosta/)
- GitHub / Portfolio: [pedromartinscs](https://github.com/pedromartinscs)

---

**Beyond the Rings** was built with ❤️ by [Pedro Martins Costa de Souza](https://github.com/pedromartinscs)
