# PSE-Image

A node-based dataflow editor for image processing, built for the *Processamento e
Análise de Imagens* course (PUC Minas). The user wires processing **blocks** into a
graph — read an image, apply point/local/analysis operations, then display or save —
without writing code.

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies: `numpy`, `opencv-python`, `matplotlib`, `PySide6`.

## Running

```bash
# development (no install required)
python -m src

# after installing the package
pip install -e .
pse-image
```

Launches the PySide6 node editor. The graph engine also runs headless, so flows can be
executed and tested without the GUI:

```bash
python -m pytest tests/
```

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

- **Interface:** Read PGM, Display Image, Save PGM
- **Point:** Brightness, Threshold
- **Local:** Convolution (custom kernel), Median, Average, Laplacian, Gaussian, Derivative
- **Analysis:** Histogram, Difference, Complement

Morphological operations (erosion/dilation) are stubbed in `domain/morphology.py`.

## Project structure

```
src/                    # application package (see table above)
  __main__.py           # entry point → python -m src
assets/images/          # sample images and PGM test bases
tests/                  # headless tests for the graph engine
```
