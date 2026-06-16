# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

```bash
python main.py
```

This opens matplotlib windows sequentially — close each window to advance to the next. The script uses `2_bracos.webp` and `meci.png` from the project root as its input images.

## Dependencies

The project uses `opencv-python`, `numpy`, and `matplotlib`. Install with:

```bash
pip install opencv-python numpy matplotlib
```

There is no `requirements.txt` or virtual environment configuration.

## Architecture

This is an image processing pipeline project (a Photoshop-like tool). It has no GUI yet beyond matplotlib display windows.

**Module layout:**

- `main.py` — wires everything together; applies a sequence of filters and displays results in a grid
- `models/models.py` — type aliases only: `ImageMatrix = list[list[int]]` (2-D grayscale) and `FilePath = Optional[str]`
- `interface/interface.py` — image I/O: `load_image` (cv2 BGR→RGB), `display_multi_image` (matplotlib grid), PGM file read/write with a P2 parser, tkinter file dialogs, and `ImageMatrix`↔NumPy converters
- `img_process/util.py` — `pad_image`: constant-border padding for convolution; `_to_grayscale`, `_image_dimensions`: internal type-normalisation helpers
- `img_process/local_process.py` — `apply_convolution(image, kernel)`: core convolution engine; normalises input to grayscale, pads, returns `np.uint32` array
- `img_process/pop_mask.py` — pre-built filters on top of `apply_convolution`: `apply_median_filter`, `apply_average_filter`, `apply_laplacian_filter`, `apply_gaussian_filter`, `apply_derivative_filter`
- `img_process/easy_process.py` — pure-Python `ImageMatrix`-based `adjust_brightness` and `apply_threshold` (not currently wired into `main.py`)
- `others/differences.py` — `compute_grayscale_difference`, `compute_color_difference`: pixel-wise absolute difference; mismatched sizes are cropped to the common region
- `others/histogram_generator.py` — `generate_histogram`, `normalize_histogram`, `match_histograms`, `plot_histogram`
- `others/complement_image.py` — `invert_image`: pixel-wise complement (255 − v)
- `others/morphological_operation.py` — `apply_erosion`, `apply_dilation` (stubs, not yet implemented)

**Filter mask convention:** all filters require odd-sized kernels; even sizes raise `ValueError`. Kernels larger than the image also raise.

**Data types:** filters accept both `ImageMatrix` (list of lists) and NumPy arrays (grayscale or BGR). Use `image_matrix_to_numpy` / `numpy_to_image_matrix` from `interface/interface.py` when crossing the boundary.

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
