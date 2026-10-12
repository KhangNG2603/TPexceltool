from __future__ import annotations

import os
import shutil
import subprocess
import sys
import winreg
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.company import (
    APP_NAME,
    ICON_PATH,
    LOGO_PATH,
    PNG_ICON_PATH,
)


class UninstallWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, install_dir: Path, del_files: bool):
        super().__init__()
        self.install_dir = install_dir
        self.del_files = del_files

    def run(self):
        try:
            self.progress.emit(20, "Đang xóa các lối tắt trên Desktop & Start Menu...")
            if sys.platform == "win32":
                ps_cmd = (
                    "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Thiên Phúc — Hóa đơn.lnk')) -ErrorAction SilentlyContinue; "
                    "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'TPexcel.lnk')) -ErrorAction SilentlyContinue; "
                    "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'Thiên Phúc')) -Recurse -Force -ErrorAction SilentlyContinue; "
                    "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'TPexcel.lnk')) -ErrorAction SilentlyContinue; "
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                    capture_output=True,
                )

            self.progress.emit(50, "Đang xóa thông tin ứng dụng khỏi Windows Registry...")
            try:
                reg_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\TPexcel"
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except Exception:
                pass

            self.progress.emit(80, "Đang thiết lập dọn dẹp thư mục cài đặt...")
            if self.del_files and self.install_dir.exists():
                # Launch detached cleanup script to delete install_dir after uninstaller exits
                cleanup_bat = Path(os.environ.get("TEMP", ".")) / "tpexcel_cleanup.bat"
                dir_str = str(self.install_dir.resolve())
                bat_code = (
                    "@echo off\r\n"
                    "timeout /t 1 /nobreak >nul\r\n"
                    f'rmdir /s /q "{dir_str}" >nul 2>&1\r\n'
                    "del \"%~f0\" >nul 2>&1\r\n"
                )
                cleanup_bat.write_text(bat_code, encoding="utf-8")
                subprocess.Popen(
                    ["cmd.exe", "/c", str(cleanup_bat)],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )

            self.progress.emit(100, "Gỡ cài đặt hoàn tất thành công!")
            self.finished.emit(True, "")
        except Exception as exc:
            self.finished.emit(False, str(exc))


class UninstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gỡ cài đặt Thiên Phúc — Hóa đơn bán hàng")
        self.setFixedSize(540, 360)
        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f8f9fa;
                color: #201f1e;
            }
            """
        )

        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        elif PNG_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(PNG_ICON_PATH)))

        if getattr(sys, "frozen", False):
            self.install_dir = Path(sys.executable).resolve().parent
        else:
            self.install_dir = Path(__file__).resolve().parent

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: #c53929; color: white;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)

        t_box = QVBoxLayout()
        lbl_title = QLabel("Gỡ cài đặt ứng dụng Thiên Phúc")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        lbl_sub = QLabel("Xóa ứng dụng và các lối tắt khỏi máy tính của bạn")
        lbl_sub.setStyleSheet("font-size: 12px; color: #fce8e6; margin-top: 2px;")
        t_box.addWidget(lbl_title)
        t_box.addWidget(lbl_sub)
        header_layout.addLayout(t_box, 1)

        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(LOGO_PATH)).scaled(
                65, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            header_layout.addWidget(logo_lbl)

        root.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet("background: #ffffff;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(12)

        self.lbl_prompt = QLabel(
            f"Bạn có chắc chắn muốn gỡ cài đặt hoàn toàn phần mềm <b>{APP_NAME}</b> khỏi hệ thống?\n\n"
            f"Thư mục ứng dụng: <code>{self.install_dir}</code>"
        )
        self.lbl_prompt.setWordWrap(True)
        self.lbl_prompt.setStyleSheet("font-size: 13px; color: #323130; line-height: 1.4;")

        self.chk_del_files = QCheckBox("Xóa toàn bộ tệp ứng dụng trong thư mục cài đặt")
        self.chk_del_files.setChecked(True)
        self.chk_del_files.setStyleSheet("font-size: 13px; font-weight: 600; color: #323130;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #c8c6c4; border-radius: 4px; text-align: center; height: 20px; background: #edebe9; }"
            "QProgressBar::chunk { background-color: #c53929; border-radius: 3px; }"
        )

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-size: 12px; color: #605e5c;")
        self.lbl_status.setVisible(False)

        body_layout.addWidget(self.lbl_prompt)
        body_layout.addWidget(self.chk_del_files)
        body_layout.addWidget(self.progress_bar)
        body_layout.addWidget(self.lbl_status)
        body_layout.addStretch(1)

        root.addWidget(body, 1)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background: #f3f2f1; border-top: 1px solid #e1dfdd;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        footer_layout.setSpacing(10)

        footer_layout.addStretch(1)

        self.btn_uninstall = QPushButton("Gỡ cài đặt")
        self.btn_uninstall.setStyleSheet(
            "QPushButton { background: #c53929; color: white; border: none; border-radius: 4px; padding: 7px 20px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background: #a52714; }"
            "QPushButton:disabled { background: #e1dfdd; color: #8a8886; }"
        )
        self.btn_uninstall.clicked.connect(self._start_uninstall)

        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #8a8886; border-radius: 4px; padding: 7px 18px; font-weight: 600; font-size: 13px; color: #323130; }"
            "QPushButton:hover { background: #e1dfdd; }"
        )
        self.btn_cancel.clicked.connect(self.close)

        footer_layout.addWidget(self.btn_uninstall)
        footer_layout.addWidget(self.btn_cancel)

        root.addWidget(footer)

        self.worker = None

    def _start_uninstall(self):
        if self.btn_uninstall.text() == "Đóng":
            self.close()
            return

        self.btn_uninstall.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.chk_del_files.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_status.setVisible(True)

        self.worker = UninstallWorker(self.install_dir, self.chk_del_files.isChecked())
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, val: int, msg: str):
        self.progress_bar.setValue(val)
        self.lbl_status.setText(msg)

    def _on_finished(self, success: bool, err_msg: str):
        if success:
            self.lbl_prompt.setText("✅ <b>Đã gỡ cài đặt thành công!</b><br>Phần mềm Thiên Phúc và các lối tắt đã được dọn dẹp sạch sẽ khỏi máy tính.")
            self.btn_uninstall.setText("Đóng")
            self.btn_uninstall.setStyleSheet(
                "QPushButton { background: #107c41; color: white; border: none; border-radius: 4px; padding: 7px 22px; font-weight: bold; font-size: 13px; }"
                "QPushButton:hover { background: #0f6c38; }"
            )
            self.btn_uninstall.setEnabled(True)
            self.btn_cancel.setVisible(False)
        else:
            QMessageBox.critical(self, "Lỗi khi gỡ cài đặt", f"Không thể hoàn tất gỡ cài đặt:\n{err_msg}")
            self.btn_uninstall.setEnabled(True)
            self.btn_cancel.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if "--silent" in sys.argv:
        # Silent uninstall mode
        worker = UninstallWorker(Path(sys.executable).resolve().parent, del_files=True)
        worker.run()
        sys.exit(0)

    win = UninstallerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
