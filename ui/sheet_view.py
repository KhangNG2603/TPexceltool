from __future__ import annotations

import csv
import io

from PySide6.QtCore import (
    QItemSelection,
    QItemSelectionModel,
    QModelIndex,
    QRect,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPainter,
    QPen,
)
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

        # Excel cell focus ring on active cell
        if option.state & QStyle.StateFlag.State_HasFocus:
            painter.setPen(QPen(QColor("#107c41"), 2))
            r = option.rect.adjusted(1, 1, -1, -1)
            painter.drawRect(r)

        painter.restore()


class ExcelTableView(QTableView):
    """QTableView tùy chỉnh với hành vi tương tác hoàn toàn giống Microsoft Excel:
    - Sao chép / dán bằng phím tắt và chuột không bị xung đột
    - Kéo chuột tại chấm góc dưới (Fill Handle) để sao chép ô xuống/sang ngang
    - Viền đứt nét xanh lá (Marching Ants) hiển thị rõ các ô đang được copy
    """

    def __init__(self, sheet_view: SheetView, parent=None):
        super().__init__(parent)
        self.sheet_view = sheet_view
        self._dragging_fill = False
        self._fill_source_range: tuple[int, int, int, int] | None = None
        self._fill_preview_range: tuple[int, int, int, int] | None = None
        self.viewport().setMouseTracking(True)

    def _get_active_range(self) -> tuple[int, int, int, int] | None:
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            curr = self.currentIndex()
            if curr.isValid():
                return curr.row(), curr.row(), curr.column(), curr.column()
            return None
        min_r = min(i.row() for i in indexes)
        max_r = max(i.row() for i in indexes)
        min_c = min(i.column() for i in indexes)
        max_c = max(i.column() for i in indexes)
        return min_r, max_r, min_c, max_c

    def _get_fill_handle_rect(self) -> QRect:
        active = self._get_active_range()
        if not active:
            return QRect()
        min_r, max_r, min_c, max_c = active
        r2 = self.visualRect(self.model().index(max_r, max_c))
        if not r2.isValid() or r2.width() <= 0 or r2.height() <= 0:
            return QRect()
        handle_size = 7
        return QRect(r2.right() - handle_size + 1, r2.bottom() - handle_size + 1, handle_size, handle_size)

    def _range_visual_rect(self, min_r: int, max_r: int, min_c: int, max_c: int) -> QRect:
        top_left = self.visualRect(self.model().index(min_r, min_c))
        bottom_right = self.visualRect(self.model().index(max_r, max_c))
        if not top_left.isValid() or not bottom_right.isValid():
            return QRect()
        return QRect(
            top_left.left(),
            top_left.top(),
            bottom_right.right() - top_left.left() + 1,
            bottom_right.bottom() - top_left.top() + 1,
        )

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()
        if not self._dragging_fill:
            handle = self._get_fill_handle_rect()
            if handle.isValid() and handle.contains(pos):
                self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.viewport().unsetCursor()
            super().mouseMoveEvent(event)
        else:
            curr_idx = self.indexAt(pos)
            if curr_idx.isValid() and self._fill_source_range:
                s_min_r, s_max_r, s_min_c, s_max_c = self._fill_source_range
                cr, cc = curr_idx.row(), curr_idx.column()
                # Xác định hướng kéo điền
                if cr > s_max_r:
                    self._fill_preview_range = (s_min_r, cr, s_min_c, s_max_c)
                elif cr < s_min_r:
                    self._fill_preview_range = (cr, s_max_r, s_min_c, s_max_c)
                elif cc > s_max_c:
                    self._fill_preview_range = (s_min_r, s_max_r, s_min_c, cc)
                elif cc < s_min_c:
                    self._fill_preview_range = (s_min_r, s_max_r, cc, s_max_c)
                else:
                    self._fill_preview_range = self._fill_source_range
                self.viewport().update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            handle = self._get_fill_handle_rect()
            if handle.isValid() and handle.contains(pos):
                active = self._get_active_range()
                if active:
                    self._dragging_fill = True
                    self._fill_source_range = active
                    self._fill_preview_range = active
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._dragging_fill and event.button() == Qt.MouseButton.LeftButton:
            self._dragging_fill = False
            self.viewport().unsetCursor()
            if (
                self._fill_source_range
                and self._fill_preview_range
                and self._fill_preview_range != self._fill_source_range
            ):
                self.sheet_view.execute_fill(self._fill_source_range, self._fill_preview_range)
            self._fill_source_range = None
            self._fill_preview_range = None
            self.viewport().update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self.viewport())

        # 1. Vẽ viền nét đứt xanh lá (Marching Ants) cho các ô đang được sao chép
        if self.sheet_view.has_copied_cells():
            copied = self.sheet_view.copied_range()
            if copied:
                c_min_r, c_max_r, c_min_c, c_max_c = copied
                c_rect = self._range_visual_rect(c_min_r, c_max_r, c_min_c, c_max_c)
                if c_rect.isValid() and c_rect.width() > 0:
                    pen = QPen(QColor("#107c41"), 2, Qt.PenStyle.DashLine)
                    painter.setPen(pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawRect(c_rect.adjusted(1, 1, -1, -1))

        # 2. Vẽ viền xem trước khi kéo Fill Handle
        if self._dragging_fill and self._fill_preview_range:
            p_min_r, p_max_r, p_min_c, p_max_c = self._fill_preview_range
            p_rect = self._range_visual_rect(p_min_r, p_max_r, p_min_c, p_max_c)
            if p_rect.isValid() and p_rect.width() > 0:
                pen = QPen(QColor("#107c41"), 2, Qt.PenStyle.DotLine)
                painter.setPen(pen)
                painter.setBrush(QColor(16, 124, 65, 30))
                painter.drawRect(p_rect.adjusted(1, 1, -1, -1))

        # 3. Vẽ ô vuông Fill Handle tại góc dưới bên phải của vùng chọn
        handle_rect = self._get_fill_handle_rect()
        if handle_rect.isValid() and not self._dragging_fill:
            painter.fillRect(handle_rect, QColor("#107c41"))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawRect(handle_rect)

        painter.end()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Ctrl + C: Sao chép ô
        if event.matches(QKeySequence.StandardKey.Copy) or (
            event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.sheet_view.copy_selection()
            event.accept()
            return

        # Ctrl + V: Dán ô
        if event.matches(QKeySequence.StandardKey.Paste) or (
            event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.sheet_view.paste_selection()
            event.accept()
            return

        # Ctrl + D: Điền dữ liệu xuống (Fill Down)
        if event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.sheet_view.fill_down()
            event.accept()
            return

        # Ctrl + R: Điền dữ liệu sang phải (Fill Right)
        if event.key() == Qt.Key.Key_R and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.sheet_view.fill_right()
            event.accept()
            return

        # Delete / Backspace: Xóa dữ liệu ô đang chọn
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.sheet_view.clear_selection()
            event.accept()
            return

        # Escape: Hủy trạng thái sao chép viền đứt nét hoặc hủy kéo fill
        if event.key() == Qt.Key.Key_Escape:
            if self.sheet_view.has_copied_cells() or self._dragging_fill:
                self.sheet_view.clear_copy_highlight()
                self._dragging_fill = False
                self._fill_preview_range = None
                self.viewport().update()
                event.accept()
                return

        # Enter: Dán nếu đang trong trạng thái sao chép ô
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.sheet_view.has_copied_cells():
                self.sheet_view.paste_selection()
                self.sheet_view.clear_copy_highlight()
                event.accept()
                return

        super().keyPressEvent(event)


class SheetView(QWidget):
    currentCellChanged = Signal(int, int)
    statusMessage = Signal(str)
    requestAddRow = Signal()
    requestDeleteRows = Signal()
    requestAddXe = Signal()
    requestRemoveXe = Signal()
    requestUndo = Signal()
    requestRedo = Signal()

    def __init__(self, model: InvoiceTableModel, parent=None):
        super().__init__(parent)
        self.model = model
        self._copied_range: tuple[int, int, int, int] | None = None
        self._copied_data: list[list[str]] | None = None

        self.table = ExcelTableView(self, self)
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
                color: #201f1e;
                background-color: #ffffff;
                gridline-color: #e1dfdd;
                selection-background-color: #cae6da;
                selection-color: #000000;
                alternate-background-color: #fafafa;
                font-size: 13px;
                border: none;
            }
            QTableView QLineEdit {
                color: #201f1e;
                background-color: #ffffff;
                border: 1.5px solid #107c41;
                padding: 1px 2px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #217346;
                color: #ffffff;
                padding: 6px;
                border: 1px solid #1b5e38;
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

    def copied_range(self) -> tuple[int, int, int, int] | None:
        return self._copied_range

    def has_copied_cells(self) -> bool:
        return self._copied_range is not None

    def clear_copy_highlight(self) -> None:
        self._copied_range = None
        self._copied_data = None
        self.table.viewport().update()

    def copy_selection(self) -> None:
        indexes = self.table.selectionModel().selectedIndexes()
        if not indexes:
            curr = self.table.currentIndex()
            if curr.isValid():
                indexes = [curr]
            else:
                return
        min_r = min(i.row() for i in indexes)
        max_r = max(i.row() for i in indexes)
        min_c = min(i.column() for i in indexes)
        max_c = max(i.column() for i in indexes)

        self._copied_range = (min_r, max_r, min_c, max_c)
        self._copied_data = []
        selected_set = {(i.row(), i.column()) for i in indexes}

        for r in range(min_r, max_r + 1):
            cells = []
            for c in range(min_c, max_c + 1):
                if (r, c) in selected_set or len(indexes) == (max_r - min_r + 1) * (max_c - min_c + 1):
                    val = self.model.data(self.model.index(r, c), Qt.ItemDataRole.EditRole)
                    if val is None:
                        val = self.model.data(self.model.index(r, c), Qt.ItemDataRole.DisplayRole)
                    cells.append("" if val is None else str(val))
                else:
                    cells.append("")
            self._copied_data.append(cells)

        tsv = "\r\n".join(["\t".join(row) for row in self._copied_data])
        QApplication.clipboard().setText(tsv)
        self.table.viewport().update()

        n_rows = max_r - min_r + 1
        n_cols = max_c - min_c + 1
        self.statusMessage.emit(f"Đã sao chép {n_rows} hàng x {n_cols} cột. Chọn ô đích và nhấn Ctrl+V hoặc Enter để dán.")

    def paste_selection(self) -> None:
        text = QApplication.clipboard().text()
        rows: list[list[str]] = []
        if text:
            clean_text = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
            reader = csv.reader(io.StringIO(clean_text), delimiter="\t")
            rows = [list(r) for r in reader]
        elif self._copied_data:
            rows = [list(r) for r in self._copied_data]

        if not rows or not rows[0]:
            return

        src_rows = len(rows)
        src_cols = max(len(r) for r in rows)
        if src_cols == 0:
            return
        rows = [r + [""] * (src_cols - len(r)) for r in rows]

        selected_indexes = self.table.selectionModel().selectedIndexes()
        if selected_indexes:
            min_sel_r = min(i.row() for i in selected_indexes)
            max_sel_r = max(i.row() for i in selected_indexes)
            min_sel_c = min(i.column() for i in selected_indexes)
            max_sel_c = max(i.column() for i in selected_indexes)
            sel_rows = max_sel_r - min_sel_r + 1
            sel_cols = max_sel_c - min_sel_c + 1
        else:
            curr = self.table.currentIndex()
            if not curr.isValid():
                return
            min_sel_r = max_sel_r = curr.row()
            min_sel_c = max_sel_c = curr.column()
            sel_rows = sel_cols = 1

        # Căn chỉnh thông minh: Nếu vùng chọn bắt đầu từ cột STT (cột 0) nhưng dữ liệu không chứa cột STT
        start_col = min_sel_c
        if start_col == 0 and src_cols < self.model.columnCount():
            start_col = 1

        start_row = min_sel_r

        # Xác định kích thước vùng dán mô phỏng Excel
        if sel_rows > 1 or sel_cols > 1:
            target_rows = max(sel_rows, src_rows)
            target_cols = max(sel_cols, src_cols)
        else:
            target_rows = src_rows
            target_cols = src_cols

        self.model.begin_batch()
        try:
            for dr in range(target_rows):
                r = start_row + dr
                src_r = dr % src_rows
                while r >= len(self.model.invoice.rows):
                    self.model.add_row()

                for dc in range(target_cols):
                    c = start_col + dc
                    src_c = dc % src_cols
                    if c >= self.model.columnCount():
                        continue
                    idx = self.model.index(r, c)
                    if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable:
                        self.model.setData(idx, rows[src_r][src_c])
        finally:
            self.model.end_batch()

        self.table.viewport().update()
        self.statusMessage.emit(f"Đã dán {target_rows} hàng x {target_cols} cột thành công.")

    def execute_fill(self, src_range: tuple[int, int, int, int], target_range: tuple[int, int, int, int]) -> None:
        s_min_r, s_max_r, s_min_c, s_max_c = src_range
        t_min_r, t_max_r, t_min_c, t_max_c = target_range
        src_h = s_max_r - s_min_r + 1
        src_w = s_max_c - s_min_c + 1
        if src_h <= 0 or src_w <= 0:
            return

        self.model.begin_batch()
        try:
            for r in range(t_min_r, t_max_r + 1):
                while r >= len(self.model.invoice.rows):
                    self.model.add_row()
                for c in range(t_min_c, t_max_c + 1):
                    # Bỏ qua các ô gốc
                    if s_min_r <= r <= s_max_r and s_min_c <= c <= s_max_c:
                        continue
                    src_r = s_min_r + ((r - s_min_r) % src_h)
                    src_c = s_min_c + ((c - s_min_c) % src_w)
                    val = self.model.data(self.model.index(src_r, src_c), Qt.ItemDataRole.EditRole)
                    if val is None:
                        val = self.model.data(self.model.index(src_r, src_c), Qt.ItemDataRole.DisplayRole)
                    idx = self.model.index(r, c)
                    if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable:
                        self.model.setData(idx, val)
        finally:
            self.model.end_batch()

        sel = self.table.selectionModel()
        top_left = self.model.index(t_min_r, t_min_c)
        bottom_right = self.model.index(t_max_r, t_max_c)
        sel.select(
            QItemSelection(top_left, bottom_right),
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
        self.table.viewport().update()
        self.statusMessage.emit("Đã điền tự động (Auto-Fill) dữ liệu thành công.")

    def fill_down(self) -> None:
        indexes = self.table.selectionModel().selectedIndexes()
        if not indexes:
            return
        min_r = min(i.row() for i in indexes)
        max_r = max(i.row() for i in indexes)
        if min_r == max_r:
            return
        min_c = min(i.column() for i in indexes)
        max_c = max(i.column() for i in indexes)

        self.model.begin_batch()
        try:
            for c in range(min_c, max_c + 1):
                top_val = self.model.data(self.model.index(min_r, c), Qt.ItemDataRole.EditRole)
                if top_val is None:
                    top_val = self.model.data(self.model.index(min_r, c), Qt.ItemDataRole.DisplayRole)
                for r in range(min_r + 1, max_r + 1):
                    idx = self.model.index(r, c)
                    if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable:
                        self.model.setData(idx, top_val)
        finally:
            self.model.end_batch()
        self.statusMessage.emit("Đã điền dữ liệu xuống (Fill Down Ctrl+D).")

    def fill_right(self) -> None:
        indexes = self.table.selectionModel().selectedIndexes()
        if not indexes:
            return
        min_c = min(i.column() for i in indexes)
        max_c = max(i.column() for i in indexes)
        if min_c == max_c:
            return
        min_r = min(i.row() for i in indexes)
        max_r = max(i.row() for i in indexes)

        self.model.begin_batch()
        try:
            for r in range(min_r, max_r + 1):
                left_val = self.model.data(self.model.index(r, min_c), Qt.ItemDataRole.EditRole)
                if left_val is None:
                    left_val = self.model.data(self.model.index(r, min_c), Qt.ItemDataRole.DisplayRole)
                for c in range(min_c + 1, max_c + 1):
                    idx = self.model.index(r, c)
                    if self.model.flags(idx) & Qt.ItemFlag.ItemIsEditable:
                        self.model.setData(idx, left_val)
        finally:
            self.model.end_batch()
        self.statusMessage.emit("Đã điền dữ liệu sang phải (Fill Right Ctrl+R).")

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
        idx = self.table.indexAt(pos)
        if idx.isValid():
            sel_model = self.table.selectionModel()
            if not sel_model.isSelected(idx):
                self.table.setCurrentIndex(idx)
                sel_model.select(idx, QItemSelectionModel.SelectionFlag.ClearAndSelect)

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

        act_fill_down = QAction("⬇️ Điền dữ liệu xuống (Ctrl+D)", self)
        act_fill_down.triggered.connect(self.fill_down)
        menu.addAction(act_fill_down)

        act_fill_right = QAction("➡️ Điền dữ liệu sang phải (Ctrl+R)", self)
        act_fill_right.triggered.connect(self.fill_right)
        menu.addAction(act_fill_right)

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
