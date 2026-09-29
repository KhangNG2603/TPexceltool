#!/usr/bin/env bash
# ==============================================================================
# Script Cài Đặt (Installer) - Thiên Phúc Hóa Đơn Bán Hàng (Linux)
# ==============================================================================

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="Thiên Phúc - Hóa đơn bán hàng"
APP_EXEC="${APP_DIR}/chay_app.sh"
ICON_PATH="${APP_DIR}/assets/logo-thien-phuc.png"

echo "============================================================"
echo "   ĐANG CÀI ĐẶT: ${APP_NAME}"
echo "============================================================"

# 1. Khởi tạo virtual environment và cài đặt dependencies
echo "[1/4] Đang khởi tạo môi trường Python virtualenv..."
if [ ! -d "${APP_DIR}/.venv" ]; then
    python3 -m venv "${APP_DIR}/.venv"
fi
"${APP_DIR}/.venv/bin/pip" install --upgrade pip --quiet
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt" --quiet
echo "  -> Đã cài đặt xong các thư viện cần thiết."

if command -v dpkg >/dev/null 2>&1; then
    if ! dpkg -l | grep -q "libxcb-cursor0" 2>/dev/null; then
        echo ""
        echo "  ⚠️ CHÚ Ý: Hệ thống thiếu thư viện giao diện 'libxcb-cursor0' cho PySide6/Qt6."
        echo "  Vui lòng mở Terminal và gõ lệnh sau để cài bổ sung (chạy 1 lần):"
        echo "      sudo apt update && sudo apt install -y libxcb-cursor0"
        echo ""
    fi
fi

# 2. Đảm bảo file chay_app.sh có quyền thực thi
chmod +x "${APP_DIR}/chay_app.sh"
chmod +x "${APP_DIR}/go_cai_dat.sh" 2>/dev/null || true

# 3. Tạo Shortcut trong Menu Ứng Dụng Linux (~/.local/share/applications)
echo "[2/4] Đang đăng ký ứng dụng vào Menu hệ thống (App Launcher)..."
APPS_DIR="${HOME}/.local/share/applications"
mkdir -p "${APPS_DIR}"

DESKTOP_FILE="${APPS_DIR}/thienphuc-hoadon.desktop"

cat <<EOF > "${DESKTOP_FILE}"
[Desktop Entry]
Version=1.0
Type=Application
Name=Thiên Phúc - Hóa đơn bán hàng
GenericName=Quản lý Hóa đơn & Phân bổ xe
Comment=Ứng dụng quản lý hóa đơn, phân bổ số lượng lên xe và xuất Excel 1 trang
Exec="${APP_EXEC}"
Path=${APP_DIR}
Icon=${ICON_PATH}
Terminal=false
Categories=Office;Finance;Spreadsheet;
StartupWMClass=Thien Phuc Hoa Don
EOF

chmod +x "${DESKTOP_FILE}"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${APPS_DIR}" 2>/dev/null || true
fi

echo "  -> Đã tạo biểu tượng ứng dụng tại: ${DESKTOP_FILE}"

# 4. Tạo lệnh chạy nhanh trong terminal (~/.local/bin/thienphuc-hoadon)
echo "[3/4] Đang tạo lệnh thực thi nhanh (thienphuc-hoadon)..."
BIN_DIR="${HOME}/.local/bin"
mkdir -p "${BIN_DIR}"
ln -sf "${APP_EXEC}" "${BIN_DIR}/thienphuc-hoadon"
echo "  -> Đã tạo lệnh: thienphuc-hoadon"

# 5. Tạo Shortcut trên Màn hình chính (Desktop)
echo "[4/4] Đang tạo Shortcut trên Màn hình chính (Desktop)..."
DESKTOP_DIR=""
if [ -d "${HOME}/Desktop" ]; then
    DESKTOP_DIR="${HOME}/Desktop"
elif [ -d "${HOME}/Bàn làm việc" ]; then
    DESKTOP_DIR="${HOME}/Bàn làm việc"
fi

if [ -n "${DESKTOP_DIR}" ]; then
    cp "${DESKTOP_FILE}" "${DESKTOP_DIR}/thienphuc-hoadon.desktop"
    chmod +x "${DESKTOP_DIR}/thienphuc-hoadon.desktop"
    # Đánh dấu tin tưởng nếu là Ubuntu/GNOME
    gio set "${DESKTOP_DIR}/thienphuc-hoadon.desktop" metadata::trusted true 2>/dev/null || true
    echo "  -> Đã tạo shortcut tại: ${DESKTOP_DIR}/thienphuc-hoadon.desktop"
fi

echo ""
echo "============================================================"
echo "   ✅ CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!"
echo "   - Bạn có thể mở ứng dụng từ Menu App hệ thống."
echo "   - Hoặc gõ lệnh 'thienphuc-hoadon' trong Terminal."
echo "   - Muốn gỡ cài đặt, hãy chạy: ./go_cai_dat.sh"
echo "============================================================"
