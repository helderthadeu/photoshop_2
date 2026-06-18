# PSE-Image

A node-based dataflow editor for image processing, built for the *Processamento e
Análise de Imagens* course (PUC Minas). The user wires processing **blocks** into a
graph — read an image, apply point/local/analysis operations, then display or save —
without writing code.

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies: `numpy`, `opencv-python`, `PySide6`.

## Running

```bash
# development (no install required)
python -m src

# after installing the package
pip install -e .
pse-image
```

Launches **PSE-Image Studio**, the PySide6 node editor. The graph engine also runs
headless, so flows can be executed and tested without the GUI:

```bash
python -m pytest tests/
```

## Using the editor

A dark, DaVinci-Fusion-inspired workspace:

- **Block Library** (left) — drag a block onto the canvas to create a node. Nodes are
  colour-coded by category (Interface, Point, Local, Analysis…).
- **Node graph** (centre) — drag from an output socket to an input socket to wire
  nodes; invalid or cyclic links are rejected and reported in the console. Click a link
  to select it (it tints red) and press `Delete` to undo the wiring; `Delete` on a
  selected node removes it along with its links. Middle-drag pans and the wheel zooms.
- **Inspector** (right) — edits the selected node's parameters; the widgets are
  generated from each block's parameter declarations.
- **Preview viewers** (top) — **ORIGINAL** always shows the loaded source image (the Load
  PGM output) and never changes with downstream edits; **PROCESSED** shows the result of
  the selected node (or the latest one). Both refresh whenever the graph or a parameter
  changes. Refreshes are debounced and run on a background thread, with per-node result
  caching, so editing stays responsive even with heavy filters; dropping a not-yet-wired
  node triggers no recomputation.
- **Console** (bottom) — execution log and error feedback.
- **Histogram** — double-click a Histogram node to open its bar-chart viewer. Wiring a
  Histogram into a Save PGM node writes the chart to disk as a PGM.

Execution is continuous — there is no run button. A complete pipeline has at least one
**Load PGM** (input) and one **Save PGM** (output); the console flags when that is missing,
and Save sinks write to disk as part of the live flow once a path is set. **Open/Save
Project** in the top bar load and persist the whole graph as JSON.

## Architecture

Layered clean architecture; dependencies point inward:

| Layer | Responsibility |
|-------|----------------|
| `src/gui/` | PySide6 canvas, block palette, image/histogram viewers |
| `src/application/` | Use cases: run a workspace, save/load a project |
| `src/graph/` | The DAG model + topological executor (headless) |
| `src/blocks/` | Blocks: adapters that declare ports + parameters over domain functions |
| `src/domain/` | Pure image-processing algorithms |
| `src/infrastructure/` | PGM codec, image loading, file dialogs (isolates cv2/tk) |

### Implemented blocks

- **Interface:** Load PGM (pick any image — it is converted to PGM), Save PGM
- **Point:** Brightness, Threshold
- **Local:** Convolution (custom kernel), Median, Average, Laplacian, Gaussian, Derivative
- **Analysis:** Histogram, Difference, Complement

## Project structure

```
src/                    # application package (see table above)
  __main__.py           # entry point → python -m src
assets/images/          # sample images and PGM test bases
tests/                  # headless tests for the graph engine
```
