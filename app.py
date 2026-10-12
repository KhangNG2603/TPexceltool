from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from core.company import APP_NAME, ICON_PATH, PNG_ICON_PATH
from ui.main_window import MainWindow


def main() -> None:
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ThienPhuc.TPexcel.App.1.0"
            )
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Thien Phuc Hoa Don")
    app.setApplicationDisplayName(APP_NAME)
    app.setStyle("Fusion")

    # Enforce consistent Excel Light Palette (prevents Windows Dark Mode from making text invisible)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#201f1e"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#fafafa"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#201f1e"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#201f1e"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#f3f2f1"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#201f1e"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#107c41"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#107c41"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    elif PNG_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(PNG_ICON_PATH)))

    win = MainWindow()

    if len(sys.argv) > 1:
        target_file = sys.argv[1].strip('\'"')
        if (
            target_file.lower().endswith(".xlsx")
            and not target_file.startswith("-")
            and Path(target_file).exists()
        ):
            win.load_file(target_file)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

