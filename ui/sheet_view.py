from __future__ import annotations

from PySide6.QtCore import QItemSelectionModel, QModelIndex, QRect, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPainter, QPen, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.invoice import col_letter
from ui.table_model import InvoiceTableModel


class GridDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        super().paint(painter, option, index)
        painter.save()
        # Draw light gray grid border
        painter.setPen(QPen(QColor("#e1dfdd")))
        painter.drawRect(option.rect.adjusted(0, 0, -1, -1))

        # Excel cell focus ring & fill handle dot
        if option.state & QStyle.StateFlag.State_HasFocus:
            painter.setPen(QPen(QColor("#107c41"), 2))
            r = option.rect.adjusted(1, 1, -1, -1)
            painter.drawRect(r)

            # Draw green Fill Handle square at bottom-right corner
            handle_size = 5
            handle_rect = QRect(r.right() - handle_size, r.bottom() - handle_size, handle_size, handle_size)
            painter.fillRect(handle_rect, QColor("#107c41"))

        painter.restore()


class SheetView(QWidget):
    currentCellChanged = Signal(int, int)
    requestAddRow = Signal()
    requestDeleteRows = Signal()
    requestAddXe = Signal()
    requestRemoveXe = Signal()
    requestUndo = Signal()
    requestRedo = Signal()

    def __init__(self, model: InvoiceTableModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.table = QTableView(self)
        self.table.setModel(model)
        self.table.setItemDelegate(GridDelegate(self.table))
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(26)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.horizontalHeader().setFixedHeight(32)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.setStyleSheet(
            """
            QTableView {
                gridline-color: #e1dfdd;
                selection-background-color: #cae6da;
                selection-color: #000000;
                alternate-background-color: #fafafa;
                background: #ffffff;
                font-size: 13px;
                border: none;
            }
            QHeaderView::section {
                background-color: #f3f2f1;
                color: #323130;
                padding: 6px;
                border: 1px solid #d4d4d4;
                font-weight: 700;
                font-size: 12px;
            }
            QHeaderView::section:vertical {
                background-color: #f3f2f1;
                color: #323130;
                font-weight: 600;
                border: 1px solid #d4d4d4;
            }
            """
        )
        self._apply_column_widths()
        self.table.selectionModel().currentChanged.connect(self._on_current)

        # Excel bottom Sheet Tabs Bar
        sheet_bar = QHBoxLayout()
        sheet_bar.setContentsMargins(8, 2, 8, 2)
        sheet_bar.setSpacing(6)

        tab_btn = QPushButton(" 📄 Hóa đơn bán hàng ")
        tab_btn.setCheckable(True)
        tab_btn.setChecked(True)
        tab_btn.setStyleSheet(
            """
            QPushButton {
                background: #ffffff;
                color: #107c41;
                border: 1px solid #d4d4d4;
                border-bottom: 3px solid #107c41;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: 700;
                font-size: 12px;
                padding: 4px 12px;
            }
            """
        )

        add_tab_btn = QPushButton(" ➕ ")
        add_tab_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: #605e5c;
                border: none;
                font-weight: bold;
                font-size: 13px;
                padding: 4px;
            }
            QPushButton:hover {
                background: #e1dfdd;
                border-radius: 3px;
            }
            """
        )

        ready_label = QLabel("SẴN SÀNG")
        ready_label.setStyleSheet("color: #605e5c; font-weight: 700; font-size: 11px;")

        zoom_label = QLabel("100%")
        zoom_label.setStyleSheet("color: #605e5c; font-weight: 600; font-size: 11px;")

        sheet_bar.addWidget(tab_btn)
        sheet_bar.addWidget(add_tab_btn)
        sheet_bar.addSpacing(16)
        sheet_bar.addWidget(ready_label)
        sheet_bar.addStretch(1)
        sheet_bar.addWidget(zoom_label)

        sheet_bar_wrap = QWidget()
        sheet_bar_wrap.setLayout(sheet_bar)
        sheet_bar_wrap.setStyleSheet("background: #f3f2f1; border-top: 1px solid #d4d4d4;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.table, 1)
        layout.addWidget(sheet_bar_wrap)

        QShortcut(QKeySequence.StandardKey.Copy, self.table).activated.connect(self.copy_selection)
        QShortcut(QKeySequence.StandardKey.Paste, self.table).activated.connect(self.paste_selection)
        QShortcut(QKeySequence.StandardKey.Delete, self.table).activated.connect(self.clear_selection)
        QShortcut(QKeySequence.StandardKey.Backspace, self.table).activated.connect(self.clear_selection)

        model.modelReset.connect(self._apply_column_widths)

    def _apply_column_widths(self) -> None:
        inv = self.model.invoice
        widths = [46, 130, 280, 72, 88]
        widths.extend([64] * inv.n_xe)
        widths.append(88)
        for i, w in enumerate(widths):
            if i < self.model.columnCount():
                self.table.setColumnWidth(i, w)

    def _on_current(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if current.isValid():
            self.currentCellChanged.emit(current.row(), current.column())

    def current_rc(self) -> tuple[int, int]:
        idx = self.table.currentIndex()
        if not idx.isValid():
            return 0, 0
        return idx.row(), idx.column()

    def excel_cell_name(self, row: int, col: int) -> str:
        excel_row = self.model.invoice.excel_data_row(row)
        return f"{col_letter(col)}{excel_row}"

    def copy_selection(self) -> None:
        indexes = self.table.selectionModel().selectedIndexes()
        if not indexes:
            return
        min_r = min(i.row() for i in indexes)
        max_r = max(i.row() for i in indexes)
        min_c = min(i.column() for i in indexes)
        max_c = max(i.column() for i in indexes)
        lines = []
        for r in range(min_r, max_r + 1):
            cells = []
            for c in range(min_c, max_c + 1):
                val = self.model.data(self.model.index(r, c), Qt.ItemDataRole.DisplayRole)
                cells.append("" if val is None else str(val))
            lines.append("\t".join(cells))
        QApplication.clipboard().setText("\n".join(lines))

    def paste_selection(self) -> None:
        text = QApplication.clipboard().text()
        if not text:
            return
        selected_indexes = self.table.selectionModel().selectedIndexes()
        start = self.table.currentIndex()
        if not start.isValid():
            return

        rows = [line.split("\t") for line in text.replace("\r\n", "\n").split("\n") if line != ""]
        if not rows:
            return

        # Single source cell pasted onto multiple selected cells
        if len(rows) == 1 and len(rows[0]) == 1 and len(selected_indexes) > 1:
            cell_val = rows[0][0]
            for idx in selected_indexes:
                if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable:
                    self.model.setData(idx, cell_val)
            return

        for dr, line in enumerate(rows):
            for dc, cell in enumerate(line):
                r = start.row() + dr
                c = start.column() + dc
                while r >= len(self.model.invoice.rows):
                    self.model.add_row()
                if c >= self.model.columnCount():
                    continue
                idx = self.model.index(r, c)
                if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable:
                    self.model.setData(idx, cell)

    def clear_selection(self) -> None:
        editable = [idx for idx in self.table.selectionModel().selectedIndexes() if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable]
        if not editable:
            return
        if len(editable) > 5:
            reply = QMessageBox.question(
                self,
                "Xác nhận xóa nhiều ô",
                f"Bạn có chắc chắn muốn xóa dữ liệu của {len(editable)} ô đang chọn không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        for idx in editable:
            self.model.setData(idx, "")

    def selected_rows(self) -> list[int]:
        data_len = len(self.model.invoice.rows)
        rows = {i.row() for i in self.table.selectionModel().selectedIndexes() if i.row() < data_len}
        if not rows:
            idx = self.table.currentIndex()
            if idx.isValid() and idx.row() < data_len:
                rows = {idx.row()}
        return sorted(rows)

    def selected_xe_index(self) -> int | None:
        idx = self.table.currentIndex()
        if not idx.isValid():
            return None
        inv = self.model.invoice
        if inv.first_xe_col() <= idx.column() <= inv.last_xe_col():
            return idx.column() - inv.first_xe_col()
        return None

    def find_text(self, needle: str) -> bool:
        needle = needle.strip().lower()
        if not needle:
            return False
        start = self.table.currentIndex()
        r0 = start.row() if start.isValid() else 0
        c0 = start.column() if start.isValid() else 0
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        positions = [(r, c) for r in range(rows) for c in range(cols)]
        start_pos = r0 * cols + c0 + 1
        ordered = positions[start_pos:] + positions[:start_pos]
        for r, c in ordered:
            val = self.model.data(self.model.index(r, c), Qt.ItemDataRole.DisplayRole)
            if val and needle in str(val).lower():
                index = self.model.index(r, c)
                self.table.setCurrentIndex(index)
                self.table.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.ClearAndSelect
                )
                self.table.scrollTo(index)
                return True
        return False

    def _show_context_menu(self, pos) -> None:
        menu = QMenu(self)

        act_undo = QAction("↩️ Hoàn tác (Ctrl+Z)", self)
        act_undo.triggered.connect(self.requestUndo.emit)
        menu.addAction(act_undo)

        act_redo = QAction("↪️ Làm lại (Ctrl+Y)", self)
        act_redo.triggered.connect(self.requestRedo.emit)
        menu.addAction(act_redo)

        menu.addSeparator()

        act_copy = QAction("📋 Sao chép (Ctrl+C)", self)
        act_copy.triggered.connect(self.copy_selection)
        menu.addAction(act_copy)

        act_paste = QAction("📥 Dán (Ctrl+V)", self)
        act_paste.triggered.connect(self.paste_selection)
        menu.addAction(act_paste)

        act_clear = QAction("🧹 Xóa nội dung ô (Delete)", self)
        act_clear.triggered.connect(self.clear_selection)
        menu.addAction(act_clear)

        menu.addSeparator()

        act_add_row = QAction("➕ Thêm dòng", self)
        act_add_row.triggered.connect(self.requestAddRow.emit)
        menu.addAction(act_add_row)

        act_del_row = QAction("🗑️ Xóa các dòng đã chọn", self)
        act_del_row.triggered.connect(self.requestDeleteRows.emit)
        menu.addAction(act_del_row)

        menu.addSeparator()

        act_add_xe = QAction("🚗 Thêm xe", self)
        act_add_xe.triggered.connect(self.requestAddXe.emit)
        menu.addAction(act_add_xe)

        act_del_xe = QAction("❌ Xóa xe đang chọn", self)
        act_del_xe.triggered.connect(self.requestRemoveXe.emit)
        menu.addAction(act_del_xe)

        menu.exec(self.table.viewport().mapToGlobal(pos))
