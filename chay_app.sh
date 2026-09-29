#!/usr/bin/env bash
# Tự động tìm thư mục thực sự của dự án (kể cả khi gọi qua symlink ~/.local/bin/thienphuc-hoadon)
TARGET="$0"
while [ -h "$TARGET" ]; do
  DIR="$(cd -P "$(dirname "$TARGET")" && pwd)"
  TARGET="$(readlink "$TARGET")"
  [[ $TARGET != /* ]] && TARGET="$DIR/$TARGET"
done
APP_DIR="$(cd -P "$(dirname "$TARGET")" && pwd)"

cd "$APP_DIR"

# Kiểm tra thư viện hệ thống Qt XCB (libxcb-cursor0) trên Linux
if command -v dpkg >/dev/null 2>&1; then
  if ! dpkg -l | grep -q "libxcb-cursor0" 2>/dev/null; then
    echo "=================================================================="
    echo "⚠️ THÔNG BÁO HỆ THỐNG: Máy tính của bạn đang thiếu thư viện 'libxcb-cursor0' cho Qt6."
    echo "Vui lòng mở Terminal và chạy lệnh sau (chỉ cần chạy 1 lần duy nhất):"
    echo ""
    echo "    sudo apt update && sudo apt install -y libxcb-cursor0"
    echo ""
    echo "=================================================================="
  fi
fi

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python app.py
