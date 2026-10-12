# Thiên Phúc — Hóa đơn bán hàng & Quản lý phân bổ hàng lên xe (Desktop App)

Ứng dụng cửa sổ mô tả giao diện Excel Editor dành cho nhân viên văn phòng để quản lý hàng hóa, phân bổ số lượng mặt hàng theo từng chuyến xe (**Xe 1...Xe n**), tự động tính toán số lượng **Còn lại** và dòng **TỔNG CỘNG**, sau đó xuất file chuẩn **1 trang Excel A4 ngang** (`.xlsx`).

---

## 🌟 Tính năng nổi bật

1. **Giao diện mô phỏng Excel Editor**:
   - Thanh công thức `fx` hiển thị tên ô (ví dụ `E16`), công thức `=E16-SUM(F16:Y16)` hoặc `=SUM(E16:E54)`.
   - Lưới bảng hỗ trợ thao tác giống Excel: Click double để sửa, phím `Delete` / `Backspace` xóa dữ liệu ô, phím điều hướng `Enter`, `Tab`.
   - Phân màu cảnh báo trực quan:
     - 🟩 **Xanh lá**: Đã phân bổ hoàn tất (`Còn lại = 0`).
     - 🟨 **Vàng**: Đang phân bổ dở dang (`0 < Còn lại < Số lượng`).
     - 🟥 **Đỏ**: Cảnh báo phân bổ vượt quá số lượng (`Còn lại < 0`).

2. **Dòng TỔNG CỘNG trực quan (Live Totals)**:
   - Hiển thị dòng `∑ TỔNG CỘNG` ngay cuối bảng dữ liệu trên giao diện và file Excel xuất ra.
   - Tự động cộng tổng: Total Số lượng, Total từng Xe (Xe 1 → Xe n) và Total Còn lại.

3. **Xuất chuẩn 1 trang Excel A4 ngang**:
   - Tên file gợi ý mặc định tự động nhảy theo tháng hóa đơn: **`SENKO_T(tháng).xlsx`** (Ví dụ tháng 9 là `SENKO_T9.xlsx`).
   - Header tiêu đề công ty + Logo Thiên Phúc + Thông tin khách hàng & ngày hóa đơn.
   - Chèn công thức Excel gốc (Excel Formula) `=E16-SUM(F16:Y16)` và `=SUM(...)`.
   - Cấu hình sẵn trang in A4 Landscape, căn lề 0.4 inch, Fit-to-Page 1x1 trang.

4. **Hệ thống Undo & Redo (Hoàn tác / Làm lại)**:
   - Nút **Hoàn tác (`Ctrl+Z`)** và **Làm lại (`Ctrl+Y`)** trên thanh công cụ và Menu chuột phải.
   - Lưu trữ lịch sử thao tác thông minh (sửa dữ liệu, thêm/xóa dòng, thêm/xóa xe, sửa thông tin khách hàng).

5. **Tiện ích cho Nhân viên Văn phòng**:
   - **Kéo & Thả (Drag & Drop)**: Thả file `.xlsx` trực tiếp vào cửa sổ app để mở.
   - **Menu chuột phải (Context Menu)**: Hoàn tác, Làm lại, Thêm dòng, Xóa dòng, Thêm/xóa cột xe, Sao chép, Dán, Xóa nội dung ô.
   - **Sao chép & Dán linh hoạt (Copy-Paste)**: Hỗ trợ copy/paste từ/đến Microsoft Excel. Nếu copy 1 giá trị và chọn nhiều ô target, app tự động dán hàng loạt.
   - **Thống kê thời gian thực**: Thanh trạng thái hiển thị tổng dòng, tổng số xe, tổng SL đặt, số dòng đã hoàn thành, số lượng dư/thiếu.

---

## 📦 Cài đặt & Gỡ cài đặt (Installer & Uninstaller)

### 🐧 Trên Linux (Ubuntu, Debian, Fedora, Mint, Arch...)

- **Cài đặt (Install)**:
  Mở Terminal và chạy:
  ```bash
  ./cai_dat.sh
  ```
  *Tác dụng*: Tự động cài đặt venv, tạo biểu tượng ứng dụng **Thiên Phúc - Hóa đơn bán hàng** trong **Menu App hệ thống (Application Launcher)**, tạo **Desktop Shortcut** và tạo lệnh thực thi nhanh `thienphuc-hoadon` trong Terminal.

