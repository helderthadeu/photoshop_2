"""Modal dialog to choose and confirm a destination before adding a Save PGM sink.

Mirrors the Load PGM dialog's look, adapted for an output: there is no image to
preview at creation time (the result is produced when the flow runs), so the
dialog confirms the destination path and shows where the PGM will be written.
`choose` is the entry point — it returns the accepted path or None if the user
cancels at any step.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.gui import theme
from src.gui.dialogs.layout_helpers import dialog_title, framed, titled_section

_PGM_FILTER = "PGM Image (*.pgm)"


class SavePgmDialog(QDialog):
    """A destination chooser for the PGM a Save block will write."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Salvar imagem PGM")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._path: str | None = None

        self._file_label = QLabel()
        self._format_value = QLabel()
        self._name_value = QLabel()
        self._location_value = QLabel()
        self._add_button = QPushButton("Adicionar ao Workspace")

        self._build_ui()
        self._show_destination(file_path)

    @classmethod
    def choose(cls, parent: QWidget | None = None) -> str | None:
        """Run the full choose→confirm flow, returning the destination path."""
        path = cls._pick_destination(parent)
        if path is None:
            return None

        dialog = cls(path, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog._path
        return None

    @property
    def selected_path(self) -> str | None:
        """The confirmed destination path, or None while unset."""
        return self._path

    # --- layout -------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        layout.addWidget(dialog_title("Salvar imagem PGM"))
        layout.addWidget(self._destination_section())
        layout.addWidget(self._info_section())
        layout.addWidget(self._hint_label())
        layout.addLayout(self._button_row())

    def _destination_section(self) -> QWidget:
        self._file_label.setStyleSheet(f"color: {theme.TEXT};")
        change_button = QPushButton("Trocar")
        change_button.clicked.connect(self._change_destination)

        row = QHBoxLayout()
        row.addWidget(self._file_label, 1)
        row.addWidget(change_button)
        return titled_section("ARQUIVO DE DESTINO", framed(row))

    def _info_section(self) -> QWidget:
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)

        cells = [
            (0, 0, "Formato:", self._format_value),
            (0, 2, "Nome:", self._name_value),
            (1, 0, "Local:", self._location_value),
        ]
        for row, column, caption, value_label in cells:
            caption_label = QLabel(caption)
            caption_label.setStyleSheet(f"color: {theme.TEXT_MUTED};")
            value_label.setStyleSheet(f"color: {theme.TEXT}; font-weight: 600;")
            value_label.setWordWrap(True)
            grid.addWidget(caption_label, row, column)
            grid.addWidget(value_label, row, column + 1)

        return titled_section("INFORMAÇÕES", framed(grid))

    def _hint_label(self) -> QLabel:
        hint = QLabel("A imagem processada será gravada neste arquivo ao executar o fluxo.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {theme.TEXT_DISABLED};")
        return hint

    def _button_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch(1)

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        self._add_button.setProperty("accent", "true")
        self._add_button.setEnabled(False)
        self._add_button.clicked.connect(self.accept)

        row.addWidget(cancel_button)
        row.addWidget(self._add_button)
        return row

    # --- destination handling ----------------------------------------------

    def _change_destination(self) -> None:
        path = self._pick_destination(self)
        if path is not None:
            self._show_destination(path)

    def _show_destination(self, file_path: str) -> None:
        destination = Path(file_path)
        self._path = file_path
        self._file_label.setText(destination.name)
        self._format_value.setText("PGM")
        self._name_value.setText(destination.name)
        self._location_value.setText(str(destination.parent))
        self._add_button.setEnabled(True)

    @staticmethod
    def _pick_destination(parent: QWidget | None) -> str | None:
        path, _ = QFileDialog.getSaveFileName(parent, "Salvar imagem PGM", "", _PGM_FILTER)
        if not path:
            return None
        if not path.lower().endswith(".pgm"):
            path += ".pgm"
        return path
