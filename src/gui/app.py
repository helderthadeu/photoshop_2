"""Application bootstrap: build the Qt application and show the main window."""
import sys

from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def run() -> int:
    """Launch the PSE-Image GUI and block until the window closes.

    Returns:
        The Qt application exit code.
    """
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()
