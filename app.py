from __future__ import annotations

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main() -> None:
    app = QApplication([])
    app.setApplicationName("Thien Phuc Hoa Don")
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
