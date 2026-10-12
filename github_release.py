from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path


def upload_release(token: str, repo: str = "KhangNG2603/TPexceltool", tag: str = "v1.0.0"):
    print(f"🚀 Đang tạo GitHub Release '{tag}' trên repository {repo}...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TPexcel-Uploader",
    }

    # Step 1: Create Release
    release_url = f"https://api.github.com/repos/{repo}/releases"
    data = json.dumps({
        "tag_name": tag,
        "target_commitish": "main",
        "name": f"TPexcel {tag} - Bộ cài đặt Hóa đơn bán hàng Windows",
        "body": "### 📦 Hướng dẫn cài đặt cho Windows:\n1. Tải về file **`TPexcel.exe`** ở phần Assets bên dưới.\n2. Nhấp đúp vào file `TPexcel.exe` để cài đặt tự động lên máy tính.",
        "draft": False,
        "prerelease": False,
    }).encode("utf-8")

    req = urllib.request.Request(release_url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            upload_url_raw = res_data["upload_url"]
            html_url = res_data["html_url"]
            print(f"✅ Đã tạo thành công Release tại: {html_url}")
    except urllib.error.HTTPError as err:
        err_body = err.read().decode('utf-8')
        print(f"❌ Lỗi HTTP khi tạo Release ({err.code}): {err_body}")
        sys.exit(1)

    # Step 2: Upload TPexcel.exe asset
    upload_url = upload_url_raw.split("{")[0] + "?name=TPexcel.exe"
    asset_file = Path("dist/TPexcel.exe")
    if not asset_file.exists():
        asset_file = Path("dist/TPexcel")

    if not asset_file.exists():
        print("❌ Không tìm thấy file dist/TPexcel.exe hoặc dist/TPexcel để tải lên.")
        sys.exit(1)

    print(f"📦 Đang tải file asset '{asset_file}' lên GitHub Release...")
    file_data = asset_file.read_bytes()
    asset_headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/octet-stream",
        "User-Agent": "TPexcel-Uploader",
    }

    asset_req = urllib.request.Request(upload_url, data=file_data, headers=asset_headers, method="POST")
    try:
        with urllib.request.urlopen(asset_req) as resp:
            asset_res = json.loads(resp.read().decode("utf-8"))
            print(f"🎉 Tải lên Asset thành công: {asset_res.get('browser_download_url')}")
            print(f"\n============================================================")
            print(f" 🌟 GITHUB RELEASE HOÀN TẤT THÀNH CÔNG!")
            print(f" Link xem & tải về: {html_url}")
            print(f"============================================================")
    except urllib.error.HTTPError as err:
        err_body = err.read().decode('utf-8')
        print(f"❌ Lỗi HTTP khi tải up Asset ({err.code}): {err_body}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python github_release.py <GITHUB_TOKEN>")
        sys.exit(1)
    upload_release(sys.argv[1])
