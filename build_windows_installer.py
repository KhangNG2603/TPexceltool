import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Fix Windows console UTF-8 printing
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


def generate_icon_if_needed(base_dir: Path):
    ico = base_dir / "assets" / "app_icon.ico"
    png = base_dir / "assets" / "logo-thien-phuc.png"
    if not ico.exists() and png.exists():
        print("🎨 Đang tạo biểu tượng ứng dụng Windows (app_icon.ico)...")
        from PIL import Image, ImageDraw

        size = 256
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)

        # Rounded green background
        margin = 8
        draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=36, fill=(16, 124, 65, 255))

        # Inner white card
        inner_m = 24
        draw.rounded_rectangle([inner_m, inner_m, size - inner_m, size - inner_m], radius=24, fill=(255, 255, 255, 255))

        # Paste logo
        logo = Image.open(png).convert("RGBA")
        max_w = (size - 2 * inner_m) - 20
        max_h = (size - 2 * inner_m) - 20
        ratio = min(max_w / logo.width, max_h / logo.height)
        new_w = int(logo.width * ratio)
        new_h = int(logo.height * ratio)
        logo_res = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)
        im.paste(logo_res, ((size - new_w) // 2, (size - new_h) // 2), logo_res)

        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        ico.parent.mkdir(parents=True, exist_ok=True)
        im.save(ico, format="ICO", sizes=sizes)
        im.save(base_dir / "assets" / "app_icon.png", format="PNG")
        print("  -> Đã tạo thành công assets/app_icon.ico")


def find_iscc() -> str | None:
    candidate_paths = [
        shutil.which("iscc"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
    ]
    for c in candidate_paths:
        if c and os.path.exists(c):
            return c
    return None


def main():
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)

    print("============================================================")
    print(" 🛠️  ĐÓNG GÓI BỘ CÀI ĐẶT WINDOWS SETUP WIZARD — THIÊN PHÚC")
    print("============================================================")

    generate_icon_if_needed(base_dir)

    pyinstaller = base_dir / ".venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller.exists():
        pyinstaller = base_dir / ".venv" / "bin" / "pyinstaller"
    pyinstaller_str = str(pyinstaller) if pyinstaller.exists() else "pyinstaller"

    # Step 1: Build Application Payload (onedir)
    print("\n[Bước 1/5] Đang đóng gói Payload ứng dụng chính (thư mục TPexcelApp)...")
    res1 = subprocess.run([pyinstaller_str, "--noconfirm", "TPexcelApp.spec"])
    if res1.returncode != 0:
        print("❌ Lỗi khi đóng gói TPexcelApp payload.")
        sys.exit(res1.returncode)

    payload_dir = base_dir / "dist" / "TPexcelApp"
    if not payload_dir.exists():
        print(f"❌ Không tìm thấy thư mục payload: {payload_dir}")
        sys.exit(1)

    # Ensure assets directory is present in payload root as well
    payload_assets = payload_dir / "assets"
    if not payload_assets.exists() and (base_dir / "assets").exists():
        shutil.copytree(base_dir / "assets", payload_assets)

    # Step 2: Build Single-File Standalone Portable Executable (TPexcelApp.exe)
    print("\n[Bước 2/5] Đang đóng gói Tệp chạy đơn độc lập (TPexcelApp.exe - Single File Portable)...")
    res_single = subprocess.run([pyinstaller_str, "--noconfirm", "TPexcel.spec"])
    if res_single.returncode != 0:
        print("⚠️ Cảnh báo: Lỗi khi đóng gói single-file TPexcelApp.exe")

    # Step 3: Create Portable Zip Package
    print("\n[Bước 3/5] Đang tạo gói nén Portable (TPexcelApp-Portable.zip)...")
    try:
        shutil.make_archive(
            str(base_dir / "dist" / "TPexcelApp-Portable"),
            "zip",
            root_dir=str(base_dir / "dist"),
            base_dir="TPexcelApp",
        )
        print("  -> Đã tạo gói nén: dist/TPexcelApp-Portable.zip")
    except Exception as exc:
        print(f"⚠️ Không thể tạo file zip: {exc}")

    # Step 4: Build Standalone Uninstaller
    print("\n[Bước 4/5] Đang đóng gói công cụ gỡ cài đặt (uninstall.exe)...")
    res2 = subprocess.run([pyinstaller_str, "--noconfirm", "TPexcelUninstaller.spec"])
    if res2.returncode != 0:
        print("⚠️ Cảnh báo: Lỗi khi đóng gói uninstall.exe, sẽ dùng script dọn dẹp bat.")

    # Step 5: Build Standalone Wizard Installer
    print("\n[Bước 5/5] Đang đóng gói Trình cài đặt Wizard duy nhất (TPexcel_Setup.exe)...")
    res3 = subprocess.run([pyinstaller_str, "--noconfirm", "TPexcelWizardInstaller.spec"])
    if res3.returncode != 0:
        print("❌ Lỗi khi đóng gói TPexcelWizardInstaller.")
        sys.exit(res3.returncode)

    # Optional: Build Inno Setup if ISCC is installed
    iscc = find_iscc()
    inno_exe = None
    if iscc:
        print("\n[Tùy chọn] Phát hiện Inno Setup Compiler! Đang biên dịch installer Inno Setup...")
        res_inno = subprocess.run([iscc, "installer_inno.iss"])
        if res_inno.returncode == 0:
            inno_target = base_dir / "dist" / "TPexcel_InnoSetup.exe"
            if inno_target.exists():
                inno_exe = inno_target
                print(f"  -> Đã tạo thêm bộ cài Inno Setup: {inno_exe}")

    setup_exe = base_dir / "dist" / "TPexcel_Setup.exe"
    single_exe = base_dir / "dist" / "TPexcelApp.exe"
    zip_pkg = base_dir / "dist" / "TPexcelApp-Portable.zip"

    print("\n============================================================")
    print(" 🎉 THÀNH CÔNG! ĐÃ TẠO XONG CÁC TỆP PHÁT HÀNH CHO WINDOWS:")
    if setup_exe.exists():
        print(f" 1. Bộ cài đặt Wizard (Setup):      {setup_exe.resolve()}")
    if single_exe.exists():
        print(f" 2. Tệp đơn chạy trực tiếp (EXE):    {single_exe.resolve()}")
    if zip_pkg.exists():
        print(f" 3. Gói giải nén chạy ngay (ZIP):   {zip_pkg.resolve()}")
    if inno_exe:
        print(f" 4. Bộ cài đặt Inno Setup:          {inno_exe.resolve()}")
    print("------------------------------------------------------------")
    print(" ✨ Người dùng có thể:")
    print("    - Tải TPexcel_Setup.exe để cài đặt có wizard, shortcut và gỡ cài đặt.")
    print("    - Hoặc tải trực tiếp TPexcelApp.exe để mở chạy ngay không cần cài đặt.")
    print("============================================================")


if __name__ == "__main__":
    main()
