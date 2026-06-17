"""Local-processing blocks: parametrizable convolution plus known kernels."""
from typing import Any

from src.blocks.base import (
    Block,
    Parameter,
    ParameterType,
    Port,
    PortDirection,
    register_block,
)
from src.domain.convolution import apply_convolution
from src.domain.filters import (
    apply_average_filter,
    apply_derivative_filter,
    apply_gaussian_filter,
    apply_laplacian_filter,
    apply_median_filter,
)


def _image_io(block: Block) -> tuple[list[Port], list[Port]]:
    """Shared single-image-in, single-image-out port layout."""
    return (
        [Port("image", PortDirection.INPUT)],
        [Port("image", PortDirection.OUTPUT)],
    )


@register_block
class ConvolutionBlock(Block):
    """Apply a user-defined convolution kernel (size and weights)."""

    display_name = "Convolution"
    category = "Local"

    def input_ports(self) -> list[Port]:
        return _image_io(self)[0]

    def output_ports(self) -> list[Port]:
        return _image_io(self)[1]

    def parameters(self) -> list[Parameter]:
        # The inspector renders a grid editor for MATRIX parameters.
        default_kernel = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
        return [Parameter("kernel", "Kernel", ParameterType.MATRIX, default_kernel)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": apply_convolution(inputs["image"], parameters["kernel"])}


@register_block
class MedianFilterBlock(Block):
    """Median filter over an odd-sized square neighbourhood."""

    display_name = "Median Filter"
    category = "Local"

    def input_ports(self) -> list[Port]:
        return _image_io(self)[0]

    def output_ports(self) -> list[Port]:
        return _image_io(self)[1]

    def parameters(self) -> list[Parameter]:
        return [Parameter("kernel_size", "Kernel size", ParameterType.INTEGER, 5, 3, 25, step=2)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": apply_median_filter(inputs["image"], parameters["kernel_size"])}


@register_block
class AverageFilterBlock(Block):
    """Mean (box) filter over an odd-sized square neighbourhood."""

    display_name = "Average Filter"
    category = "Local"

    def input_ports(self) -> list[Port]:
        return _image_io(self)[0]

    def output_ports(self) -> list[Port]:
        return _image_io(self)[1]

    def parameters(self) -> list[Parameter]:
        return [Parameter("kernel_size", "Kernel size", ParameterType.INTEGER, 5, 3, 25, step=2)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": apply_average_filter(inputs["image"], parameters["kernel_size"])}


@register_block
class LaplacianFilterBlock(Block):
    """Laplacian-of-Gaussian edge filter."""

    display_name = "Laplacian Filter"
    category = "Local"

    def input_ports(self) -> list[Port]:
        return _image_io(self)[0]

    def output_ports(self) -> list[Port]:
        return _image_io(self)[1]

    def parameters(self) -> list[Parameter]:
        return [
            Parameter("kernel_size", "Kernel size", ParameterType.INTEGER, 3, 3, 25, step=2),
            Parameter("sigma", "Sigma", ParameterType.FLOAT, 1.0, 0.1, 10.0, step=0.1),
        ]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        result = apply_laplacian_filter(
            inputs["image"],
            parameters["kernel_size"],
            parameters["sigma"],
        )
        return {"image": result}


@register_block
class GaussianFilterBlock(Block):
    """Distance-weighted Gaussian blur."""

    display_name = "Gaussian Filter"
    category = "Local"

    def input_ports(self) -> list[Port]:
        return _image_io(self)[0]

    def output_ports(self) -> list[Port]:
        return _image_io(self)[1]

    def parameters(self) -> list[Parameter]:
        return [Parameter("kernel_size", "Kernel size", ParameterType.INTEGER, 3, 3, 25, step=2)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": apply_gaussian_filter(inputs["image"], parameters["kernel_size"])}


@register_block
class DerivativeFilterBlock(Block):
    """Directional (x or y) derivative filter."""

    display_name = "Derivative Filter"
    category = "Local"

    def input_ports(self) -> list[Port]:
        return _image_io(self)[0]

    def output_ports(self) -> list[Port]:
        return _image_io(self)[1]

    def parameters(self) -> list[Parameter]:
        return [
            Parameter("kernel_size", "Kernel size", ParameterType.INTEGER, 3, 3, 25, step=2),
            Parameter(
                "direction",
                "Direction",
                ParameterType.CHOICE,
                "x",
                choices=["x", "y"],
                choice_labels=["Horizontal (x)", "Vertical (y)"],
            ),
        ]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        result = apply_derivative_filter(
            inputs["image"],
            parameters["kernel_size"],
            parameters["direction"],
        )
        return {"image": result}
