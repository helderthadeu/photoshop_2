"""Shared drag-and-drop mime identifier for blocks dragged onto the canvas.

Kept in its own dependency-free module so the block library and the canvas view
can both reference it without importing each other (which would form a cycle).
"""

BLOCK_MIME_TYPE = "application/x-pse-block"
