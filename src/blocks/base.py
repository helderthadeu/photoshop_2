"""Core block abstractions: ports, parameters, the Block contract, and a registry.

A Block declares its input/output ports and parameter specs, and implements a
pure `process` that maps input images + parameter values to output images. The
GUI renders parameter panels generically from these declarations; the graph
executor calls `process`. Blocks are stateless — per-node values live on Node.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PortDirection(Enum):
    INPUT = "input"
    OUTPUT = "output"


class ParameterType(Enum):
    INTEGER = "integer"
    FLOAT = "float"
    TEXT = "text"
    CHOICE = "choice"


@dataclass(frozen=True)
class Port:
    """A named input or output socket on a block."""
    name: str
    direction: PortDirection


@dataclass(frozen=True)
class Parameter:
    """A user-editable parameter spec the GUI uses to build an input widget."""
    name: str
    label: str
    parameter_type: ParameterType
    default: Any
    minimum: float | None = None
    maximum: float | None = None
    choices: list[str] = field(default_factory=list)


class Block(ABC):
    """Base class for every processing block.

    Subclasses set `display_name`/`category` and implement the port, parameter,
    and process contract. `process` must be free of side effects.
    """

    display_name: str = "Block"
    category: str = "General"

    @abstractmethod
    def input_ports(self) -> list[Port]:
        """Return the input sockets this block consumes."""

    @abstractmethod
    def output_ports(self) -> list[Port]:
        """Return the output sockets this block produces."""

    def parameters(self) -> list[Parameter]:
        """Return the editable parameter specs (none by default)."""
        return []

    @abstractmethod
    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        """Transform input port values into output port values.

        Args:
            inputs: Mapping of input port name → upstream value.
            parameters: Mapping of parameter name → user-set value.

        Returns:
            Mapping of output port name → produced value.
        """

    def default_parameters(self) -> dict[str, Any]:
        """Return a fresh mapping of parameter name → default value."""
        defaults: dict[str, Any] = {}
        for parameter in self.parameters():
            defaults[parameter.name] = parameter.default
        return defaults


BLOCK_REGISTRY: dict[str, type[Block]] = {}


def register_block(block_class: type[Block]) -> type[Block]:
    """Class decorator that records a block type in the global registry."""
    BLOCK_REGISTRY[block_class.__name__] = block_class
    return block_class
