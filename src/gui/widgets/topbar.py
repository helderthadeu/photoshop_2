"""Application top bar: product identity on the left, primary actions on the right.

Emits intent signals (`open_requested`, `save_requested`) for project I/O so the
main window owns the behaviour while this widget stays presentational. Graph
execution is continuous (live preview), so there is no run action.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class TopBar(QWidget):
    """The fixed header strip with branding and the open/save project actions."""

    open_requested = Signal()
    save_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("TopBar")
        self.setFixedHeight(54)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.addLayout(self._build_identity())
        layout.addStretch(1)
        layout.addLayout(self._build_actions())

    def _build_identity(self) -> QVBoxLayout:
        identity = QVBoxLayout()
        identity.setSpacing(0)

        title = QLabel("PSE-Image Studio")
        title.setObjectName("TopBarTitle")
        subtitle = QLabel("Visual Image Processing Environment")
        subtitle.setObjectName("TopBarSubtitle")

        identity.addWidget(title)
        identity.addWidget(subtitle)
        return identity

    def _build_actions(self) -> QHBoxLayout:
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        open_button = QPushButton("Open Project")
        open_button.clicked.connect(self.open_requested.emit)
        save_button = QPushButton("Save Project")
        save_button.setProperty("accent", "true")
        save_button.clicked.connect(self.save_requested.emit)

        actions.addWidget(open_button)
        actions.addWidget(save_button)
        return actions
