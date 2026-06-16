"""OS file-chooser dialogs for PGM open/save operations.

Uses tkinter dialogs so they stay independent of the Qt GUI layer.
"""
import tkinter as tk
from tkinter import filedialog

FilePath = str | None


def select_pgm_file() -> FilePath:
    """Open a file-chooser dialog filtered to PGM files.

    Returns:
        Selected file path, or None if the user cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a PGM File",
        filetypes=[("PGM Files", "*.pgm"), ("All Files", "*.*")],
    )
    return file_path or None


def save_pgm_file() -> FilePath:
    """Open a save-file dialog that enforces the .pgm extension.

    Returns:
        Chosen save path, or None if the user cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save PGM File",
        defaultextension=".pgm",
        filetypes=[("PGM Files", "*.pgm")],
    )
    return file_path or None
