"""Point-processing blocks: brightness and threshold."""
from typing import Any

from src.blocks.base import (
    Block,
    Parameter,
    ParameterType,
    Port,
    PortDirection,
    register_block,
)
from src.domain.point import adjust_brightness, apply_threshold


@register_block
class BrightnessBlock(Block):
    """Brighten or darken the image by a percentage of the full intensity range."""

    display_name = "Brightness"
    category = "Point"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def parameters(self) -> list[Parameter]:
        return [Parameter("percent", "Brightness", ParameterType.INTEGER, 0, -100, 100, unit="%")]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        # ±100% maps to ±1.0 factor for brightness adjustment.
        bias = parameters["percent"] / 100
        return {"image": adjust_brightness(inputs["image"], bias)}


@register_block
class ThresholdBlock(Block):
    """Binarise an image at a fixed intensity threshold."""

    display_name = "Threshold"
    category = "Point"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def parameters(self) -> list[Parameter]:
        return [Parameter("threshold", "Threshold", ParameterType.INTEGER, 128, 0, 255)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": apply_threshold(inputs["image"], parameters["threshold"])}
