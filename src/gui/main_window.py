"""The PSE-Image Studio main window: a Fusion-style node compositor for images.

The window wires the independent pieces together — top bar, block library,
node canvas, inspector, console, and image viewers — and owns the cross-cutting
behaviour. There is no display node and no run button: execution is continuous,
so the two viewers show a live ORIGINAL/PROCESSED preview of the selected node,
refreshed whenever the graph or a parameter changes, and Save PGM sinks write as
part of that flow. A complete pipeline is expected to have at least one PGM input
and one PGM output; the console reports when that requirement is unmet. Each
piece stays unaware of the others.
"""
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QWidget,
)

import src.blocks  # noqa: F401  (imported to populate BLOCK_REGISTRY)
from src.application.execution_service import run_workspace
from src.application.project_service import load_project, save_project
from src.blocks.analysis_blocks import HistogramBlock
from src.blocks.io_blocks import LoadPgmBlock, SavePgmBlock
from src.domain.types import ImageMatrix
from src.graph.errors import GraphError
from src.graph.executor import ExecutionResult
from src.graph.node import Node
from src.graph.workspace import Workspace
from src.gui.canvas.graph_scene import GraphScene
from src.gui.canvas.graph_view import GraphView
from src.gui.dialogs.block_setup import choose_path
from src.gui.dialogs.histogram_dialog import HistogramDialog
from src.gui.panels.block_library import BlockLibrary
from src.gui.panels.console import Console
from src.gui.panels.image_viewer import ImageViewer, first_image
from src.gui.panels.inspector import Inspector
from src.gui.widgets.topbar import TopBar


