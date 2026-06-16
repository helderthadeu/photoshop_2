"""Smoke test: a small DAG executes in dependency order without a GUI."""
from typing import Any

from src.blocks.base import Block, Port, PortDirection
from src.blocks.point_blocks import BrightnessBlock, ThresholdBlock
from src.graph.connection import Connection
from src.graph.executor import execute_workspace
from src.graph.node import Node
from src.graph.workspace import Workspace


class _ConstantImageBlock(Block):
    """Test-only source block that emits a fixed image."""

    display_name = "Constant"
    category = "Test"

    def __init__(self, image: list[list[int]]) -> None:
        self._image = image

    def input_ports(self) -> list[Port]:
        return []

    def output_ports(self) -> list[Port]:
        return [Port("image", PortDirection.OUTPUT)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"image": self._image}


def test_brightness_then_threshold_flow():
    workspace = Workspace()
    workspace.add_node(Node("source", _ConstantImageBlock([[10, 20], [30, 200]])))
    workspace.add_node(Node("bright", BrightnessBlock(), {"bias": 100}))
    workspace.add_node(Node("thresh", ThresholdBlock(), {"threshold": 128}))

    workspace.connect(Connection("source", "image", "bright", "image"))
    workspace.connect(Connection("bright", "image", "thresh", "image"))

    result = execute_workspace(workspace)

    assert result.outputs_of("bright")["image"] == [[110, 120], [130, 255]]
    assert result.outputs_of("thresh")["image"] == [[0, 0], [255, 255]]
