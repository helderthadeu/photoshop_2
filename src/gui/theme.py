"""Visual theme: dark palette, category colours, fonts, and the global stylesheet.

This module is the single source of truth for the PSE-Image Studio look — a
technical, DaVinci-Fusion-inspired dark interface. Widgets read colours from the
named constants here; the whole application stylesheet is produced by
`build_stylesheet`. Keeping every colour in one place means a re-skin touches
only this file.
"""
from PySide6.QtGui import QColor, QFont

__all__ = [
    "BACKGROUND",
    "BACKGROUND_ALT",
    "PANEL",
    "PANEL_RAISED",
    "BORDER",
    "TEXT",
    "TEXT_MUTED",
    "TEXT_DISABLED",
    "ACCENT",
    "ACCENT_HOVER",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CATEGORY_COLORS",
    "DEFAULT_CATEGORY_COLOR",
    "category_color",
    "UI_FONT_FAMILY",
    "MONO_FONT_FAMILY",
    "ui_font",
    "mono_font",
    "build_stylesheet",
]

# --- Surfaces ---------------------------------------------------------------
BACKGROUND = "#15191F"
BACKGROUND_ALT = "#1E232B"
PANEL = "#20252D"
PANEL_RAISED = "#272D36"
BORDER = "#3A414D"

# --- Text -------------------------------------------------------------------
TEXT = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"
TEXT_DISABLED = "#6B7280"

# --- Action colours ---------------------------------------------------------
ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
ERROR = "#EF4444"

# --- Block category colours -------------------------------------------------
# Keys match Block.category strings declared by the registered blocks.
CATEGORY_COLORS: dict[str, str] = {
    "Interface": "#3B82F6",
    "Point": "#8B5CF6",
    "Local": "#F97316",
    "Analysis": "#22C55E",
}
DEFAULT_CATEGORY_COLOR = "#6B7280"

# --- Fonts ------------------------------------------------------------------
UI_FONT_FAMILY = "Segoe UI"
MONO_FONT_FAMILY = "Consolas"


def category_color(category: str) -> QColor:
    """Return the accent colour for a block category, or the disabled grey.

    Args:
        category: The block's declared category string.

    Returns:
        A QColor; unknown categories map to `DEFAULT_CATEGORY_COLOR`.
    """
    hex_value = CATEGORY_COLORS.get(category, DEFAULT_CATEGORY_COLOR)
    return QColor(hex_value)


def ui_font(size: int = 12, *, semibold: bool = False) -> QFont:
    """Build the standard interface font at the given point size."""
    font = QFont(UI_FONT_FAMILY, size)
    font.setWeight(QFont.Weight.DemiBold if semibold else QFont.Weight.Normal)
    return font


def mono_font(size: int = 11) -> QFont:
    """Build the monospaced font used for logs and numeric matrices."""
    return QFont(MONO_FONT_FAMILY, size)


def build_stylesheet() -> str:
    """Assemble the full application stylesheet from the palette constants.

    Returns:
        A Qt Style Sheet string applied once on the QApplication.
    """
    sections = [
        _base_stylesheet(),
        _topbar_stylesheet(),
        _dock_stylesheet(),
        _input_stylesheet(),
        _button_stylesheet(),
        _list_and_tree_stylesheet(),
        _scrollbar_stylesheet(),
    ]
    return "\n".join(sections)


def _topbar_stylesheet() -> str:
    """The application header strip; one flat bar with a single bottom border.

    Styling the bar through its object name (rather than a bare per-widget
    stylesheet) keeps the background from leaking onto child widgets, which is
    what otherwise draws a visible box around the title.
    """
    return f"""
    QWidget#TopBar {{
        background-color: {BACKGROUND_ALT};
        border-bottom: 1px solid {BORDER};
    }}
    QWidget#TopBar QLabel {{
        background: transparent;
        border: none;
    }}
    QLabel#TopBarTitle {{
        color: {TEXT};
        font-size: 18px;
        font-weight: 600;
    }}
    QLabel#TopBarSubtitle {{
        color: {TEXT_MUTED};
        font-size: 11px;
    }}
    """


def _base_stylesheet() -> str:
    """Window, panels, labels, and tooltips."""
    return f"""
    QMainWindow, QWidget {{
        background-color: {BACKGROUND};
        color: {TEXT};
        font-family: "{UI_FONT_FAMILY}";
        font-size: 12px;
    }}
    QLabel {{
        background: transparent;
        color: {TEXT};
    }}
    QToolTip {{
        background-color: {PANEL_RAISED};
        color: {TEXT};
        border: 1px solid {BORDER};
        padding: 4px;
    }}
    QSplitter::handle {{
        background-color: {BACKGROUND};
    }}
    QSplitter::handle:hover {{
        background-color: {BORDER};
    }}
    """


def _dock_stylesheet() -> str:
    """Dock widgets and their title bars."""
    return f"""
    QDockWidget {{
        color: {TEXT_MUTED};
        font-size: 11px;
        font-weight: 600;
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
    }}
    QDockWidget::title {{
        background-color: {BACKGROUND_ALT};
        padding: 6px 10px;
        border-bottom: 1px solid {BORDER};
    }}
    """


def _input_stylesheet() -> str:
    """Line edits, spin boxes, and combo boxes."""
    return f"""
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit {{
        background-color: {BACKGROUND_ALT};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 4px 6px;
        selection-background-color: {ACCENT};
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border: 1px solid {ACCENT};
    }}
    QComboBox QAbstractItemView {{
        background-color: {PANEL_RAISED};
        color: {TEXT};
        selection-background-color: {ACCENT};
        border: 1px solid {BORDER};
    }}
    """


def _button_stylesheet() -> str:
    """Push buttons and the primary (accented) variant."""
    return f"""
    QPushButton {{
        background-color: {PANEL_RAISED};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 5px 12px;
    }}
    QPushButton:hover {{
        background-color: {BORDER};
    }}
    QPushButton:pressed {{
        background-color: {BACKGROUND_ALT};
    }}
    QPushButton[accent="true"] {{
        background-color: {ACCENT};
        border: 1px solid {ACCENT};
        color: #FFFFFF;
        font-weight: 600;
    }}
    QPushButton[accent="true"]:hover {{
        background-color: {ACCENT_HOVER};
        border: 1px solid {ACCENT_HOVER};
    }}
    """


def _list_and_tree_stylesheet() -> str:
    """Block library list/tree styling."""
    return f"""
    QListWidget, QTreeWidget, QTreeView, QListView {{
        background-color: {PANEL};
        color: {TEXT};
        border: none;
        outline: 0;
    }}
    QListWidget::item, QTreeWidget::item {{
        padding: 5px 6px;
        border-radius: 4px;
    }}
    QListWidget::item:hover, QTreeWidget::item:hover {{
        background-color: {PANEL_RAISED};
    }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background-color: {ACCENT};
        color: #FFFFFF;
    }}
    QHeaderView::section {{
        background-color: {BACKGROUND_ALT};
        color: {TEXT_MUTED};
        border: none;
        padding: 4px;
    }}
    """


def _scrollbar_stylesheet() -> str:
    """Slim, unobtrusive scrollbars."""
    return f"""
    QScrollBar:vertical {{
        background: {BACKGROUND};
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_DISABLED};
    }}
    QScrollBar:horizontal {{
        background: {BACKGROUND};
        height: 10px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER};
        border-radius: 5px;
        min-width: 24px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        height: 0;
        width: 0;
    }}
    """
