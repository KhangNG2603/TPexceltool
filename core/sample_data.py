from core.invoice import Invoice, ProductRow


SAMPLE_PRODUCTS = [
    ("SENKO-B102", "Quạt bàn Mini B102", "Cái", 20),
    ("SENKO-B1213", "Quạt bàn B3 B1213", "Cái", 40),
    ("SENKO-B1216", "Quạt bàn B3- B1216", "Cái", 40),
    ("SENKO-B1612", "Quạt bàn B4 B1612", "Cái", 160),
    ("SENKO-B1616", "Quạt bàn Senko B1616", "Cái", 100),
    ("SENKO-BD1010", "Bàn đảo 3T Senko BD1010", "Cái", 20),
    ("SENKO-BD1012", "BÀN ĐẢO 3 TẤC Senko BD1012", "Cái", 20),
    ("SENKO-BD1410", "BÀN ĐẢO 4 TẤC Senko BD1410", "Cái", 20),
    ("SENKO-BD230", "Bàn đảo 2T Senko BD230", "Cái", 20),
    ("SENKO-DCN1801", "Quạt đứng CN 4.5 tấc DCN1801", "Cái", 60),
    ("SENKO-DCN1803", "Quạt đứng Senko DCN1803", "Cái", 5),
    ("SENKO-DH1600", "Quạt đứng hẹn giờ DH1600", "Cái", 10),
    ("SENKO-DR1608", "Quạt đứng Senko DR1608", "Cái", 10),
    ("SENKO-DTS1601", "Quạt đứng thân sắt Senko DTS1601", "Cái", 40),
    ("SENKO-DTS1603", "Quạt đứng thân sắt Senko DTS1603", "Cái", 20),
    ("SENKO-H100", "QUẠT HÚT SENKO H100", "Cái", 40),
    ("SENKO-H150", "QUẠT HÚT SENKO H150", "Cái", 80),
    ("SENKO-H200", "QUẠT HÚT SENKO H200", "Cái", 80),
    ("SENKO-H250", "QUẠT HÚT SENKO H250", "Cái", 80),
    ("SENKO-HT150", "QUẠT HÚT TRẦN SENKO HT150", "Cái", 80),
    ("SENKO-HT200", "Quạt HÚT TRẦN SENKO HT200", "Cái", 50),
    ("SENKO-HT250", "Quạt HÚT TRẦN SENKO HT250", "Cái", 50),
    ("SENKO-L1638", "Quạt lỡ nhựa Senko 1638", "Cái", 200),
    ("SENKO-LS1639", "Quạt lỡ Senko LS 1639", "Cái", 8),
    ("SENKO-LTS1631", "Quạt lỡ thân sắt Senko LTS1631", "Cái", 200),
    ("SENKO-LTS1633", "Quạt lỡ thân sắt Senko LTS1633", "Cái", 20),
    ("SENKO-S1850", "Quạt sàn Senko S1850", "Cái", 10),
    ("SENKO-SL1830", "Quạt sàn lỡ Senko SL1830", "Cái", 10),
    ("SENKO-T1680", "SENKO TREO 1 DÂY T1680", "Cái", 40),
    ("SENKO-T1682", "SENKO TREO 1 DÂY T1682", "Cái", 24),
    ("SENKO-TC1620", "Quạt treo Senko TC 1620", "Cái", 60),
    ("SENKO-TC1622", "Quạt treo Senko TC 1622", "Cái", 100),
    ("SENKO-TC1623", "Quạt treo Senko TC1623", "Cái", 80),
    ("SENKO-TC1626", "QUẠT TREO SENKO TC1626", "Cái", 200),
    ("SENKO-TC1881", "Quạt treo CN 2 dây TC1881", "Cái", 80),
    ("SENKO-TC1883", "Quạt treo Senko TC1883", "Cái", 20),
    ("SENKO-TD105", "Đảo trần Senko TD105", "Cái", 80),
    ("SENKO-TR1628", "Quạt treo Remote TR1628", "Cái", 50),
    ("SENKO-TR1683", "Quạt treo SenKo ĐKTX 1683 ko lấy còm", "Cái", 40),
]


def sample_invoice() -> Invoice:
    rows = [
        ProductRow(ma=ma, ten=ten, dvt=dvt, so_luong=float(sl), xe=[])
        for ma, ten, dvt, sl in SAMPLE_PRODUCTS
    ]
    inv = Invoice(rows=rows, invoice_number="001")
    return inv
