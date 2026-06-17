"""Interface blocks: read a PGM source and save a PGM sink.

There is no display block: the editor previews images live from the selected
node, so a viewer is a GUI concern rather than a node in the graph.
"""
from typing import Any

from src.blocks.base import (
    Block,
    Parameter,
    ParameterType,
    Port,
    PortDirection,
    register_block,
)
from src.domain.histogram import render_histogram_image
from src.infrastructure.pgm_codec import read_pgm_file, write_pgm_file


@register_block
class LoadPgmBlock(Block):
    """Source block that loads an image from a PGM file."""

    display_name = "Load PGM"
    category = "Interface"

    def input_ports(self) -> list[Port]:
        return []

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def parameters(self) -> list[Parameter]:
        return [Parameter("path", "File path", ParameterType.TEXT, "")]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": read_pgm_file(parameters["path"])}


@register_block
class SavePgmBlock(Block):
    """Sink block that writes its input to a PGM file.

    Accepts either an image or a histogram: a histogram (a flat list of counts)
    is first rendered to a bar-chart image so it can be saved as a PGM too.
    """

    display_name = "Save PGM"
    category = "Interface"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return []

    def parameters(self) -> list[Parameter]:
        return [Parameter("path", "File path", ParameterType.TEXT, "")]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        path = parameters["path"]
        # An unconfigured sink (no path yet) is a no-op so continuous execution
        # is not broken while the graph is still being wired up.
        if path:
            data = inputs["image"]
            matrix = render_histogram_image(data) if _is_histogram(data) else data
            write_pgm_file(path, matrix)
        return {}


def _is_histogram(value: Any) -> bool:
    """True when `value` is a flat list of counts rather than a 2-D image."""
    return isinstance(value, list) and bool(value) and not isinstance(value[0], list)
