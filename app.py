from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
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