- **Gỡ cài đặt (Uninstall)**:
  Mở Terminal và chạy:
  ```bash
  ./go_cai_dat.sh
  ```
  *Tác dụng*: Dọn dẹp sạch sẽ shortcut trong App Menu, Desktop shortcut và lệnh terminal.

---

### 🪟 Trên Windows

- **Đóng gói bộ cài đặt Wizard Installer (Dành cho nhà phát triển / Quản trị viên)**:
  Double click file **`cai_dat.bat`**
  *Tác dụng*:
  1. Tự động kiểm tra phiên bản Python trên máy tính (`py -3.11`, `py`, `python`).
  2. Tạo môi trường ảo `.venv` và cài đặt thư viện cần thiết.
  3. Tự động tạo biểu tượng ứng dụng Windows đa kích thước (`assets/app_icon.ico`).
  4. Đóng gói mã nguồn thành tệp cài đặt **`dist\TPexcel_Setup.exe`** (Wizard Installer độc lập hoàn chỉnh).
  5. Đóng gói công cụ gỡ cài đặt **`dist\uninstall.exe`**.
  6. Tạo sẵn kịch bản biên dịch Inno Setup chuẩn **`installer_inno.iss`** (tùy chọn).

- **Cài đặt ứng dụng cho người dùng cuối (End-User Setup Wizard)**:
  Người dùng chỉ cần nhấp đúp vào **`dist\TPexcel_Setup.exe`**:
  - Giao diện **Setup Wizard** 4 bước chuẩn Windows:
    1. **Chào mừng (Welcome)**: Giới thiệu ứng dụng & phiên bản.
    2. **Chọn thư mục (Destination)**: Mặc định `%LOCALAPPDATA%\Programs\TPexcel` (không đòi quyền Admin, không lo lỗi phân quyền, tương thích 100% Windows 10/11) cùng tính năng kiểm tra dung lượng ổ đĩa khả dụng.
    3. **Tùy chọn bổ sung (Options)**: Tạo lối tắt Desktop, Start Menu, và đăng ký ứng dụng vào Windows.
    4. **Cài đặt & Hoàn tất (Finish)**: Thanh tiến trình cài đặt thực tế và tùy chọn khởi chạy ứng dụng ngay.
  - **Tích hợp sâu hệ thống Windows**:
    - Tự động hiển thị trong **Windows Settings > Apps > Installed apps** (và Control Panel).
    - Biểu tượng ứng dụng và tác vụ trên thanh tác vụ Taskbar hiển thị chuẩn (AppUserModelID).

- **Gỡ cài đặt (Uninstall)**:
  Có thể gỡ cài đặt dễ dàng bằng bất kỳ cách nào:
  1. Mở **Windows Settings -> Apps -> Installed apps**, tìm **Thiên Phúc — Hóa đơn bán hàng** và bấm **Uninstall**.
  2. Hoặc chạy file **`go_cai_dat.bat`** (hoặc `uninstall.exe` trong thư mục cài đặt).
  *Tác dụng*: Xóa sạch sẽ tệp ứng dụng, lối tắt Desktop, menu Start và dọn dẹp Registry Windows.

---

## 🚀 Hướng dẫn chạy nhanh không cần cài đặt

- **Linux / macOS**: `./chay_app.sh`
- **Windows**: Double click `chay_app.bat` (hoặc mở trực tiếp file `dist\TPexcelApp\TPexcelApp.exe` sau khi build)

---

## ⌨️ Danh sách Phím tắt (Shortcuts)

| Phím tắt | Thao tác |
| :--- | :--- |
| `Ctrl + Z` | ↩️ Hoàn tác thao tác vừa thực hiện (Undo) |
| `Ctrl + Y` / `Ctrl + Shift + Z` | ↪️ Làm lại thao tác vừa hoàn tác (Redo) |
| `Ctrl + N` | Tạo hóa đơn rỗng mới |
| `Ctrl + O` | Mở file Excel (`.xlsx`) |
| `Ctrl + S` | Lưu file Excel hiện tại (nhanh) |
| `Ctrl + E` / `Ctrl + Shift + S` / `F12` | Xuất 1 trang Excel A4 ngang |
| `Ctrl + F` | Tìm kiếm mã hàng / tên hàng |
| `Ctrl + C` | Sao chép vùng ô đã chọn |
| `Ctrl + V` | Dán dữ liệu từ Clipboard / Excel |
| `Delete` / `Backspace` | Xóa dữ liệu các ô đang chọn |
| `F2` | Chỉnh sửa trực tiếp ô hiện tại |
| `Ctrl + Shift + N` | Thêm dòng hàng mới |
