"""Modal dialog to pick, preview, and confirm an image before loading it as PGM.

Used when a Load PGM block is dropped onto the canvas: the user selects any
OpenCV-readable image, which is converted to PGM (PGM sources pass through), then
reviews a thumbnail and the PGM metadata (format, grayscale depth, dimensions,
size) and confirms. The rest of the pipeline always works on the PGM version.
`choose` is the entry point — it returns the accepted PGM path or None if the
user cancels at any step.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
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
from src.gui.panels.image_viewer import to_grayscale_qimage
from src.infrastructure.image_loader import ensure_pgm
from src.infrastructure.pgm_codec import read_pgm_file, read_pgm_header

_PREVIEW_SIZE = QSize(360, 170)
_IMAGE_FILTER = (
    "Imagens (*.pgm *.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff);;Todos os arquivos (*)"
)


class LoadPgmDialog(QDialog):
    """A file selector with live preview and metadata for a single PGM image."""

    def __init__(self, file_path: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Abrir imagem PGM")
        self.setModal(True)
        self.setMinimumWidth(420)
        self._path: str | None = None

        self._file_label = QLabel()
        self._preview = QLabel()
        self._format_value = QLabel()
        self._bits_value = QLabel()
        self._dimension_value = QLabel()
        self._size_value = QLabel()
        self._add_button = QPushButton("Adicionar ao Workspace")

        self._build_ui()
        self._load(file_path)

    @classmethod
    def choose(cls, parent: QWidget | None = None) -> str | None:
        """Run the full select→preview→confirm flow, returning the chosen path."""
        path = cls._pick_file(parent)
        if path is None:
            return None

        dialog = cls(path, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog._path
        return None

    @property
    def selected_path(self) -> str | None:
        """The confirmed file path, or None while unset/invalid."""
        return self._path

    # --- layout -------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)
        layout.addWidget(dialog_title("Abrir imagem PGM"))
        layout.addWidget(self._file_section())
        layout.addWidget(self._preview_section())
        layout.addWidget(self._info_section())
        layout.addLayout(self._button_row())

    def _file_section(self) -> QWidget:
        self._file_label.setStyleSheet(f"color: {theme.TEXT};")
        change_button = QPushButton("Trocar")
        change_button.clicked.connect(self._change_file)

        row = QHBoxLayout()
        row.addWidget(self._file_label, 1)
        row.addWidget(change_button)
        return titled_section("ARQUIVO SELECIONADO", framed(row))

    def _preview_section(self) -> QWidget:
        self._preview.setFixedHeight(_PREVIEW_SIZE.height())
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setStyleSheet(
            f"background-color: {theme.BACKGROUND}; color: {theme.TEXT_DISABLED};"
            f" border: 1px solid {theme.BORDER}; border-radius: 6px;"
        )
        return titled_section("PRÉ-VISUALIZAÇÃO", self._preview)

    def _info_section(self) -> QWidget:
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(8)

        cells = [
            (0, 0, "Formato:", self._format_value),
            (0, 2, "Escala de cinza:", self._bits_value),
            (1, 0, "Dimensão:", self._dimension_value),
            (1, 2, "Tamanho:", self._size_value),
        ]
        for row, column, caption, value_label in cells:
            caption_label = QLabel(caption)
            caption_label.setStyleSheet(f"color: {theme.TEXT_MUTED};")
            value_label.setStyleSheet(f"color: {theme.TEXT}; font-weight: 600;")
            grid.addWidget(caption_label, row, column)
            grid.addWidget(value_label, row, column + 1)

        return titled_section("INFORMAÇÕES", framed(grid))

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

    # --- file loading -------------------------------------------------------

    def _change_file(self) -> None:
        path = self._pick_file(self)
        if path is not None:
            self._load(path)

    def _load(self, source_path: str) -> None:
        """Convert the chosen image to PGM and show its preview and metadata.

        The label keeps the originally chosen file name, while every downstream
        value (and the node) uses the converted PGM path.
        """
        self._file_label.setText(Path(source_path).name)
        try:
            pgm_path = str(ensure_pgm(source_path))
            matrix = read_pgm_file(pgm_path)
            header = read_pgm_header(pgm_path)
        except (ValueError, OSError) as error:
            self._show_invalid(str(error))
            return

        self._path = pgm_path
        self._show_preview(matrix)
        self._show_info(pgm_path, header)
        self._add_button.setEnabled(True)

    def _show_preview(self, matrix: list[list[int]]) -> None:
        pixmap = QPixmap.fromImage(to_grayscale_qimage(matrix))
        scaled = pixmap.scaled(
            _PREVIEW_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview.setPixmap(scaled)

    def _show_info(self, file_path: str, header: tuple[int, int, int]) -> None:
        width, height, max_value = header
        size_kb = round(Path(file_path).stat().st_size / 1024)

        self._format_value.setText("PGM")
        self._bits_value.setText(f"{max(1, max_value.bit_length())} bits")
        self._dimension_value.setText(f"{width} × {height}")
        self._size_value.setText(f"{size_kb} KB")

    def _show_invalid(self, message: str) -> None:
        self._path = None
        self._add_button.setEnabled(False)
        self._preview.setPixmap(QPixmap())
        self._preview.setText("Arquivo inválido")
        self._preview.setToolTip(message)
        for value_label in (self._format_value, self._bits_value,
                             self._dimension_value, self._size_value):
            value_label.setText("—")

    @staticmethod
    def _pick_file(parent: QWidget | None) -> str | None:
        path, _ = QFileDialog.getOpenFileName(parent, "Selecionar imagem", "", _IMAGE_FILTER)
        return path or None
