from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QDragEnterEvent, QDropEvent, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QStyle,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.company import ICON_PATH, PNG_ICON_PATH
from core.excel_io import export_invoice, load_invoice
from core.invoice import Invoice, ProductRow
from core.sample_data import sample_invoice
from core.undo_manager import UndoManager
from ui.header_widget import InvoiceHeader
from ui.sheet_view import SheetView
from ui.table_model import InvoiceTableModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thiên Phúc — Hóa đơn bán hàng")
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        elif PNG_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(PNG_ICON_PATH)))
        self.resize(1280, 820)
        self.setAcceptDrops(True)
        self.dirty = False
        self._block_undo_push = False

        invoice = sample_invoice()
        self.undo_mgr = UndoManager()
        self.undo_mgr.reset(invoice)

        self.model = InvoiceTableModel(invoice)
        self.header = InvoiceHeader()
        self.sheet = SheetView(self.model)

        self.cell_name = QLabel("A16")
        self.cell_name.setFixedWidth(76)
        self.cell_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cell_name.setStyleSheet(
            "background: #e1dfdd; color: #201f1e; border: 1px solid #8a8886; border-radius: 3px; padding: 4px; font-weight: 700; font-size: 13px;"
        )
        self.formula = QLineEdit()
        self.formula.setPlaceholderText("Nội dung ô / công thức...")
        self.formula.setStyleSheet(
            "QLineEdit { border: 1px solid #c8c6c4; border-radius: 3px; background: #ffffff; padding: 4px 8px; font-size: 13px; color: #201f1e; }"
            "QLineEdit:focus { border: 1.5px solid #107c41; }"
        )
        self.formula.returnPressed.connect(self._apply_formula)

        fx_row = QHBoxLayout()
        fx_row.setContentsMargins(12, 6, 12, 6)
        fx_row.setSpacing(10)
        fx = QLabel("fx")
        fx.setStyleSheet("color: #107c41; font-weight: 900; font-size: 15px; font-style: italic;")
        fx_row.addWidget(self.cell_name)
        fx_row.addWidget(fx)
        fx_row.addWidget(self.formula, 1)
        fx_wrap = QWidget()
        fx_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        fx_wrap.setLayout(fx_row)
        fx_wrap.setStyleSheet("background: #f3f2f1; border-bottom: 1px solid #e1dfdd;")

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.header)
        root.addWidget(fx_wrap)
        root.addWidget(self.sheet, 1)
        central = QWidget()
        central.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        central.setStyleSheet("background-color: #ffffff;")
        central.setLayout(root)
        self.setCentralWidget(central)

        self._build_toolbar()
        self.status = QStatusBar()
        self.status.setStyleSheet(
            "QStatusBar { background: #f3f2f1; border-top: 1px solid #e1dfdd; color: #323130; font-weight: 600; font-size: 12px; padding: 4px 12px; }"
        )
        self.setStatusBar(self.status)

        self.header.customer.textChanged.connect(self._mark_dirty)
        self.header.address.textChanged.connect(self._mark_dirty)
        self.header.number.textChanged.connect(self._mark_dirty)
        self.header.date.dateChanged.connect(lambda *_: self._mark_dirty())
        self.model.invoiceChanged.connect(self._on_invoice_changed)
        self.sheet.currentCellChanged.connect(self._on_cell)
        self.sheet.statusMessage.connect(lambda msg: self.status.showMessage(msg, 3500))

        self.sheet.requestAddRow.connect(self.add_row)
        self.sheet.requestDeleteRows.connect(self.delete_rows)
        self.sheet.requestAddXe.connect(self.add_xe)
        self.sheet.requestRemoveXe.connect(self.remove_xe)
        self.sheet.requestUndo.connect(self.undo)
        self.sheet.requestRedo.connect(self.redo)

        QShortcut(QKeySequence.StandardKey.Copy, self).activated.connect(self._copy_action)
        QShortcut(QKeySequence.StandardKey.Paste, self).activated.connect(self._paste_action)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.sheet.fill_down)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.sheet.fill_right)
        QShortcut(QKeySequence.StandardKey.Find, self).activated.connect(self.search.setFocus)
        QShortcut(QKeySequence.StandardKey.Undo, self).activated.connect(self.undo)
        QShortcut(QKeySequence.StandardKey.Redo, self).activated.connect(self.redo)
        QShortcut(QKeySequence.StandardKey.Save, self).activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self.export_as)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.export_as)
        QShortcut(QKeySequence.StandardKey.Open, self).activated.connect(self.open_file)
        QShortcut(QKeySequence.StandardKey.New, self).activated.connect(self.new_file)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_as)
        QShortcut(QKeySequence("Ctrl+Shift+N"), self).activated.connect(self.add_row)

        self._sync_header_from_invoice()
        self._update_undo_redo_actions()
        self._update_status()
        QTimer.singleShot(0, lambda: self.sheet.table.setCurrentIndex(self.model.index(0, 1)))

    def _copy_action(self) -> None:
        focus = QApplication.focusWidget()
        if isinstance(focus, (QLineEdit, QTextEdit)):
            focus.copy()
        else:
            self.sheet.copy_selection()

    def _paste_action(self) -> None:
        focus = QApplication.focusWidget()
        if isinstance(focus, (QLineEdit, QTextEdit)):
            focus.paste()
        else:
            self.sheet.paste_selection()

    def _icon(self, std):
        return self.style().standardIcon(std)

    def _build_toolbar(self) -> None:
        bar = QToolBar("Chính")
        bar.setMovable(False)
        bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        bar.setStyleSheet(
            """
            QToolBar {
                background: #ffffff;
                border-bottom: 1.5px solid #e1dfdd;
                spacing: 4px;
                padding: 4px 8px;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #323130;
            }
            QToolButton:hover {
                background: #f3f2f1;
                border: 1px solid #c8c6c4;
            }
            QToolButton:pressed {
                background: #edebe9;
            }
            QToolButton:disabled {
                color: #a19f9d;
            }
            QLineEdit#search {
                min-width: 200px;
                padding: 4px 8px;
                border: 1px solid #c8c6c4;
                border-radius: 4px;
                background: #faf9f8;
                color: #201f1e;
                font-size: 12px;
            }
            QLineEdit#search:focus {
                border: 1.5px solid #107c41;
                background: #ffffff;
            }
            QPushButton#findBtn {
                background: #107c41;
                color: #ffffff;
                font-weight: 700;
                border-radius: 4px;
                padding: 4px 10px;
                border: none;
            }
            QPushButton#findBtn:hover {
                background: #0f6c38;
            }
            """
        )
        self.addToolBar(bar)

        def add(text, slot, icon=None, shortcut=None):
            act = QAction(text, self)
            if icon is not None:
                act.setIcon(self._icon(icon))
            if shortcut:
                act.setShortcut(shortcut)
            act.triggered.connect(slot)
            bar.addAction(act)
            return act

        add("Tạo mới", self.new_file, QStyle.StandardPixmap.SP_FileIcon, QKeySequence.StandardKey.New)
        add("Mở Excel", self.open_file, QStyle.StandardPixmap.SP_DialogOpenButton, QKeySequence.StandardKey.Open)
        add("Lưu", self.save_file, QStyle.StandardPixmap.SP_DialogSaveButton, QKeySequence.StandardKey.Save)
        add("Xuất Excel A4", self.export_as, QStyle.StandardPixmap.SP_DriveHDIcon)
        bar.addSeparator()

        self.act_undo = add("Hoàn tác", self.undo, QStyle.StandardPixmap.SP_ArrowBack, QKeySequence.StandardKey.Undo)
        self.act_redo = add("Làm lại", self.redo, QStyle.StandardPixmap.SP_ArrowForward, QKeySequence.StandardKey.Redo)
        bar.addSeparator()

        add("Thêm dòng", self.add_row, QStyle.StandardPixmap.SP_FileDialogNewFolder)
        add("Xóa dòng", self.delete_rows, QStyle.StandardPixmap.SP_TrashIcon)
        add("Thêm xe", self.add_xe, QStyle.StandardPixmap.SP_FileDialogDetailedView)
        add("Xóa xe", self.remove_xe, QStyle.StandardPixmap.SP_DialogDiscardButton)
        bar.addSeparator()
        add("Mẫu Senko", self.load_sample, QStyle.StandardPixmap.SP_BrowserReload)

        bar.addSeparator()
        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setPlaceholderText("Tìm mã / tên hàng… (Ctrl+F)")
        self.search.returnPressed.connect(self.find_next)
        bar.addWidget(self.search)
        find_btn = QPushButton("Tìm")
        find_btn.setObjectName("findBtn")
        find_btn.clicked.connect(self.find_next)
        bar.addWidget(find_btn)

    def invoice(self) -> Invoice:
        inv = self.model.invoice
        inv.customer_name = self.header.customer.text().strip()
        inv.customer_address = self.header.address.text().strip()
        inv.invoice_number = self.header.number.text().strip()
        qd = self.header.date.date()
        inv.invoice_date = date(qd.year(), qd.month(), qd.day())
        return inv

    def _sync_header_from_invoice(self) -> None:
        inv = self.model.invoice
        self.header.customer.setText(inv.customer_name)
        self.header.address.setText(inv.customer_address)
        self.header.number.setText(inv.invoice_number)
        d = inv.invoice_date
        self.header.date.setDate(QDate(d.year, d.month, d.day))
        self.dirty = False
        self._update_title()

    def _mark_dirty(self, *_):
        self.dirty = True
        self._update_title()

    def _on_invoice_changed(self) -> None:
        if not self._block_undo_push:
            self.undo_mgr.push(self.invoice())
            self._update_undo_redo_actions()
        self._mark_dirty()
        self._update_status()

    def _update_undo_redo_actions(self) -> None:
        self.act_undo.setEnabled(self.undo_mgr.can_undo())
        self.act_redo.setEnabled(self.undo_mgr.can_redo())

    def undo(self) -> None:
        prev = self.undo_mgr.undo()
        if prev is not None:
            self._block_undo_push = True
            try:
                self.model.set_invoice(prev)
                self._sync_header_from_invoice()
                self._update_undo_redo_actions()
                self.status.showMessage("Đã hoàn tác (Undo).", 3000)
            finally:
                self._block_undo_push = False

    def redo(self) -> None:
        nxt = self.undo_mgr.redo()
        if nxt is not None:
            self._block_undo_push = True
            try:
                self.model.set_invoice(nxt)
                self._sync_header_from_invoice()
                self._update_undo_redo_actions()
                self.status.showMessage("Đã làm lại (Redo).", 3000)
            finally:
                self._block_undo_push = False

    def _default_filename(self) -> str:
        d = self.model.invoice.invoice_date or date.today()
        return f"SENKO_T{d.month}.xlsx"

    def _update_title(self) -> None:
        name = Path(self.model.invoice.file_path).name if self.model.invoice.file_path else self._default_filename()
        mark = "*" if self.dirty else ""
        self.setWindowTitle(f"{mark}{name}")

    def _update_status(self) -> None:
        inv = self.model.invoice
        remain_bad = sum(1 for r in inv.rows if r.con_lai() < 0)
        remain_ok = sum(1 for r in inv.rows if r.con_lai() == 0 and (r.so_luong or 0) > 0)
        total_sl = inv.total_so_luong()
        total_rem = inv.total_con_lai()

        self.status.showMessage(
            f"{len(inv.rows)} dòng hàng  ·  {inv.n_xe} xe  ·  "
            f"Tổng SL: {total_sl:g}  ·  Đã hoàn thành: {remain_ok}/{len(inv.rows)}  ·  "
            f"Còn lại: {total_rem:g}  ·  Lỗi vượt số: {remain_bad}"
        )

    def _on_cell(self, row: int, col: int) -> None:
        if self.model.is_total_row(row):
            self.cell_name.setText(f"TOTAL_{col}")
            inv = self.model.invoice
            if col == inv.sl_col():
                self.formula.setText(f"=SUM(E16:E{15 + len(inv.rows)})")
            elif inv.first_xe_col() <= col <= inv.last_xe_col():
                c_letter = chr(65 + col)
                self.formula.setText(f"=SUM({c_letter}16:{c_letter}{15 + len(inv.rows)})")
            elif col == inv.con_lai_col():
                c_letter = chr(65 + col)
                self.formula.setText(f"=SUM({c_letter}16:{c_letter}{15 + len(inv.rows)})")
            else:
                self.formula.setText("TỔNG CỘNG")
            self.formula.setReadOnly(True)
            return

        self.cell_name.setText(self.sheet.excel_cell_name(row, col))
        idx = self.model.index(row, col)
        if col == self.model.invoice.con_lai_col():
            self.formula.setText(self.model.invoice.con_lai_formula(row))
            self.formula.setReadOnly(True)
        else:
            val = self.model.data(idx, Qt.ItemDataRole.EditRole)
            self.formula.setText("" if val is None else str(val))
            self.formula.setReadOnly(not bool(self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable))

    def _apply_formula(self) -> None:
        if self.formula.isReadOnly():
            return
        r, c = self.sheet.current_rc()
        if self.model.is_total_row(r):
            return
        idx = self.model.index(r, c)
        self.model.setData(idx, self.formula.text())

    def new_file(self) -> None:
        if not self._confirm_discard():
            return
        blank = Invoice(rows=[ProductRow() for _ in range(10)])
        self.model.set_invoice(blank)
        self.undo_mgr.reset(blank)
        self._sync_header_from_invoice()
        self._update_undo_redo_actions()
        self._update_status()

    def add_row(self) -> None:
        rows = self.sheet.selected_rows()
        at = (rows[-1] + 1) if rows else None
        pos = self.model.add_row(at)
        self.sheet.table.setCurrentIndex(self.model.index(pos, 1))

    def delete_rows(self) -> None:
        rows = self.sheet.selected_rows()
        if not rows:
            return
        if len(rows) > 1:
            reply = QMessageBox.warning(
                self,
                "Xác nhận xóa dòng hàng",
                f"Bạn có chắc chắn muốn xóa {len(rows)} dòng hàng đã chọn không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.model.remove_rows_at(rows)

    def add_xe(self) -> None:
        self.model.add_xe()

    def remove_xe(self) -> None:
        if self.model.invoice.n_xe <= 1:
            QMessageBox.information(self, "Xóa xe", "Phải giữ ít nhất 1 cột xe.")
            return

        xe_idx = self.sheet.selected_xe_index()
        xe_name = f"Xe ({xe_idx + 1})" if xe_idx is not None else f"Xe ({self.model.invoice.n_xe})"

        reply = QMessageBox.warning(
            self,
            "Xác nhận xóa cột xe",
            f"Bạn có chắc chắn muốn xóa cột {xe_name} không?\n\nTất cả số liệu phân bổ trên cột xe này sẽ bị xóa.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.model.remove_xe(xe_idx)

    def find_next(self) -> None:
        if not self.sheet.find_text(self.search.text()):
            self.status.showMessage("Không tìm thấy kết quả phù hợp.", 3000)

    def load_sample(self) -> None:
        if not self._confirm_discard():
            return
        sample = sample_invoice()
        self.model.set_invoice(sample)
        self.undo_mgr.reset(sample)
        self._sync_header_from_invoice()
        self._update_undo_redo_actions()
        self._update_status()

    def open_file(self) -> None:
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Mở Excel", "", "Excel (*.xlsx);;Tất cả (*.*)"
        )
        if not path:
            return
        self._load_file_path(path)

    def load_file(self, path: str | Path) -> None:
        self._load_file_path(str(path))

    def _load_file_path(self, path: str) -> None:
        try:
            inv = load_invoice(path)
        except Exception as exc:
            QMessageBox.critical(self, "Không mở được file", str(exc))
            return
        self.model.set_invoice(inv)
        self.undo_mgr.reset(inv)
        self._sync_header_from_invoice()
        self._update_undo_redo_actions()
        self._update_status()

    def save_file(self) -> None:
        path = self.model.invoice.file_path
        if not path:
            return self.export_as()
        self._write(path)

    def export_as(self) -> None:
        doc_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        default_dir = Path(doc_dir) if doc_dir else Path.home()
        suggested = self.model.invoice.file_path or str(
            default_dir / self._default_filename()
        )
        path, _ = QFileDialog.getSaveFileName(
            self, "Xuất 1 trang Excel", suggested, "Excel (*.xlsx);;Tất cả (*.*)"
        )
        if not path:
            return
        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"
        self._write(path)

    def _write(self, path: str) -> None:
        try:
            export_invoice(self.invoice(), path)
        except PermissionError:
            QMessageBox.critical(
                self,
                "Tệp đang bị khóa",
                f"Không thể lưu vào:\n{path}\n\n"
                "Tệp này đang được mở bởi Microsoft Excel hoặc một chương trình khác.\n"
                "Vui lòng đóng tệp trong Excel rồi thử lại!",
            )
            return
        except Exception as exc:
            QMessageBox.critical(self, "Không lưu được", str(exc))
            return
        self.model.invoice.file_path = path
        self.dirty = False
        self._update_title()
        self.status.showMessage(f"Đã xuất 1 trang Excel thành công: {path}", 5000)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(".xlsx") for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith(".xlsx"):
                if self._confirm_discard():
                    self._load_file_path(path)
                break

    def _confirm_discard(self) -> bool:
        if not self.dirty:
            return True
        box = QMessageBox.question(
            self,
            "Chưa lưu",
            "Có thay đổi chưa lưu. Tiếp tục và bỏ thay đổi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return box == QMessageBox.StandardButton.Yes

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()
