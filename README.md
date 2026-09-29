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

- **Cài đặt (Install)**:
  Double click file **`cai_dat.bat`**
  *Tác dụng*: Tự động khởi tạo môi trường, cài đặt thư viện, đóng gói tệp thực thi **`TPexcel.exe`** bằng PyInstaller và tạo **Desktop Shortcut** & **Start Menu Shortcut** (`TPexcel`).

- **Gỡ cài đặt (Uninstall)**:
  Double click file **`go_cai_dat.bat`**
  *Tác dụng*: Xóa sạch shortcut `TPexcel` khỏi Màn hình chính và Start Menu Windows.

---

## 🚀 Hướng dẫn chạy nhanh không cần cài đặt

- **Linux / macOS**: `./chay_app.sh`
- **Windows**: Double click `chay_app.bat`

---

## ⌨️ Danh sách Phím tắt (Shortcuts)

| Phím tắt | Thao tác |
| :--- | :--- |
| `Ctrl + Z` | ↩️ Hoàn tác thao tác vừa thực hiện (Undo) |
| `Ctrl + Y` / `Ctrl + Shift + Z` | ↪️ Làm lại thao tác vừa hoàn tác (Redo) |
| `Ctrl + N` | Tạo hóa đơn rỗng mới |
| `Ctrl + O` | Mở file Excel (`.xlsx`) |
| `Ctrl + S` | Lưu / Xuất file Excel hiện tại |
| `Ctrl + E` | Xuất file Excel 1 trang |
| `Ctrl + F` | Tìm kiếm mã hàng / tên hàng |
| `Ctrl + C` | Sao chép vùng ô đã chọn |
| `Ctrl + V` | Dán dữ liệu từ Clipboard / Excel |
| `Delete` / `Backspace` | Xóa dữ liệu các ô đang chọn |
| `Ctrl + Shift + N` | Thêm dòng hàng mới |
