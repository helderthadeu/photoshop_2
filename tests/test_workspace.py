"""Tests for workspace DAG validity: ports, cycles, and removal."""
from typing import Any

import pytest

from src.blocks.base import Block, Port, PortDirection
from src.graph.connection import Connection
from src.graph.errors import ConnectionError, CycleError
from src.graph.node import Node
from src.graph.workspace import Workspace


class _PassThrough(Block):
    """Test block with one input and one output."""

    def input_ports(self) -> list[Port]:
        return [Port("in", PortDirection.INPUT)]

    def output_ports(self) -> list[Port]:
        return [Port("out", PortDirection.OUTPUT)]

    def process(self, inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
        return {"out": inputs.get("in")}


def _two_node_workspace() -> Workspace:
    workspace = Workspace()
    workspace.add_node(Node("a", _PassThrough()))
    workspace.add_node(Node("b", _PassThrough()))
    return workspace


def test_valid_connection_is_recorded():
    workspace = _two_node_workspace()
    workspace.connect(Connection("a", "out", "b", "in"))
    assert len(workspace.connections) == 1


def test_cycle_is_rejected():
    workspace = _two_node_workspace()
    workspace.connect(Connection("a", "out", "b", "in"))
    with pytest.raises(CycleError):
        workspace.connect(Connection("b", "out", "a", "in"))


def test_unknown_node_is_rejected():
    workspace = _two_node_workspace()
    with pytest.raises(ConnectionError):
        workspace.connect(Connection("a", "out", "ghost", "in"))


def test_unknown_port_is_rejected():
    workspace = _two_node_workspace()
    with pytest.raises(ConnectionError):
        workspace.connect(Connection("a", "missing", "b", "in"))


def test_removing_a_node_drops_its_connections():
    workspace = _two_node_workspace()
    workspace.connect(Connection("a", "out", "b", "in"))
    workspace.remove_node("a")
    assert workspace.connections == []


def test_duplicate_node_id_is_rejected():
    workspace = Workspace()
    workspace.add_node(Node("a", _PassThrough()))
    with pytest.raises(ConnectionError):
        workspace.add_node(Node("a", _PassThrough()))
