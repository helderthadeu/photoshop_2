# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

```bash
pip install -r requirements.txt   # numpy, opencv-python, PySide6
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

- `domain/` — `types` (`ImageMatrix`), `conversion`, `convolution` (`apply_convolution` + `pad_image`), `filters` (median/average/laplacian/gaussian/derivative), `point` (brightness/threshold), `histogram` (compute only — no plotting), `difference`, `complement`
- `blocks/` — `base` (`Block`, `Port`, `Parameter`, `BLOCK_REGISTRY`, `@register_block`), then `io_blocks`, `point_blocks`, `filter_blocks`, `analysis_blocks`. Importing `src.blocks` registers all 13 blocks via side-effect. There is no display block: the GUI previews images live from the selected node.
- `graph/` — `node`, `connection`, `workspace` (cycle detection, port validation), `executor` (Kahn topological sort), `errors`
- `application/` — `execution_service.run_workspace`, `project_service` (save/load DAG as JSON)
- `infrastructure/` — `pgm_codec` (hand-written P2 reader/writer + `read_pgm_header`), `image_loader` (`ensure_pgm`: converts any OpenCV-readable image to a cached grayscale PGM so the pipeline only ever sees PGM; cv2 is confined here). File choosing uses Qt's `QFileDialog` directly in the GUI layer.
- `gui/` — `app.run()` (applies the global stylesheet), `main_window` (the *PSE-Image Studio* shell that wires every piece; continuous live preview + project Open/Save), `theme` (single source of palette, fonts, and the Qt stylesheet — DaVinci-Fusion-inspired dark look), `drag_mime` (the shared block drag-and-drop mime id, kept dependency-free to avoid an import cycle between the library and the canvas). Subpackages: `canvas/` (`GraphScene`/`GraphView` plus `NodeItem`/`PortItem`/`ConnectionItem`; drag-to-connect, deletable links, pan/zoom, dotted grid, block drops), `panels/` (`BlockLibrary`, `Inspector`, `Console`, `ImageViewer` + the public `to_grayscale_qimage`/`first_image` helpers), `dialogs/` (`LoadPgmDialog` — pick any image when a Load PGM block is dropped, it is converted to PGM, then preview/metadata/confirm; `SavePgmDialog` — choose the destination when a Save PGM block is dropped; `HistogramDialog` — bar-chart viewer opened by double-clicking a Histogram node; `block_setup` — the one place mapping a block to its dialog, used both on drop and by the inspector's "Procurar…" path button; dialogs share `layout_helpers`), `widgets/` (`TopBar`; `MatrixEditor` — the odd-sized grid editor for `ParameterType.MATRIX` (Convolution kernel); `ValueSlider` — the labelled slider the inspector renders for any ranged numeric parameter, snapping to `Parameter.step` and showing `Parameter.unit`).

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
