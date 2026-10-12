from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path


def upload_release(token: str, repo: str = "KhangNG2603/TPexceltool", tag: str = "v1.0.1"):
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
        "body": "### 📦 Các tùy chọn tải về cho Windows:\n- **`TPexcel_Setup.exe`**: Bộ cài đặt Setup Wizard từng bước (tạo shortcut Desktop, Start Menu, có gỡ cài đặt).\n- **`TPexcelApp.exe`**: Tệp đơn chạy trực tiếp Portable không cần cài đặt.\n- **`TPexcelApp-Portable.zip`**: Gói nén di động chạy ngay sau khi giải nén.",
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

    # Step 2: Upload Release Assets
    candidates = [
        Path("dist/TPexcel_Setup.exe"),
        Path("dist/TPexcelApp.exe"),
        Path("dist/TPexcelApp-Portable.zip"),
        Path("dist/TPexcel.exe"),
    ]
    assets_to_upload = [p for p in candidates if p.exists()]
    if not assets_to_upload:
        print("❌ Không tìm thấy file trong dist/ để tải lên.")
        sys.exit(1)

    for asset_file in assets_to_upload:
        print(f"📦 Đang tải file asset '{asset_file}' lên GitHub Release...")
        upload_url = upload_url_raw.split("{")[0] + f"?name={asset_file.name}"
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
                print(f"🎉 Tải lên {asset_file.name} thành công: {asset_res.get('browser_download_url')}")
        except urllib.error.HTTPError as err:
            err_body = err.read().decode('utf-8')
            print(f"❌ Lỗi HTTP khi tải up {asset_file.name} ({err.code}): {err_body}")

    print(f"\n============================================================")
    print(f" 🌟 GITHUB RELEASE HOÀN TẤT THÀNH CÔNG!")
    print(f" Link xem & tải về: {html_url}")
    print(f"============================================================")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python github_release.py <GITHUB_TOKEN>")
        sys.exit(1)
    upload_release(sys.argv[1])
