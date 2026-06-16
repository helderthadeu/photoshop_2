# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

```bash
pip install -r requirements.txt   # numpy, opencv-python, matplotlib, PySide6
python main.py                    # launches the PySide6 node editor
```

The graph engine runs headless (no GUI needed) — useful for tests:

```bash
python -m pytest tests/           # or run a test function directly if pytest is absent
```

## What this is

**PSE-Image** — a node-based dataflow editor for image processing. The user wires
processing **blocks** into a directed acyclic graph (DAG); each block takes images
in and produces images out. This is the architectural driver: everything orbits the
graph, and the filters are the innermost, replaceable detail.

## Architecture — layered, dependencies point inward

```
gui/            PySide6 canvas, palette, viewers          (framework lives ONLY here)
  ↓
application/    use cases: run_workspace, save/load project
  ↓
graph/          Workspace (DAG) + topological executor     (headless, fully testable)
  ↓
blocks/         Block = adapter declaring ports+parameters (registry pattern)
  ↓
domain/         pure algorithms (filters, histogram, …)    (no UI, no I/O orchestration)

infrastructure/ PGM codec, cv2 loader, file dialogs        (implements I/O for inner layers)
```

**The dependency rule:** `domain` knows nothing about blocks or GUI. The GUI depends
inward, never the reverse. You can execute a whole flow without launching Qt.

**Package layout** (`src/`):

- `domain/` — `types` (`ImageMatrix`), `conversion`, `convolution` (`apply_convolution` + `pad_image`), `filters` (median/average/laplacian/gaussian/derivative), `point` (brightness/threshold), `histogram` (compute only — no plotting), `difference`, `complement`, `morphology` (stubs)
- `blocks/` — `base` (`Block`, `Port`, `Parameter`, `BLOCK_REGISTRY`, `@register_block`), then `io_blocks`, `point_blocks`, `filter_blocks`, `analysis_blocks`. Importing `src.blocks` registers all 14 blocks via side-effect.
- `graph/` — `node`, `connection`, `workspace` (cycle detection, port validation), `executor` (Kahn topological sort), `errors`
- `application/` — `execution_service.run_workspace`, `project_service` (save/load DAG as JSON)
- `infrastructure/` — `pgm_codec` (hand-written P2 reader/writer), `image_loader` (cv2 + `ImageMatrix`↔NumPy), `file_dialogs` (tkinter)
- `gui/` — `app.run()`, `main_window` (minimal shell so far); `canvas/`, `panels/`, `widgets/` are scaffolded but not yet implemented

**Key conventions:**
- A **Block** is stateless; it *declares* ports + parameter specs and implements a pure `process(inputs, parameters)`. Per-node parameter *values* live on `Node`. The GUI renders parameter panels generically from the declarations — never hand-code UI per operation.
- All filters require odd-sized kernels (`ValueError` otherwise); kernels larger than the image also raise.
- Filters accept both `ImageMatrix` (list of lists) and NumPy arrays. cv2 is confined to `infrastructure/` and `domain/conversion.py` / `domain/histogram.py`.
- **"No ready-made methods" (course rule):** all *algorithms* are hand-written. cv2 is used only for file loading and BGR→gray; if the professor forbids the latter, replace `cvtColor` in `domain/conversion.py` with a hand-rolled luminance conversion.

---

## Coding Standards

These standards apply to all Python code in this repository. Apply them whenever writing or reviewing code.

### Naming

- **Packages, modules, functions, variables** → `snake_case`.
- **Classes** → `PascalCase`, noun names.
- **Functions and methods** → verbs or verbal phrases that describe the action (`apply_filter`, not `filter`).
- **Constants** → `UPPER_SNAKE_CASE`.
- **Internal symbols** → prefix with `_` when visibility must be clear to readers and consumers.
- Names must be meaningful, pronounceable, and searchable. Avoid ambiguous abbreviations; domain abbreviations (e.g. `pgm`, `rgb`) are allowed when they are standard in the field.
- Do not expose internal symbols for convenience; create an intentional public API only when there is a sustained contract.

### Functions

- A function must have one clear responsibility. Error handling that grows large should be extracted to a boundary/wrapper.
- Functions should be lean — ideally around 20 lines. Exceeding that requires evident cohesion or extraction.
- Organise files in decreasing abstraction order: public/high-level functions first, their private helpers immediately below.
- Parameters must not exceed a triad; use a `dataclass` or request object when there are more.
- Framework-imposed signatures (Qt overrides, callbacks) may exceed the triad; mark with `# standards: allow-framework-override` and delegate logic to small helpers.
- Functions must not have hidden side effects. Disk writes, network, global state, UI, and relevant logging must be clear from the name, contract, or orchestration layer.
- Apply the Law of Demeter: avoid long chains that access internal details of other objects.
- Separate distinct concepts within a function with blank lines.
- When a large refactor occurs, look for dead code and remove anything with no real use.

### Error handling

- Use exceptions instead of error codes for internal Python failures.
- Never return `None` to indicate an error; raise an exception with a clear message.
- Domain errors should use custom exceptions from the package or tool.
- `try/except` must catch specific exceptions; never hide broad failures without logging context.
- `None` is only a legitimate optional value, not an error signal. When `None` represents a valid absence, type-hint it as `T | None` and return it directly.

### Types and imports

- Type hints are mandatory on functions, methods, dataclasses, and relevant public or internal returns.
- Organise imports in three blocks separated by blank lines: standard library → third-party → local. Remove unused imports.
- Use `pathlib.Path` for file paths.
- Do not use mutable objects as default arguments; in dataclasses use `field(default_factory=...)`.

### Data and comments

- Dataclasses represent data and must not contain business logic; place behaviour in services or domain functions.
- A file must have one main responsibility. A short module comment explaining its role and boundaries is useful.
- Comments must explain intent, domain rules, trade-offs, or context — not repeat what the code already says.
- Public artefacts require docstrings covering contract, parameters, return value, and errors.
- Private artefacts may have smaller comments focused on the reason.

### Additional conventions adopted in this project

- `__all__` should be declared in modules that have a clear public/private split, to make the public API explicit.
- Target 88-character line length (Black-compatible).
- **Prefer explicit `for` loops over list comprehensions** (*explicit iteration* principle). List comprehensions compress multiple steps into a single expression, which reduces readability when the body is non-trivial, nested, or multi-step. Use explicit loops with named intermediate variables so intent stays clear. Reserve inline comprehensions only for configuration-style literals (e.g. building a constant matrix of identical weights) where the pattern is immediately obvious.
- Update `README.md` when a change alters structure, components, contracts, or flows.
