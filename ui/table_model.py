from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont

from core.invoice import Invoice, col_letter, format_number, parse_number


class InvoiceTableModel(QAbstractTableModel):
    invoiceChanged = Signal()

    def __init__(self, invoice: Invoice):
        super().__init__()
        self.invoice = invoice

    def set_invoice(self, invoice: Invoice) -> None:
        self.beginResetModel()
        self.invoice = invoice
        self.endResetModel()
        self.invoiceChanged.emit()

    def is_total_row(self, row: int) -> bool:
        return row == len(self.invoice.rows)

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.invoice.rows) + 1  # +1 for Total Row

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return self.invoice.col_count()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                labels = self.invoice.header_labels()
                if 0 <= section < len(labels):
                    letter = col_letter(section)
                    return f"{letter} · {labels[section]}"
            else:
                if section < len(self.invoice.rows):
                    return str(section + 1)
                return "∑"
        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font
        if role == Qt.ItemDataRole.ForegroundRole and orientation == Qt.Orientation.Horizontal:
            return QBrush(QColor("#ffffff"))
        if role == Qt.ItemDataRole.BackgroundRole and orientation == Qt.Orientation.Horizontal:
            return QBrush(QColor("#217346"))
        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if self.is_total_row(index.row()):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        col = index.column()
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if col in (self.invoice.stt_col(), self.invoice.con_lai_col()):
            return base
        return base | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row_idx = index.row()
        col = index.column()
        inv = self.invoice

        # --- Total Row ---
        if self.is_total_row(row_idx):
            if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
                if col == 0:
                    return ""
                if col == 1:
                    return ""
                if col == 2:
                    return "TỔNG CỘNG"
                if col == 3:
                    return ""
                if col == inv.sl_col():
                    return format_number(inv.total_so_luong())
                if inv.first_xe_col() <= col <= inv.last_xe_col():
                    return format_number(inv.total_xe(col - inv.first_xe_col()))
                if col == inv.con_lai_col():
                    return format_number(inv.total_con_lai())
                return None

            if role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setBold(True)
                return font

            if role == Qt.ItemDataRole.BackgroundRole:
                return QBrush(QColor("#e2efda"))

            if role == Qt.ItemDataRole.TextAlignmentRole:
                if col == 2:
                    return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

            return None

        # --- Normal Data Row ---
        row = inv.rows[row_idx]

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == inv.stt_col():
                return str(row_idx + 1)
            if col == 1:
                return row.ma
            if col == 2:
                return row.ten
            if col == 3:
                return row.dvt
            if col == inv.sl_col():
                return format_number(row.so_luong)
            if inv.first_xe_col() <= col <= inv.last_xe_col():
                val = row.xe[col - inv.first_xe_col()]
                return format_number(val)
            if col == inv.con_lai_col():
                if role == Qt.ItemDataRole.EditRole:
                    return inv.con_lai_formula(row_idx)
                return format_number(row.con_lai())
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (1, 2, 3):
                return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

        if role == Qt.ItemDataRole.BackgroundRole:
            if col == inv.con_lai_col():
                remain = row.con_lai()
                if remain < 0:
                    return QBrush(QColor("#f8d7da"))  # Red warning
                if remain == 0 and (row.so_luong or 0) > 0:
                    return QBrush(QColor("#d4edda"))  # Soft green (complete)
                if 0 < remain < (row.so_luong or 0):
                    return QBrush(QColor("#fff3cd"))  # Soft yellow (in progress)
                return QBrush(QColor("#f3f2f1"))
            if col == inv.stt_col():
                return QBrush(QColor("#f8f8f8"))
            return None

        if role == Qt.ItemDataRole.ForegroundRole:
            if col == inv.con_lai_col() and row.con_lai() < 0:
                return QBrush(QColor("#9b1c1c"))
            return None

        if role == Qt.ItemDataRole.ToolTipRole and col == inv.con_lai_col():
            return inv.con_lai_formula(row_idx)

        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False
        if self.is_total_row(index.row()):
            return False

        row_idx = index.row()
        row = self.invoice.rows[row_idx]
        col = index.column()
        inv = self.invoice
        text = "" if value is None else str(value).strip()

        if col == 1:
            row.ma = text
        elif col == 2:
            row.ten = text
        elif col == 3:
            row.dvt = text or "Cái"
        elif col == inv.sl_col():
            row.so_luong = parse_number(text) or 0.0
        elif inv.first_xe_col() <= col <= inv.last_xe_col():
            row.xe[col - inv.first_xe_col()] = parse_number(text)
        else:
            return False

        last_col_idx = inv.con_lai_col()
        total_row_idx = len(inv.rows)

        # Notify cell change
        self.dataChanged.emit(
            index,
            index,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.BackgroundRole],
        )

        # Notify remaining cell change in the same row
        con_lai_index = self.index(row_idx, last_col_idx)
        self.dataChanged.emit(
            con_lai_index,
            con_lai_index,
            [
                Qt.ItemDataRole.DisplayRole,
                Qt.ItemDataRole.BackgroundRole,
                Qt.ItemDataRole.ForegroundRole,
                Qt.ItemDataRole.ToolTipRole,
            ],
        )

        # Notify total row changes for edited col and con_lai col
        tot_edited_index = self.index(total_row_idx, col)
        tot_sl_index = self.index(total_row_idx, inv.sl_col())
        tot_cl_index = self.index(total_row_idx, last_col_idx)

        for tot_idx in (tot_edited_index, tot_sl_index, tot_cl_index):
            self.dataChanged.emit(tot_idx, tot_idx, [Qt.ItemDataRole.DisplayRole])

        self.invoiceChanged.emit()
        return True

    def add_row(self, at: int | None = None) -> int:
        data_len = len(self.invoice.rows)
        pos = at if (at is not None and 0 <= at <= data_len) else data_len
        self.beginInsertRows(QModelIndex(), pos, pos)
        idx = self.invoice.add_row(pos)
        self.endInsertRows()
        self.invoiceChanged.emit()
        return idx

    def remove_rows_at(self, rows: list[int]) -> None:
        data_len = len(self.invoice.rows)
        valid = [r for r in rows if 0 <= r < data_len]
        if not valid:
            return
        for r in sorted(set(valid), reverse=True):
            if len(self.invoice.rows) > 1:
                self.beginRemoveRows(QModelIndex(), r, r)
                self.invoice.rows.pop(r)
                self.endRemoveRows()
        self.invoiceChanged.emit()

    def add_xe(self) -> None:
        self.beginResetModel()
        self.invoice.add_xe()
        self.endResetModel()
        self.invoiceChanged.emit()

    def remove_xe(self, xe_index: int | None = None) -> None:
        self.beginResetModel()
        self.invoice.remove_xe(xe_index)
        self.endResetModel()
        self.invoiceChanged.emit()
