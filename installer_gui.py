from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class InstallWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(
        self,
        dest_dir: str,
        create_desktop_shortcut: bool,
        create_start_shortcut: bool,
    ):
        super().__init__()
        self.dest_dir = Path(dest_dir)
        self.create_desktop_shortcut = create_desktop_shortcut
        self.create_start_shortcut = create_start_shortcut

    def _get_payload_path(self) -> Path:
        if hasattr(sys, "_MEIPASS"):
            meipass = Path(sys._MEIPASS)
            payload = meipass / "payload"
            if payload.exists():
                return payload

        base_dir = Path(__file__).resolve().parent
        candidates = [
            base_dir / "dist" / "TPexcelApp",
            base_dir / "payload",
            base_dir,
        ]
        for cand in candidates:
            if cand.exists() and (cand / "TPexcelApp.exe").exists() or (cand / "TPexcelApp").exists():
                return cand
        return base_dir

    def run(self):
        try:
            self.progress.emit(10, "Đang chuẩn bị thư mục cài đặt...")
            self.dest_dir.mkdir(parents=True, exist_ok=True)

            payload = self._get_payload_path()
            self.progress.emit(25, f"Đang sao chép các tệp ứng dụng vào: {self.dest_dir}")

            if payload.is_dir():
                for item in payload.iterdir():
                    target = self.dest_dir / item.name
                    if item.is_dir():
                        if target.exists():
                            shutil.rmtree(target, ignore_errors=True)
                        shutil.copytree(item, target)
                    else:
                        shutil.copy2(item, target)
            else:
                shutil.copy2(payload, self.dest_dir / payload.name)

            self.progress.emit(70, "Đang đăng ký Shortcut trên hệ thống Windows...")

            target_exe = self.dest_dir / "TPexcelApp.exe"
            if not target_exe.exists():
                target_exe = self.dest_dir / "TPexcelApp"

            if sys.platform == "win32":
                exe_str = str(target_exe.resolve())
                work_dir = str(self.dest_dir.resolve())

                if self.create_desktop_shortcut:
                    ps_cmd = (
                        f"$ws = New-Object -ComObject WScript.Shell; "
                        f"$s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'TPexcel.lnk')); "
                        f"$s.TargetPath = '{exe_str}'; "
                        f"$s.WorkingDirectory = '{work_dir}'; "
                        f"$s.Save()"
                    )
                    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True)

                if self.create_start_shortcut:
                    ps_cmd = (
                        f"$ws = New-Object -ComObject WScript.Shell; "
                        f"$s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('StartMenu'), 'Programs', 'TPexcel.lnk')); "
                        f"$s.TargetPath = '{exe_str}'; "
                        f"$s.WorkingDirectory = '{work_dir}'; "
                        f"$s.Save()"
                    )
                    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True)

            self.progress.emit(90, "Đang tạo công cụ gỡ cài đặt (Uninstaller)...")
            uninstaller_bat = self.dest_dir / "go_cai_dat.bat"
            uninstaller_content = (
                "@echo off\n"
                "chcp 65001 >nul\n"
                "title Gỡ cài đặt - TPexcel\n"
                "echo Đang xóa Shortcut...\n"
                "powershell -NoProfile -ExecutionPolicy Bypass -Command \"Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'TPexcel.lnk')) -ErrorAction SilentlyContinue\"\n"
                "powershell -NoProfile -ExecutionPolicy Bypass -Command \"Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('StartMenu'), 'Programs', 'TPexcel.lnk')) -ErrorAction SilentlyContinue\"\n"
                "echo Đã xóa shortcut khỏi Màn hình và Start Menu.\n"
                "pause\n"
            )
            uninstaller_bat.write_text(uninstaller_content, encoding="utf-8")

            self.progress.emit(100, "Cài đặt hoàn tất thành công!")
            self.finished.emit(True, "Cài đặt thành công!")
        except Exception as exc:
            self.finished.emit(False, str(exc))


