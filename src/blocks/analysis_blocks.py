"""Analysis blocks: histogram, image difference, and complement."""
from typing import Any

from src.blocks.base import (
    Block,
    Port,
    PortDirection,
    register_block,
)
from src.domain.complement import invert_image
from src.domain.difference import compute_grayscale_difference
from src.domain.histogram import generate_histogram


@register_block
class HistogramBlock(Block):
    """Produce the intensity histogram of an image for plotting."""

    display_name = "Histogram"
    category = "Analysis"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return [Port("histogram", PortDirection.OUTPUT)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"histogram": generate_histogram(inputs["image"])}


@register_block
class DifferenceBlock(Block):
    """Absolute pixel-wise difference between two grayscale images."""

    display_name = "Difference"
    category = "Analysis"

    def input_ports(self) -> list[Port]:
        return [
            Port("image_a", PortDirection.INPUT),
            Port("image_b", PortDirection.INPUT),
        ]

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        result = compute_grayscale_difference(inputs["image_a"], inputs["image_b"])
        return {"image": result}


@register_block
class ComplementBlock(Block):
    """Photographic negative (255 - v) of a grayscale image."""

    display_name = "Complement"
    category = "Analysis"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": invert_image(inputs["image"])}
