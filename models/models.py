"""
models.py

This module defines core domain type aliases to be shared across 
the backend and frontend modules of the project.
"""

from typing import TypeAlias, Optional

# A 2D list representing the grayscale pixel intensities [0-255]
ImageMatrix: TypeAlias = list[list[int]]

# A string representing a valid file system path, or None if the operation was cancelled
FilePath: TypeAlias = Optional[str]