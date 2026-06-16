"""Interface blocks: read a PGM source, display, and save a PGM sink."""
from typing import Any

from src.blocks.base import (
    Block,
    Parameter,
    ParameterType,
    Port,
    PortDirection,
    register_block,
)
from src.infrastructure.pgm_codec import read_pgm_file, write_pgm_file


@register_block
class ReadPgmBlock(Block):
    """Source block that loads an image from a PGM file."""

    display_name = "Read PGM"
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
    """Sink block that writes its input image to a PGM file."""

    display_name = "Save PGM"
    category = "Interface"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return []

    def parameters(self) -> list[Parameter]:
        return [Parameter("path", "File path", ParameterType.TEXT, "")]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        write_pgm_file(parameters["path"], inputs["image"])
        return {}


@register_block
class DisplayImageBlock(Block):
    """Sink block that passes its input through for the GUI viewer to render."""

    display_name = "Display Image"
    category = "Interface"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return []

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        # The GUI reads the executor's cached input for this node to display it.
        return {}
