from __future__ import annotations

import os
import shutil
import subprocess
import sys
import winreg
from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.company import (
    APP_NAME,
    APP_PUBLISHER,
    APP_SHORT_NAME,
    APP_VERSION,
    ICON_PATH,
    LOGO_PATH,
    PNG_ICON_PATH,
)


class InstallWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(
        self,
        dest_dir: Path,
        create_desktop_shortcut: bool,
        create_start_shortcut: bool,
        register_uninstall: bool,
    ):
        super().__init__()
        self.dest_dir = dest_dir
        self.create_desktop_shortcut = create_desktop_shortcut
        self.create_start_shortcut = create_start_shortcut
        self.register_uninstall = register_uninstall

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
            if cand.exists() and ((cand / "TPexcelApp.exe").exists() or (cand / "TPexcelApp").exists()):
                return cand
        return base_dir

    def run(self):
        try:
            self.progress.emit(10, "Đang chuẩn bị thư mục đích...")
            self.dest_dir.mkdir(parents=True, exist_ok=True)

            payload = self._get_payload_path()
            self.progress.emit(25, f"Đang sao chép các tệp ứng dụng vào: {self.dest_dir}...")

            if payload.is_dir():
                items = list(payload.iterdir())
                total_items = max(1, len(items))
                for i, item in enumerate(items):
                    target = self.dest_dir / item.name
                    if item.is_dir():
                        if target.exists():
                            shutil.rmtree(target, ignore_errors=True)
                        shutil.copytree(item, target)
                    else:
                        shutil.copy2(item, target)
                    percent = 25 + int(40 * (i + 1) / total_items)
                    self.progress.emit(percent, f"Đang cài đặt: {item.name}")
            else:
                shutil.copy2(payload, self.dest_dir / payload.name)

            # Copy uninstaller if available in payload or dist
            base_dir = Path(__file__).resolve().parent
            uninstaller_src = None
            if hasattr(sys, "_MEIPASS"):
                cand = Path(sys._MEIPASS) / "uninstall.exe"
                if cand.exists():
                    uninstaller_src = cand
            if not uninstaller_src:
                cand = base_dir / "dist" / "uninstall.exe"
                if cand.exists():
                    uninstaller_src = cand

            if uninstaller_src and uninstaller_src.exists():
                shutil.copy2(uninstaller_src, self.dest_dir / "uninstall.exe")

            self.progress.emit(70, "Đang thiết lập phím tắt hệ thống Windows...")
            target_exe = self.dest_dir / "TPexcelApp.exe"
            if not target_exe.exists():
                target_exe = self.dest_dir / "TPexcelApp"

            exe_str = str(target_exe.resolve())
            work_dir = str(self.dest_dir.resolve())
            icon_arg = exe_str

            if sys.platform == "win32":
                if self.create_desktop_shortcut:
                    self.progress.emit(75, "Đang tạo lối tắt trên Desktop...")
                    ps_cmd = (
                        f"$ws = New-Object -ComObject WScript.Shell; "
                        f"$s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Thiên Phúc — Hóa đơn.lnk')); "
                        f"$s.TargetPath = '{exe_str}'; "
                        f"$s.WorkingDirectory = '{work_dir}'; "
                        f"$s.IconLocation = '{icon_arg},0'; "
                        f"$s.Description = 'Thiên Phúc — Hóa đơn bán hàng & Quản lý xe'; "
                        f"$s.Save()"
                    )
                    subprocess.run(
                        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                        capture_output=True,
                    )

                if self.create_start_shortcut:
                    self.progress.emit(82, "Đang tạo lối tắt trong Menu Start...")
                    ps_cmd = (
                        f"$ws = New-Object -ComObject WScript.Shell; "
                        f"$folder = [System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'Thiên Phúc'); "
                        f"if (!(Test-Path $folder)) {{ New-Item -ItemType Directory -Path $folder -Force | Out-Null }}; "
                        f"$s = $ws.CreateShortcut([System.IO.Path]::Combine($folder, 'Thiên Phúc — Hóa đơn.lnk')); "
                        f"$s.TargetPath = '{exe_str}'; "
                        f"$s.WorkingDirectory = '{work_dir}'; "
                        f"$s.IconLocation = '{icon_arg},0'; "
                        f"$s.Description = 'Thiên Phúc — Hóa đơn bán hàng & Quản lý xe'; "
                        f"$s.Save()"
                    )
                    subprocess.run(
                        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                        capture_output=True,
                    )

                if self.register_uninstall:
                    self.progress.emit(90, "Đang đăng ký vào danh sách ứng dụng Windows...")
                    self._register_in_registry(self.dest_dir, target_exe)

            self.progress.emit(95, "Đang hoàn thiện tệp hỗ trợ gỡ cài đặt...")
            self._create_uninstaller_script(self.dest_dir)

            self.progress.emit(100, "Cài đặt hoàn tất thành công!")
            self.finished.emit(True, "")
        except Exception as exc:
            self.finished.emit(False, str(exc))

    def _register_in_registry(self, dest_dir: Path, target_exe: Path) -> None:
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\TPexcel"
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_PUBLISHER)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(dest_dir))
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, f"{str(target_exe)},0")

                uninstaller_exe = dest_dir / "uninstall.exe"
                if uninstaller_exe.exists():
                    uninstall_cmd = f'"{str(uninstaller_exe)}"'
                else:
                    uninstall_cmd = f'"{str(dest_dir / "go_cai_dat.bat")}"'

                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)
                winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, f"{uninstall_cmd} --silent")
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)

                # Estimate size in KB
                total_bytes = sum(f.stat().st_size for f in dest_dir.rglob("*") if f.is_file())
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, int(total_bytes // 1024))
        except Exception as exc:
            print(f"Warning: Could not register in Windows Registry: {exc}")

    def _create_uninstaller_script(self, dest_dir: Path) -> None:
        bat_file = dest_dir / "go_cai_dat.bat"
        bat_content = (
            "@echo off\r\n"
            "chcp 65001 >nul\r\n"
            "title Gỡ cài đặt - Thiên Phúc\r\n"
            "echo ============================================================\r\n"
            "echo   ĐANG GỠ CÀI ĐẶT THIÊN PHÚC — HÓA ĐƠN BÁN HÀNG\r\n"
            "echo ============================================================\r\n"
            "echo [1/3] Đang xóa lối tắt Desktop và Start Menu...\r\n"
            "powershell -NoProfile -ExecutionPolicy Bypass -Command "
            "\"Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Thiên Phúc — Hóa đơn.lnk')) -ErrorAction SilentlyContinue; "
            "Remove-Item -Path ([System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'Thiên Phúc')) -Recurse -Force -ErrorAction SilentlyContinue\"\r\n"
            "echo [2/3] Đang xóa thông tin khỏi Windows Registry...\r\n"
            "reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\TPexcel\" /f >nul 2>&1\r\n"
            "echo [3/3] Đã dọn dẹp xong!\r\n"
            "echo.\r\n"
            "echo Đã gỡ cài đặt thành công phần mềm Thiên Phúc khỏi máy tính.\r\n"
            "pause\r\n"
        )
        bat_file.write_text(bat_content, encoding="utf-8")


class WizardInstallerWindow(QWidget):
    """A multi-step Modern Windows Wizard Installer for TPexcel."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Cài đặt {APP_NAME} — Setup Wizard")
        self.setFixedSize(620, 460)
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

        self.default_dir = Path(
            os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "TPexcel")
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top Header Banner
        self.header = QWidget()
        self.header.setStyleSheet("background: #107c41; color: white;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(24, 14, 24, 14)

        text_box = QVBoxLayout()
        self.lbl_banner_title = QLabel("Cài đặt Thiên Phúc — Hóa Đơn Bán Hàng")
        self.lbl_banner_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.lbl_banner_sub = QLabel("Trình hướng dẫn thiết lập ứng dụng trên Windows")
        self.lbl_banner_sub.setStyleSheet("font-size: 12px; color: #d4edda; margin-top: 2px;")
        text_box.addWidget(self.lbl_banner_title)
        text_box.addWidget(self.lbl_banner_sub)
        header_layout.addLayout(text_box, 1)

        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(LOGO_PATH)).scaled(
                70, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            header_layout.addWidget(logo_lbl)

        root.addWidget(self.header)

        # Center Stacked Pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #ffffff; padding: 10px;")

        self.page_welcome = self._create_welcome_page()
        self.page_dir = self._create_dir_page()
        self.page_options = self._create_options_page()
        self.page_ready = self._create_ready_page()
        self.page_installing = self._create_installing_page()
        self.page_finished = self._create_finished_page()

        self.stack.addWidget(self.page_welcome)     # Index 0
        self.stack.addWidget(self.page_dir)         # Index 1
        self.stack.addWidget(self.page_options)     # Index 2
        self.stack.addWidget(self.page_ready)       # Index 3
        self.stack.addWidget(self.page_installing)  # Index 4
        self.stack.addWidget(self.page_finished)    # Index 5

        root.addWidget(self.stack, 1)

        # Bottom Navigation Footer
        footer = QWidget()
        footer.setStyleSheet("background: #f3f2f1; border-top: 1px solid #e1dfdd;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        footer_layout.setSpacing(10)

        self.lbl_step = QLabel("Bước 1 / 4")
        self.lbl_step.setStyleSheet("color: #605e5c; font-size: 12px; font-weight: 600;")
        footer_layout.addWidget(self.lbl_step)

        footer_layout.addStretch(1)

        self.btn_back = QPushButton("< Quay lại")
        self.btn_back.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #8a8886; border-radius: 4px; padding: 7px 18px; font-weight: 600; font-size: 13px; }"
            "QPushButton:hover { background: #e1dfdd; }"
            "QPushButton:disabled { background: #f3f2f1; color: #a19f9d; border-color: #c8c6c4; }"
        )
        self.btn_back.clicked.connect(self._go_back)

        self.btn_next = QPushButton("Tiếp tục >")
        self.btn_next.setStyleSheet(
            "QPushButton { background: #107c41; color: white; border: none; border-radius: 4px; padding: 7px 22px; font-weight: bold; font-size: 13px; }"
            "QPushButton:hover { background: #0f6c38; }"
            "QPushButton:disabled { background: #c8c6c4; color: #605e5c; }"
        )
        self.btn_next.clicked.connect(self._go_next)

        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #8a8886; border-radius: 4px; padding: 7px 16px; font-weight: 600; font-size: 13px; color: #323130; }"
            "QPushButton:hover { background: #e1dfdd; }"
        )
        self.btn_cancel.clicked.connect(self.close)

        footer_layout.addWidget(self.btn_back)
        footer_layout.addWidget(self.btn_next)
        footer_layout.addWidget(self.btn_cancel)

        root.addWidget(footer)

        self.worker = None
        self._update_navigation_state()

    # ------------------ Pages Builder ------------------

    def _create_welcome_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(14)

        t1 = QLabel(f"Chào mừng bạn đến với chương trình cài đặt\n{APP_NAME}!")
        t1.setStyleSheet("font-size: 17px; font-weight: bold; color: #107c41; line-height: 1.3;")

        desc = QLabel(
            "Ứng dụng quản lý hóa đơn bán hàng và phân bổ hàng hóa lên các chuyến xe "
            "với giao diện Excel Editor trực quan, tự động tính dòng TỔNG CỘNG và xuất file chuẩn 1 trang Excel A4 ngang.\n\n"
            "Trình hướng dẫn (Setup Wizard) này sẽ từng bước thiết lập ứng dụng trên máy tính của bạn.\n\n"
            "Vui lòng đóng các phiên bản cũ của ứng dụng trước khi tiếp tục.\n"
            "Nhấn 'Tiếp tục >' để bắt đầu."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 13px; line-height: 1.5; color: #323130;")

        l.addWidget(t1)
        l.addWidget(desc)
        l.addStretch(1)
        return p

    def _create_dir_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(12)

        lbl = QLabel("Chọn thư mục cài đặt ứng dụng:")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #201f1e;")

        sub = QLabel("Ứng dụng sẽ được cài đặt vào thư mục dưới đây. Để cài vào thư mục khác, bấm 'Duyệt...'.")
        sub.setWordWrap(True)
        sub.setStyleSheet("font-size: 12px; color: #605e5c;")

        box = QHBoxLayout()
        box.setSpacing(8)
        self.txt_dest = QLineEdit(str(self.default_dir))
        self.txt_dest.setStyleSheet(
            "QLineEdit { border: 1.5px solid #c8c6c4; border-radius: 4px; padding: 6px 10px; background: white; font-size: 13px; }"
            "QLineEdit:focus { border-color: #107c41; }"
        )
        self.txt_dest.textChanged.connect(self._update_disk_space)

        btn_browse = QPushButton("Duyệt...")
        btn_browse.setStyleSheet(
            "QPushButton { background: #e1dfdd; border: 1px solid #8a8886; border-radius: 4px; padding: 6px 14px; font-weight: 600; font-size: 12px; }"
            "QPushButton:hover { background: #c8c6c4; }"
        )
        btn_browse.clicked.connect(self._browse)
        box.addWidget(self.txt_dest, 1)
        box.addWidget(btn_browse)

        self.lbl_space_req = QLabel("Dung lượng ổ đĩa yêu cầu: ~85 MB")
        self.lbl_space_req.setStyleSheet("font-size: 12px; color: #605e5c;")

        self.lbl_space_avail = QLabel("Dung lượng còn trống: Đang kiểm tra...")
        self.lbl_space_avail.setStyleSheet("font-size: 12px; color: #107c41; font-weight: 600;")

        l.addWidget(lbl)
        l.addWidget(sub)
        l.addLayout(box)
        l.addSpacing(10)
        l.addWidget(self.lbl_space_req)
        l.addWidget(self.lbl_space_avail)
        l.addStretch(1)

        self._update_disk_space()
        return p

    def _create_options_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(14)

        lbl = QLabel("Chọn các tác vụ bổ sung:")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #201f1e;")

        sub = QLabel("Chọn các tùy chọn bạn muốn Setup Wizard thực hiện trong quá trình cài đặt:")
        sub.setStyleSheet("font-size: 12px; color: #605e5c;")

        self.chk_desktop = QCheckBox("Tạo biểu tượng trên Màn hình nền (Desktop Shortcut)")
        self.chk_desktop.setChecked(True)
        self.chk_desktop.setStyleSheet("font-size: 13px; font-weight: 600; color: #323130;")

        self.chk_start = QCheckBox("Tạo biểu tượng trong Menu Start (Start Menu Shortcut)")
        self.chk_start.setChecked(True)
        self.chk_start.setStyleSheet("font-size: 13px; font-weight: 600; color: #323130;")

        self.chk_register = QCheckBox("Đăng ký vào Windows (hiển thị trong Settings > Installed apps để dễ gỡ bỏ)")
        self.chk_register.setChecked(True)
        self.chk_register.setStyleSheet("font-size: 13px; color: #323130;")

        l.addWidget(lbl)
        l.addWidget(sub)
        l.addSpacing(6)
        l.addWidget(self.chk_desktop)
        l.addWidget(self.chk_start)
        l.addWidget(self.chk_register)
        l.addStretch(1)
        return p

    def _create_ready_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 20, 20, 20)
        l.setSpacing(10)

        lbl = QLabel("Sẵn sàng cài đặt")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #201f1e;")

        sub = QLabel("Nhấn 'Cài đặt' để bắt đầu sao chép tệp ứng dụng vào máy tính của bạn.")
        sub.setStyleSheet("font-size: 12px; color: #605e5c;")

        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setStyleSheet(
            "QTextEdit { background: #faf9f8; border: 1px solid #d4d4d4; border-radius: 4px; padding: 10px; font-size: 12px; color: #323130; }"
        )

        l.addWidget(lbl)
        l.addWidget(sub)
        l.addWidget(self.txt_summary, 1)
        return p

    def _create_installing_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 24, 20, 20)
        l.setSpacing(14)

        lbl = QLabel("Đang tiến hành cài đặt...")
        lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #107c41;")

        self.lbl_status = QLabel("Đang chuẩn bị...")
        self.lbl_status.setStyleSheet("font-size: 12px; color: #605e5c;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #c8c6c4; border-radius: 4px; text-align: center; height: 22px; background: #edebe9; font-weight: 600; }"
            "QProgressBar::chunk { background-color: #107c41; border-radius: 3px; }"
        )

        l.addWidget(lbl)
        l.addWidget(self.lbl_status)
        l.addWidget(self.progress_bar)
        l.addStretch(1)
        return p

    def _create_finished_page(self) -> QWidget:
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 24, 20, 20)
        l.setSpacing(14)

        lbl = QLabel("🎉 Cài đặt hoàn tất thành công!")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #107c41;")

        desc = QLabel(
            f"Ứng dụng {APP_NAME} đã được cài đặt thành công vào máy tính của bạn.\n\n"
            "Bạn có thể mở ứng dụng bất cứ lúc nào từ biểu tượng trên Màn hình nền hoặc Menu Start."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 13px; line-height: 1.5; color: #323130;")

        self.chk_launch = QCheckBox("Khởi chạy Thiên Phúc ngay bây giờ")
        self.chk_launch.setChecked(True)
        self.chk_launch.setStyleSheet("font-size: 13px; font-weight: bold; color: #107c41; margin-top: 10px;")

        l.addWidget(lbl)
        l.addWidget(desc)
        l.addWidget(self.chk_launch)
        l.addStretch(1)
        return p

    # ------------------ Navigation Logic ------------------

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Chọn thư mục cài đặt", self.txt_dest.text())
        if d:
            self.txt_dest.setText(d)

    def _update_disk_space(self):
        try:
            path_str = self.txt_dest.text().strip()
            root_drive = Path(path_str).anchor or "C:\\"
            usage = shutil.disk_usage(root_drive)
            avail_gb = usage.free / (1024**3)
            self.lbl_space_avail.setText(f"Dung lượng còn trống trên ổ {root_drive}: {avail_gb:.1f} GB")
        except Exception:
            self.lbl_space_avail.setText("Dung lượng còn trống: Không xác định")

    def _update_summary(self):
        dest = self.txt_dest.text().strip()
        tasks = []
        if self.chk_desktop.isChecked():
            tasks.append("• Tạo lối tắt trên Màn hình nền (Desktop)")
        if self.chk_start.isChecked():
            tasks.append("• Tạo lối tắt trong Menu Start (Programs)")
        if self.chk_register.isChecked():
            tasks.append("• Đăng ký vào danh sách ứng dụng Windows (Add/Remove Programs)")

        content = (
            f"Thư mục cài đặt:\n  {dest}\n\n"
            f"Các tác vụ sẽ thực hiện:\n  " + "\n  ".join(tasks)
        )
        self.txt_summary.setPlainText(content)

    def _update_navigation_state(self):
        idx = self.stack.currentIndex()
        if idx == 0:
            self.lbl_step.setText("Bước 1 / 4: Chào mừng")
            self.btn_back.setEnabled(False)
            self.btn_next.setText("Tiếp tục >")
            self.btn_cancel.setEnabled(True)
        elif idx == 1:
            self.lbl_step.setText("Bước 2 / 4: Thư mục cài đặt")
            self.btn_back.setEnabled(True)
            self.btn_next.setText("Tiếp tục >")
            self.btn_cancel.setEnabled(True)
        elif idx == 2:
            self.lbl_step.setText("Bước 3 / 4: Tùy chọn")
            self.btn_back.setEnabled(True)
            self.btn_next.setText("Tiếp tục >")
            self.btn_cancel.setEnabled(True)
        elif idx == 3:
            self.lbl_step.setText("Bước 4 / 4: Xác nhận")
            self._update_summary()
            self.btn_back.setEnabled(True)
            self.btn_next.setText("Cài đặt")
            self.btn_cancel.setEnabled(True)
        elif idx == 4:
            self.lbl_step.setText("Đang cài đặt...")
            self.btn_back.setEnabled(False)
            self.btn_next.setEnabled(False)
            self.btn_cancel.setEnabled(False)
        elif idx == 5:
            self.lbl_step.setText("Hoàn tất")
            self.btn_back.setVisible(False)
            self.btn_next.setEnabled(True)
            self.btn_next.setText("Hoàn tất")
            self.btn_cancel.setVisible(False)

    def _go_next(self):
        idx = self.stack.currentIndex()
        if idx < 3:
            self.stack.setCurrentIndex(idx + 1)
            self._update_navigation_state()
        elif idx == 3:
            # Start installation
            dest = Path(self.txt_dest.text().strip())
            self.stack.setCurrentIndex(4)
            self._update_navigation_state()
            self._start_install(dest)
        elif idx == 5:
            # Finish
            if self.chk_launch.isChecked():
                dest = Path(self.txt_dest.text().strip())
                exe_target = dest / "TPexcelApp.exe"
                if not exe_target.exists():
                    exe_target = dest / "TPexcelApp"
                if exe_target.exists():
                    if sys.platform == "win32":
                        os.startfile(str(exe_target))
                    else:
                        subprocess.Popen([str(exe_target)])
            self.close()

    def _go_back(self):
        idx = self.stack.currentIndex()
        if idx > 0 and idx != 4:
            self.stack.setCurrentIndex(idx - 1)
            self._update_navigation_state()

    def _start_install(self, dest: Path):
        self.worker = InstallWorker(
            dest_dir=dest,
            create_desktop_shortcut=self.chk_desktop.isChecked(),
            create_start_shortcut=self.chk_start.isChecked(),
            register_uninstall=self.chk_register.isChecked(),
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, val: int, msg: str):
        self.progress_bar.setValue(val)
        self.lbl_status.setText(msg)

    def _on_finished(self, success: bool, err_msg: str):
        if success:
            self.stack.setCurrentIndex(5)
            self._update_navigation_state()
        else:
            QMessageBox.critical(self, "Lỗi cài đặt", f"Không thể hoàn tất quá trình cài đặt:\n{err_msg}")
            self.stack.setCurrentIndex(3)
            self._update_navigation_state()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    win = WizardInstallerWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
