#!/usr/bin/env bash
# ==============================================================================
# Script Gỡ Cài Đặt (Uninstaller) - Thiên Phúc Hóa Đơn Bán Hàng (Linux)
# ==============================================================================

set -e

APP_NAME="Thiên Phúc - Hóa đơn bán hàng"
APPS_FILE="${HOME}/.local/share/applications/thienphuc-hoadon.desktop"
BIN_FILE="${HOME}/.local/bin/thienphuc-hoadon"

echo "============================================================"
echo "   ĐANG GỠ CÀI ĐẶT: ${APP_NAME}"
echo "============================================================"

# 1. Xóa file Desktop Entry trong Menu ứng dụng
if [ -f "${APPS_FILE}" ]; then
    rm -f "${APPS_FILE}"
    echo "[✓] Đã xóa Shortcut trong Menu ứng dụng hệ thống."
fi

# 2. Xóa lệnh trong ~/.local/bin
if [ -f "${BIN_FILE}" ] || [ -L "${BIN_FILE}" ]; then
    rm -f "${BIN_FILE}"
    echo "[✓] Đã xóa lệnh thienphuc-hoadon trong ~/.local/bin."
fi

# 3. Xóa Shortcut trên Màn hình chính (Desktop)
if [ -f "${HOME}/Desktop/thienphuc-hoadon.desktop" ]; then
    rm -f "${HOME}/Desktop/thienphuc-hoadon.desktop"
    echo "[✓] Đã xóa Shortcut trên Desktop."
fi
if [ -f "${HOME}/Bàn làm việc/thienphuc-hoadon.desktop" ]; then
    rm -f "${HOME}/Bàn làm việc/thienphuc-hoadon.desktop"
    echo "[✓] Đã xóa Shortcut trên Bàn làm việc."
fi

# 4. Cập nhật lại cơ sở dữ liệu menu hệ thống
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "   ✅ ĐÃ GỠ CÀI ĐẶT THÀNH CÔNG KHỎI HỆ THỐNG!"
echo "   Lưu ý: Thư mục mã nguồn dự án vẫn được giữ nguyên."
echo "============================================================"
