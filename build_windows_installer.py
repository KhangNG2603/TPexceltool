#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)

    print("============================================================")
    print(" 🛠️  ĐANG ĐÓNG GÓI BỘ CÀI ĐẶT TPEXCEL CHO WINDOWS")
    print("============================================================")

    pyinstaller = base_dir / ".venv" / "bin" / "pyinstaller"
    if sys.platform == "win32":
        pyinstaller = base_dir / ".venv" / "Scripts" / "pyinstaller.exe"

    if not pyinstaller.exists():
        pyinstaller_str = "pyinstaller"
    else:
        pyinstaller_str = str(pyinstaller)

    print("\n[Step 1/2] Đang đóng gói Payload ứng dụng chính (TPexcelApp)...")
    res1 = subprocess.run([pyinstaller_str, "--noconfirm", "TPexcelApp.spec"])
    if res1.returncode != 0:
        print("❌ Lỗi khi đóng gói TPexcelApp payload.")
        sys.exit(res1.returncode)

    payload_dir = base_dir / "dist" / "TPexcelApp"
    if not payload_dir.exists():
        print(f"❌ Không tìm thấy thư mục payload: {payload_dir}")
        sys.exit(1)

    print("\n[Step 2/2] Đang đóng gói tệp cài đặt duy nhất (TPexcel.exe)...")
    res2 = subprocess.run([pyinstaller_str, "--noconfirm", "TPexcelInstaller.spec"])
    if res2.returncode != 0:
        print("❌ Lỗi khi đóng gói TPexcelInstaller.")
        sys.exit(res2.returncode)

    out_exe = base_dir / "dist" / "TPexcel.exe"
    out_bin = base_dir / "dist" / "TPexcel"

    final_target = out_exe if out_exe.exists() else out_bin
    if final_target.exists():
        print("\n============================================================")
        print(" 🎉 THÀNH CÔNG! ĐÃ TẠO TỆP CÀI ĐẶT DUY NHẤT:")
        print(f" 👉 {final_target.resolve()}")
        print(" Windows user chỉ cần tải file này về và nhấp đúp để cài đặt.")
        print("============================================================")
    else:
        print("❌ Không tìm thấy tệp đầu ra TPexcel.exe sau khi đóng gói.")


if __name__ == "__main__":
    main()
