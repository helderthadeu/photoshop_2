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
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
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
from src.graph.executor import ExecutionResult, NodeCache, NodeProgress
from src.graph.node import Node
from src.graph.workspace import Workspace

# How long to coalesce rapid edits (slider drags, successive drops) before
# launching one preview run, in milliseconds.
_PREVIEW_DEBOUNCE_MS = 40


def _format_elapsed(seconds: float) -> str:
    """Render an elapsed time as ms below one second, otherwise as seconds."""
    if seconds < 1.0:
        return f"{seconds * 1000:.0f} ms"
    return f"{seconds:.2f} s"


class _PreviewSignals(QObject):
    """Carries a worker's outcome and per-node progress back to the GUI thread."""

    finished = Signal(object)
    failed = Signal(str)
    progress = Signal(object)


class _PreviewWorker(QRunnable):
    """Runs the graph off the UI thread so heavy filters never freeze the canvas."""

    def __init__(self, workspace: Workspace, cache: NodeCache, signals: _PreviewSignals) -> None:
        super().__init__()
        self._workspace = workspace
        self._cache = cache
        self._signals = signals

    def run(self) -> None:  # standards: allow-framework-override
        try:
            result = run_workspace(
                self._workspace,
                cache=self._cache,
                skip_incomplete=True,
                progress=self._signals.progress.emit,
            )
        except Exception as error:  # boundary: report on the GUI thread, never crash the pool
            self._signals.failed.emit(str(error))
            return
        self._signals.finished.emit(result)
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

        self._preview_cache: NodeCache = {}
        self._pool = QThreadPool.globalInstance()
        self._preview_signals = _PreviewSignals()
        self._preview_running = False
        self._preview_dirty = False
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(_PREVIEW_DEBOUNCE_MS)

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
        self._scene.node_added.connect(self._on_node_added)
        self._scene.connection_failed.connect(self._console.error)
        self._scene.graph_changed.connect(self._on_graph_changed)
        self._inspector.parameter_changed.connect(self._schedule_preview)
        self._inspector.path_browse_requested.connect(self._browse_path)
        self._topbar.save_requested.connect(self._save_project)
        self._topbar.open_requested.connect(self._open_project)
        self._preview_timer.timeout.connect(self._launch_preview)
        self._preview_signals.finished.connect(self._on_preview_finished)
        self._preview_signals.failed.connect(self._on_preview_failed)
        self._preview_signals.progress.connect(self._on_preview_progress)

    # --- selection + live preview ------------------------------------------

    def _on_node_selected(self, node: Node | None) -> None:
        """Track the selected node, update the inspector, and refresh preview."""
        self._selected_node = node
        self._inspector.set_node(node)
        self._schedule_preview()

    def _on_node_added(self, node: Node) -> None:
        """React to a freshly dropped node without recomputing the whole graph.

        Only the cheap pipeline check always runs. A node with input ports cannot
        affect any preview until it is wired up, so it triggers no execution; a
        source node (no inputs) refreshes so its image appears right away.
        """
        self._check_pipeline()
        if not node.block.input_ports():
            self._schedule_preview()

    def _browse_path(self, node: Node) -> None:
        """Re-open the block's dialog to choose a new file path, then refresh."""
        path = choose_path(node.block, self)
        if path is None:
            return
        node.parameters["path"] = path
        self._inspector.set_node(node)
        self._schedule_preview()

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
        self._schedule_preview()

    def _schedule_preview(self) -> None:
        """Coalesce rapid edits into a single (re)start of the debounce timer.

        Every preview trigger — selection, parameter edit, connect/disconnect —
        funnels here so a burst of changes (e.g. a slider drag) launches just one
        background run once the changes settle.
        """
        self._preview_timer.start()

    def _launch_preview(self) -> None:
        """Run the graph off the UI thread, single-flighting overlapping requests.

        ORIGINAL shows the loaded source image; PROCESSED shows the selected node
        (or the latest producer). The heavy execution runs on a worker thread so
        the canvas stays responsive; a request arriving mid-run is deferred and
        replayed once the current run finishes.
        """
        if not self._scene.workspace.nodes:
            self._clear_preview()
            return
        if self._preview_running:
            self._preview_dirty = True
            return

        self._preview_running = True
        worker = _PreviewWorker(self._scene.workspace, self._preview_cache, self._preview_signals)
        self._pool.start(worker)

    def _on_preview_finished(self, result: ExecutionResult) -> None:
        """Apply a completed run's images, then replay any deferred request."""
        self._preview_running = False
        self._last_preview_error = None
        self._show_original(result)
        self._show_processed(result)
        self._relaunch_if_dirty()

    def _on_preview_failed(self, message: str) -> None:
        """Report a run failure once and clear the preview, then replay if dirty."""
        self._preview_running = False
        self._report_preview_error(message)
        self._clear_preview()
        self._relaunch_if_dirty()

    def _relaunch_if_dirty(self) -> None:
        """Start another run when edits arrived while the previous one was busy."""
        if self._preview_dirty:
            self._preview_dirty = False
            self._launch_preview()

    def _on_preview_progress(self, event: NodeProgress) -> None:
        """Log a computed node entering and leaving processing.

        Only nodes that actually run are reported (cache hits stay silent), so
        the console traces exactly where time goes — a visible progression of the
        pipeline and an explainable indicator during a heavy block's execution.
        """
        if event.phase == "start":
            self._console.info(f"▶ Calculando {event.display_name} ({event.node_id})…")
        else:
            self._console.success(
                f"✓ {event.display_name} ({event.node_id}) — {_format_elapsed(event.elapsed)}"
            )

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
        # A new graph reuses id schemes (e.g. ConvolutionBlock_1), so the prior
        # project's memo must not leak into it.
        self._preview_cache.clear()
        self._scene.load_workspace(workspace)
        self._console.success(f"Opened project from {path}.")

    # --- shortcuts ----------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent) -> None:  # standards: allow-framework-override
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self._scene.remove_selected()
            event.accept()
            return
        super().keyPressEvent(event)
