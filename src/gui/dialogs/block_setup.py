"""Maps blocks to the dialog that configures them.

A single place that decides which modal a block needs — used both when a block is
dropped on the canvas (to seed its parameters) and when its path is changed later
from the inspector. Keeps that block→dialog knowledge out of the canvas and the
inspector.
"""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from src.blocks.base import Block
from src.blocks.io_blocks import LoadPgmBlock, SavePgmBlock
from src.gui.dialogs.load_pgm_dialog import LoadPgmDialog
from src.gui.dialogs.save_pgm_dialog import SavePgmDialog


def initial_parameters(block_class: type, parent: QWidget | None = None) -> dict | None:
    """Return seed parameters for a newly dropped block, or None if cancelled.

    Blocks that need no setup return an empty dict; Load/Save prompt for a path.
    """
    if block_class is LoadPgmBlock:
        return _path_parameters(LoadPgmDialog.choose(parent))
    if block_class is SavePgmBlock:
        return _path_parameters(SavePgmDialog.choose(parent))
    return {}


def choose_path(block: Block, parent: QWidget | None = None) -> str | None:
    """Re-open the dialog matching `block` to pick a new path, or None if cancelled."""
    if isinstance(block, LoadPgmBlock):
        return LoadPgmDialog.choose(parent)
    if isinstance(block, SavePgmBlock):
        return SavePgmDialog.choose(parent)
    return None


def _path_parameters(path: str | None) -> dict | None:
    if path is None:
        return None
    return {"path": path}
