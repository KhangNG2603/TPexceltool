import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            p = Path(sys._MEIPASS)
            if (p / "assets").exists():
                return p
        exe_dir = Path(sys.executable).resolve().parent
        if (exe_dir / "_internal" / "assets").exists():
            return exe_dir / "_internal"
        if (exe_dir / "assets").exists():
            return exe_dir
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return exe_dir
    return Path(__file__).resolve().parent.parent


ROOT = get_base_dir()
LOGO_PATH = ROOT / "assets" / "logo-thien-phuc.png"
ICON_PATH = ROOT / "assets" / "app_icon.ico"
PNG_ICON_PATH = ROOT / "assets" / "app_icon.png"

APP_NAME = "Thiên Phúc — Hóa đơn bán hàng"
APP_SHORT_NAME = "TPexcel"
APP_VERSION = "1.0.2"
APP_PUBLISHER = "Công ty TNHH TBĐ Thiên Phúc"

COMPANY_NAME = "CÔNG TY TNHH XÂY DỰNG THƯƠNG MẠI THIẾT BỊ ĐIỆN THIÊN PHÚC"
COMPANY_ADDRESS = "F6/26W, ấp 6B, Xã Vĩnh Lộc, Thành phố Hồ Chí Minh, Việt Nam."
COMPANY_TEL = "Tel: 0907.234.565-0906.324.565-0942.234.565"
DOCUMENT_TITLE = "HÓA ĐƠN BÁN HÀNG"

DEFAULT_XE_COUNT = 1
HEADER_ROWS = 15  # dòng dữ liệu đầu tiên trên Excel = 16