class MainWindow(QMainWindow):
    """Top-level shell hosting the editor, viewers, inspector, and console."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PSE-Image Studio")
        self.resize(1440, 900)

        self._scene = GraphScene(Workspace())
        self._view = GraphView(self._scene)
        self._inspector = Inspector()
        self._console = Console()
        self._library = BlockLibrary()
        self._original_viewer = ImageViewer("ORIGINAL")
        self._processed_viewer = ImageViewer("PROCESSED")
        self._topbar = TopBar()
        self._selected_node: Node | None = None
        self._last_preview_error: str | None = None
        self._pipeline_complete = False

        self._build_layout()
        self._connect_signals()

    # --- layout -------------------------------------------------------------

    def _build_layout(self) -> None:
        self.setMenuWidget(self._topbar)
        self.setCentralWidget(self._build_central())
        self._add_dock(self._library, Qt.DockWidgetArea.LeftDockWidgetArea)
        self._add_dock(self._inspector, Qt.DockWidgetArea.RightDockWidgetArea)
        self._add_dock(self._console, Qt.DockWidgetArea.BottomDockWidgetArea, "Console")

    def _build_central(self) -> QSplitter:
        viewers = QWidget()
        viewers_layout = QHBoxLayout(viewers)
        viewers_layout.setContentsMargins(0, 0, 0, 0)
        viewers_layout.addWidget(self._original_viewer)
        viewers_layout.addWidget(self._processed_viewer)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(viewers)
        splitter.addWidget(self._view)
        splitter.setSizes([320, 540])
        return splitter

    def _add_dock(self, widget: QWidget, area: Qt.DockWidgetArea, title: str = "") -> None:
        """Pin a panel in place; an empty title hides the dock header entirely.

        Every dock is fixed — no moving, floating, or closing. The side panels
        carry their own heading, so they are header-less; the console keeps a
        titled header bar.
        """
        dock = QDockWidget(title, self)
        dock.setWidget(widget)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock.setAllowedAreas(area)
        if not title:
            dock.setTitleBarWidget(QWidget(dock))
        self.addDockWidget(area, dock)

    def _connect_signals(self) -> None:
        self._scene.node_selected.connect(self._on_node_selected)
        self._scene.node_activated.connect(self._on_node_activated)
        self._scene.connection_failed.connect(self._console.error)
        self._scene.graph_changed.connect(self._on_graph_changed)
        self._inspector.parameter_changed.connect(self._refresh_preview)
        self._inspector.path_browse_requested.connect(self._browse_path)
        self._topbar.save_requested.connect(self._save_project)
        self._topbar.open_requested.connect(self._open_project)

    # --- selection + live preview ------------------------------------------

    def _on_node_selected(self, node: Node | None) -> None:
        """Track the selected node, update the inspector, and refresh preview."""
        self._selected_node = node
        self._inspector.set_node(node)
        self._refresh_preview()

    def _browse_path(self, node: Node) -> None:
        """Re-open the block's dialog to choose a new file path, then refresh."""
        path = choose_path(node.block, self)
        if path is None:
            return
        node.parameters["path"] = path
        self._inspector.set_node(node)
        self._refresh_preview()

    def _on_node_activated(self, node: Node) -> None:
        """Double-click on a Histogram node opens its histogram plot."""
        if not isinstance(node.block, HistogramBlock):
            return
        try:
            result = run_workspace(self._scene.workspace)
        except Exception as error:  # boundary: report why the plot is unavailable
            self._console.error(f"Não foi possível gerar o histograma: {error}")
            return

        histogram = result.outputs_of(node.node_id).get("histogram")
        if histogram is None:
            self._console.warning("Sem histograma para exibir ainda.")
            return
        HistogramDialog(histogram, self).exec()

    def _on_graph_changed(self) -> None:
        """React to a structural change: re-check the pipeline and refresh preview."""
        self._check_pipeline()
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        """Re-execute the graph and refresh the ORIGINAL/PROCESSED previews.

        ORIGINAL always shows the loaded source image (the Load PGM output) and is
        unaffected by selection or downstream edits; PROCESSED shows the result of
        the selected node (or the latest producer). Runs on every graph or
        parameter change. A failure during editing (an unset path, an incomplete
        kernel) clears the preview and is reported once — identical repeats are
        not re-logged.
        """
        if not self._scene.workspace.nodes:
            self._clear_preview()
            return

        try:
            result = run_workspace(self._scene.workspace)
        except Exception as error:  # boundary: keep editing fluid, report once
            self._report_preview_error(str(error))
            self._clear_preview()
            return

        self._last_preview_error = None
        self._show_original(result)
        self._show_processed(result)

    def _show_original(self, result: ExecutionResult) -> None:
        """Show the loaded source image; clear if there is no Load PGM node."""
        source = self._source_node()
        if source is None:
            self._original_viewer.clear_image()
            return
        image = first_image(result.outputs_of(source.node_id))
        self._set_viewer(self._original_viewer, f"ORIGINAL · {source.node_id}", image)

    def _show_processed(self, result: ExecutionResult) -> None:
        """Show the selected node's result, or the latest producer's if none."""
        node = self._selected_node or self._preview_fallback_node()
        if node is None:
            self._processed_viewer.clear_image()
            return
        output = first_image(result.outputs_of(node.node_id))
        fallback = first_image(result.inputs_of(node.node_id))
        image = output if output is not None else fallback
        self._set_viewer(self._processed_viewer, f"PROCESSED · {node.node_id}", image)

    def _source_node(self) -> Node | None:
        """The first Load PGM node, whose image feeds the ORIGINAL preview."""
        for node in self._scene.workspace.nodes.values():
            if isinstance(node.block, LoadPgmBlock):
                return node
        return None

    def _set_viewer(
        self,
        viewer: ImageViewer,
        subtitle: str,
        image: ImageMatrix | np.ndarray | None,
    ) -> None:
        if image is None:
            viewer.clear_image()
            return
        viewer.show_image(image, subtitle)

    def _clear_preview(self) -> None:
        self._original_viewer.clear_image()
        self._processed_viewer.clear_image()

    def _report_preview_error(self, message: str) -> None:
        if message == self._last_preview_error:
            return
        self._last_preview_error = message
        self._console.warning(f"Preview unavailable: {message}")

    def _preview_fallback_node(self) -> Node | None:
        """Pick a node to preview when nothing is selected: the latest producer."""
        for node in reversed(list(self._scene.workspace.nodes.values())):
            if node.block.output_ports():
                return node
        return None

    # --- pipeline validation ------------------------------------------------

    def _check_pipeline(self) -> None:
        """Report when the graph gains or loses a required PGM input/output pair."""
        complete = self._has_block(LoadPgmBlock) and self._has_block(SavePgmBlock)
        if complete == self._pipeline_complete:
            return

        self._pipeline_complete = complete
        if complete:
            self._console.success("Pipeline ready: PGM input → PGM output.")
        else:
            self._console.warning("Pipeline needs at least one Load PGM and one Save PGM.")

    def _has_block(self, block_type: type) -> bool:
        for node in self._scene.workspace.nodes.values():
            if isinstance(node.block, block_type):
                return True
        return False

    # --- project I/O --------------------------------------------------------

    def _save_project(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "PSE Project (*.json)")
        if not path:
            return
        save_project(self._scene.workspace, path)
        self._console.success(f"Saved project to {path}.")

    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "PSE Project (*.json)")
        if not path:
            return
        try:
            workspace = load_project(path)
        except GraphError as error:
            self._console.error(f"Could not open project: {error}")
            return
        self._scene.load_workspace(workspace)
        self._console.success(f"Opened project from {path}.")

    # --- shortcuts ----------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent) -> None:  # standards: allow-framework-override
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self._scene.remove_selected()
            event.accept()
            return
        super().keyPressEvent(event)
