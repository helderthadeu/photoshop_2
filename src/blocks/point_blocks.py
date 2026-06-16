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
    """Shift every pixel intensity by a constant bias."""

    display_name = "Brightness"
    category = "Point"

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def parameters(self) -> list[Parameter]:
        return [Parameter("bias", "Bias", ParameterType.INTEGER, 0, -255, 255)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": adjust_brightness(inputs["image"], parameters["bias"])}


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
