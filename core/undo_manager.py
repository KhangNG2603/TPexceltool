from __future__ import annotations

from typing import Optional
from core.invoice import Invoice


class UndoManager:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.undo_stack: list[Invoice] = []
        self.redo_stack: list[Invoice] = []
        self._busy = False

    def reset(self, initial_invoice: Invoice) -> None:
        self.undo_stack = [initial_invoice.copy()]
        self.redo_stack.clear()

    def push(self, invoice: Invoice) -> None:
        if self._busy:
            return
        self.undo_stack.append(invoice.copy())
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 1

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self) -> Optional[Invoice]:
        if not self.can_undo():
            return None
        self._busy = True
        try:
            cur = self.undo_stack.pop()
            self.redo_stack.append(cur)
            return self.undo_stack[-1].copy()
        finally:
            self._busy = False

    def redo(self) -> Optional[Invoice]:
        if not self.can_redo():
            return None
        self._busy = True
        try:
            target = self.redo_stack.pop()
            self.undo_stack.append(target.copy())
            return target.copy()
        finally:
            self._busy = False
