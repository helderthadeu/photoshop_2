"""Dockable panels: block library, inspector, console, and image viewer."""
from src.gui.panels.block_library import BlockLibrary
from src.gui.panels.console import Console
from src.gui.panels.image_viewer import ImageViewer
from src.gui.panels.inspector import Inspector

__all__ = [
    "BlockLibrary",
    "Console",
    "ImageViewer",
    "Inspector",
]
