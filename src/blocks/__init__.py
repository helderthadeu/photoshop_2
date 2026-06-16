"""Block definitions: thin adapters that wrap domain functions as graph nodes.

Importing this package registers every built-in block in the BLOCK_REGISTRY.
"""
from src.blocks import (  # noqa: F401  (imported for side-effect: registration)
    analysis_blocks,
    filter_blocks,
    io_blocks,
    point_blocks,
)