class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cài đặt TPexcel — Thiên Phúc Hóa Đơn Bán Hàng")
        self.setFixedSize(580, 420)
        self.setStyleSheet("background-color: #f8f9fa; font-family: 'Segoe UI', Arial, sans-serif;")

        default_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "TPexcel")
        if sys.platform != "win32":
            default_dir = os.path.expanduser("~/TPexcel")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header Banner
        header = QWidget()
        header.setStyleSheet("background: #107c41; color: white;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)

        title = QLabel("Thiên Phúc — Hóa Đơn Bán Hàng")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

        subtitle = QLabel("Chương trình cài đặt ứng dụng TPexcel cho Windows")
        subtitle.setStyleSheet("font-size: 13px; color: #e1dfdd; margin-top: 4px;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        root.addWidget(header)

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(14)

        lbl_dest = QLabel("Thư mục cài đặt ứng dụng:")
        lbl_dest.setStyleSheet("font-weight: 600; font-size: 13px; color: #201f1e;")

        dest_box = QHBoxLayout()
        dest_box.setSpacing(8)
        self.txt_dest = QLineEdit(default_dir)
        self.txt_dest.setStyleSheet(
            "QLineEdit { border: 1px solid #c8c6c4; border-radius: 4px; padding: 6px 10px; background: white; font-size: 13px; }"
            "QLineEdit:focus { border: 1.5px solid #107c41; }"
        )
        btn_browse = QPushButton("Duyệt...")
        btn_browse.setStyleSheet(
            "QPushButton { background: #e1dfdd; border: 1px solid #8a8886; border-radius: 4px; padding: 6px 14px; font-weight: 600; font-size: 12px; }"
            "QPushButton:hover { background: #c8c6c4; }"
        )
        btn_browse.clicked.connect(self._browse)
        dest_box.addWidget(self.txt_dest, 1)
        dest_box.addWidget(btn_browse)

        self.chk_desktop = QCheckBox("Tạo biểu tượng shortcut trên Màn hình chính (Desktop)")
        self.chk_desktop.setChecked(True)
        self.chk_desktop.setStyleSheet("font-size: 13px; color: #323130;")

        self.chk_start = QCheckBox("Tạo biểu tượng shortcut trong Menu Start")
        self.chk_start.setChecked(True)
        self.chk_start.setStyleSheet("font-size: 13px; color: #323130;")

        self.chk_launch = QCheckBox("Tự động mở TPexcel sau khi cài đặt hoàn tất")
        self.chk_launch.setChecked(True)
        self.chk_launch.setStyleSheet("font-size: 13px; color: #323130; font-weight: 600;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #c8c6c4; border-radius: 4px; text-align: center; height: 20px; background: #edebe9; }"
            "QProgressBar::chunk { background-color: #107c41; border-radius: 3px; }"
        )

        self.lbl_status = QLabel("Sẵn sàng cài đặt.")
        self.lbl_status.setStyleSheet("font-size: 12px; color: #605e5c;")

        body_layout.addWidget(lbl_dest)
        body_layout.addLayout(dest_box)
        body_layout.addWidget(self.chk_desktop)
        body_layout.addWidget(self.chk_start)
        body_layout.addWidget(self.chk_launch)
        body_layout.addWidget(self.progress_bar)
        body_layout.addWidget(self.lbl_status)

        root.addWidget(body, 1)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background: #f3f2f1; border-top: 1px solid #e1dfdd;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        footer_layout.setSpacing(12)

        footer_layout.addStretch(1)

        self.btn_install = QPushButton("Cài đặt ngay")
        self.btn_install.setStyleSheet(
            "QPushButton { background: #107c41; color: white; border: none; border-radius: 4px; padding: 8px 24px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background: #0f6c38; }"
            "QPushButton:disabled { background: #c8c6c4; color: #605e5c; }"
        )
        self.btn_install.clicked.connect(self._start_install)

        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #8a8886; border-radius: 4px; padding: 8px 18px; font-weight: 600; font-size: 13px; color: #323130; }"
            "QPushButton:hover { background: #f3f2f1; }"
        )
        self.btn_cancel.clicked.connect(self.close)

        footer_layout.addWidget(self.btn_install)
        footer_layout.addWidget(self.btn_cancel)

        root.addWidget(footer)

        self.worker = None
        self.installed_exe = None

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Chọn thư mục cài đặt", self.txt_dest.text())
        if d:
            self.txt_dest.setText(d)

    def _start_install(self):
        if self.btn_install.text() == "Hoàn tất":
            if self.chk_launch.isChecked() and self.installed_exe and os.path.exists(self.installed_exe):
                if sys.platform == "win32":
                    os.startfile(self.installed_exe)
                else:
                    subprocess.Popen([self.installed_exe])
            self.close()
            return

        dest = self.txt_dest.text().strip()
        if not dest:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thư mục cài đặt.")
            return

        self.btn_install.setEnabled(False)
        self.txt_dest.setEnabled(False)
        self.chk_desktop.setEnabled(False)
        self.chk_start.setEnabled(False)

        self.worker = InstallWorker(
            dest_dir=dest,
            create_desktop_shortcut=self.chk_desktop.isChecked(),
            create_start_shortcut=self.chk_start.isChecked(),
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, val: int, msg: str):
        self.progress_bar.setValue(val)
        self.lbl_status.setText(msg)

    def _on_finished(self, success: bool, msg: str):
        if success:
            dest = Path(self.txt_dest.text().strip())
            exe_name = "TPexcelApp.exe" if sys.platform == "win32" else "TPexcelApp"
            self.installed_exe = str(dest / exe_name)

            self.progress_bar.setValue(100)
            self.lbl_status.setText("✅ Cài đặt hoàn tất thành công!")
            self.btn_install.setText("Hoàn tất")
            self.btn_install.setEnabled(True)
            self.btn_cancel.setVisible(False)
        else:
            QMessageBox.critical(self, "Lỗi cài đặt", f"Không thể hoàn tất cài đặt:\n{msg}")
            self.btn_install.setEnabled(True)
            self.txt_dest.setEnabled(True)
            self.chk_desktop.setEnabled(True)
            self.chk_start.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    win = InstallerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
