from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from core.company import DEFAULT_XE_COUNT


def col_letter(index_zero: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    n = index_zero + 1
    letters = []
    while n:
        n, rem = divmod(n - 1, 26)
        letters.append(chr(65 + rem))
    return "".join(reversed(letters))


def parse_number(value) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(" ", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_number(value: Optional[float]) -> str:
    if value is None:
        return ""
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:g}"


@dataclass
class ProductRow:
    ma: str = ""
    ten: str = ""
    dvt: str = "Cái"
    so_luong: float = 0.0
    xe: list[Optional[float]] = field(default_factory=list)

    def ensure_xe(self, n: int) -> None:
        if len(self.xe) < n:
            self.xe.extend([None] * (n - len(self.xe)))
        elif len(self.xe) > n:
            self.xe = self.xe[:n]

    def xe_sum(self) -> float:
        return float(sum(v or 0.0 for v in self.xe))

    def con_lai(self) -> float:
        return float(self.so_luong or 0.0) - self.xe_sum()


@dataclass
class Invoice:
    customer_name: str = ""
    customer_address: str = ""
    invoice_date: date = field(default_factory=date.today)
    invoice_number: str = ""
    n_xe: int = DEFAULT_XE_COUNT
    rows: list[ProductRow] = field(default_factory=list)
    file_path: Optional[str] = None

    def __post_init__(self) -> None:
        self.n_xe = max(1, int(self.n_xe))
        if not self.rows:
            self.rows = [ProductRow() for _ in range(8)]
        for row in self.rows:
            row.ensure_xe(self.n_xe)

    def copy(self) -> "Invoice":
        return deepcopy(self)

    def set_xe_count(self, n: int) -> None:
        self.n_xe = max(1, int(n))
        for row in self.rows:
            row.ensure_xe(self.n_xe)

    def add_xe(self) -> None:
        self.set_xe_count(self.n_xe + 1)

    def remove_xe(self, index: int | None = None) -> bool:
        if self.n_xe <= 1:
            return False
        if index is None or index < 0 or index >= self.n_xe:
            index = self.n_xe - 1
        for row in self.rows:
            if index < len(row.xe):
                row.xe.pop(index)
        self.n_xe -= 1
        return True

    def add_row(self, at: int | None = None) -> int:
        row = ProductRow()
        row.ensure_xe(self.n_xe)
        if at is None or at < 0 or at > len(self.rows):
            self.rows.append(row)
            return len(self.rows) - 1
        self.rows.insert(at, row)
        return at

    def remove_rows(self, indices: list[int]) -> None:
        for i in sorted(set(indices), reverse=True):
            if 0 <= i < len(self.rows) and len(self.rows) > 1:
                self.rows.pop(i)

    # --- column layout in the grid / Excel body ---
    def col_count(self) -> int:
        return 5 + self.n_xe + 1

    def stt_col(self) -> int:
        return 0

    def sl_col(self) -> int:
        return 4

    def first_xe_col(self) -> int:
        return 5

    def last_xe_col(self) -> int:
        return 4 + self.n_xe

    def con_lai_col(self) -> int:
        return 5 + self.n_xe

    def excel_data_row(self, grid_row: int) -> int:
        from core.company import HEADER_ROWS

        return HEADER_ROWS + 1 + grid_row

    def con_lai_formula(self, grid_row: int) -> str:
        excel_row = self.excel_data_row(grid_row)
        sl = col_letter(self.sl_col())
        first = col_letter(self.first_xe_col())
        last = col_letter(self.last_xe_col())
        return f"={sl}{excel_row}-SUM({first}{excel_row}:{last}{excel_row})"

    def header_labels(self) -> list[str]:
        labels = ["STT", "Mã hàng", "Tên hàng", "Đơn vị", "Số lượng"]
        labels.extend(f"Xe ({i})" for i in range(1, self.n_xe + 1))
        labels.append("Còn lại")
        return labels

    def total_so_luong(self) -> float:
        return sum(row.so_luong or 0.0 for row in self.rows)

    def total_xe(self, xe_index: int) -> float:
        total = 0.0
        for row in self.rows:
            if 0 <= xe_index < len(row.xe):
                total += row.xe[xe_index] or 0.0
        return total

    def total_con_lai(self) -> float:
        return sum(row.con_lai() for row in self.rows)

