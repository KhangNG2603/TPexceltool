from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from core.company import (
    COMPANY_ADDRESS,
    COMPANY_NAME,
    COMPANY_TEL,
    DOCUMENT_TITLE,
    LOGO_PATH,
)


class InvoiceHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("invoiceHeader")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            #invoiceHeader {
                background-color: #ffffff;
                border-bottom: 2px solid #e1dfdd;
                padding-bottom: 4px;
            }
            QLabel {
                color: #201f1e;
                background: transparent;
            }
            QLabel#company {
                font-family: "Segoe UI", "Times New Roman", sans-serif;
                font-size: 15px;
                font-weight: 700;
                color: #107c41;
            }
            QLabel#addr {
                font-family: "Segoe UI", "Times New Roman", sans-serif;
                font-size: 12px;
                color: #605e5c;
            }
            QLabel#docTitle {
                font-size: 22px;
                font-weight: 800;
                color: #107c41;
                letter-spacing: 1.5px;
                padding: 4px 0;
            }
            QLabel.fieldLabel {
                font-weight: 700;
                font-size: 13px;
                color: #323130;
            }
            QLineEdit, QDateEdit {
                border: none;
                border-bottom: 1.5px solid #8a8886;
                background-color: #faf9f8;
                padding: 4px 8px;
                font-size: 13px;
                border-radius: 2px;
                color: #201f1e;
            }
            QLineEdit:hover, QDateEdit:hover {
                background-color: #f3f2f1;
                border-bottom-color: #323130;
            }
            QLineEdit:focus, QDateEdit:focus {
                background-color: #ffffff;
                border-bottom: 2px solid #107c41;
                color: #201f1e;
            }
            """
        )

        logo = QLabel()
        logo.setFixedSize(130, 86)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if LOGO_PATH.exists():
            pix = QPixmap(str(LOGO_PATH)).scaled(
                124, 82,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)

        company = QLabel(COMPANY_NAME)
        company.setObjectName("company")
        company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company.setWordWrap(True)
        addr = QLabel(COMPANY_ADDRESS)
        addr.setObjectName("addr")
        addr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tel = QLabel(COMPANY_TEL)
        tel.setObjectName("addr")
        tel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QVBoxLayout()
        info.setSpacing(2)
        info.addWidget(company)
        info.addWidget(addr)
        info.addWidget(tel)

        top = QHBoxLayout()
        top.setContentsMargins(16, 8, 16, 4)
        top.addWidget(logo, 0)
        top.addLayout(info, 1)

        title = QLabel(DOCUMENT_TITLE)
        title.setObjectName("docTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.customer = QLineEdit()
        self.customer.setPlaceholderText("Nhập tên khách hàng...")
        self.address = QLineEdit()
        self.address.setPlaceholderText("Nhập địa chỉ giao hàng...")
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd/MM/yyyy")
        self.number = QLineEdit()
        self.number.setPlaceholderText("Mã / Số hóa đơn...")

        fields = QGridLayout()
        fields.setContentsMargins(16, 4, 16, 8)
        fields.setHorizontalSpacing(16)
        fields.setVerticalSpacing(10)
        fields.addWidget(self._label("Tên khách:"), 0, 0)
        fields.addWidget(self.customer, 0, 1)
        fields.addWidget(self._label("Ngày:"), 0, 2)
        fields.addWidget(self.date, 0, 3)
        fields.addWidget(self._label("Địa chỉ:"), 1, 0)
        fields.addWidget(self.address, 1, 1)
        fields.addWidget(self._label("Số HĐ:"), 1, 2)
        fields.addWidget(self.number, 1, 3)
        fields.setColumnStretch(1, 1)
        fields.setColumnStretch(3, 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)
        layout.addLayout(top)
        layout.addWidget(title)
        layout.addLayout(fields)

    def _label(self, text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet("font-weight: 700; font-size: 13px; color: #323130;")
        return lb
