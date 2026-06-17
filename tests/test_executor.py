"""Tests for execution: missing inputs and the histogram→save flow."""
from typing import Any

import pytest

import src.blocks  # noqa: F401  (registers the built-in blocks)
from src.blocks.analysis_blocks import HistogramBlock
from src.blocks.base import Block, Port, PortDirection
from src.blocks.io_blocks import LoadPgmBlock, SavePgmBlock
from src.graph.connection import Connection
from src.graph.errors import MissingInputError
from src.graph.executor import execute_workspace
from src.graph.node import Node
from src.graph.workspace import Workspace
from src.infrastructure.pgm_codec import read_pgm_header, write_pgm_file


class _Sink(Block):
    """A block that requires an image input but never gets one in the test."""

    def input_ports(self) -> list[Port]:
        return [Port("image", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return []

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {}


def test_unconnected_input_raises_missing_input_error():
    workspace = Workspace()
    workspace.add_node(Node("sink", _Sink()))
    with pytest.raises(MissingInputError):
        execute_workspace(workspace)


def test_histogram_is_saved_as_a_chart_image(tmp_path):
    source = tmp_path / "in.pgm"
    destination = tmp_path / "hist.pgm"
    write_pgm_file(source, [[0, 128, 255], [0, 128, 255]])

    workspace = Workspace()
    workspace.add_node(Node("load", LoadPgmBlock(), {"path": str(source)}))
    workspace.add_node(Node("hist", HistogramBlock()))
    workspace.add_node(Node("save", SavePgmBlock(), {"path": str(destination)}))
    workspace.connect(Connection("load", "image", "hist", "image"))
    workspace.connect(Connection("hist", "histogram", "save", "image"))

    execute_workspace(workspace)

    assert destination.exists()
    width, height, _ = read_pgm_header(destination)
    assert (width, height) == (256, 200)
