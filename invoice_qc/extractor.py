import os
import re
from typing import List, Dict, Any, Optional

import pdfplumber
from langdetect import detect, LangDetectException

from .schemas import Invoice, LineItem
from .utils import parse_number


def extract_text_from_pdf(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        texts = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n".join(texts)


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"

PATTERNS: Dict[str, Dict[str, List[str]]] = {
    "invoice_number": {
        "de": [
            r"Rechnungsnummer[:\s]*([A-Za-z0-9\-\/]+)",
            r"Rechnung\s*Nr\.?\s*([A-Za-z0-9\-\/]+)",
            r"AUFNR([0-9A-Za-z\-\/]+)",
        ],
        "en": [
            r"Invoice\s*(Number|No\.?|#)[:\s]*([A-Za-z0-9\-\/]+)",
        ],
    },
    "invoice_date": {
        "de": [
            r"vom\s+([\d\.\/\-]+)",
            r"Rechnungsdatum[:\s]*([\d\.\/\-]+)",
        ],
        "en": [
            r"Invoice\s*Date[:\s]*([\d\.\/\-]+)",
            r"Date[:\s]*([\d\.\/\-]+)",
        ],
    },
    "customer_number": {
        "de": [r"Unsere\s+Kundennummer\s*([\dA-Za-z\-\/]+)"],
        "en": [r"Customer\s*(No\.?|Number)[:\s]*([\dA-Za-z\-\/]+)"],
    },
    "end_customer_number": {
        "de": [r"Endkundennummer\s*([\dA-Za-z\-\/]+)"],
        "en": [r"End\s*Customer\s*(No\.?|Number)[:\s]*([\dA-Za-z\-\/]+)"],
    },
    "payment_terms": {
        "de": [r"Zahlungsbedingungen\s*(.+)"],
        "en": [r"Payment\s*Terms\s*(.+)"],
    },
    "delivery_terms": {
        "de": [r"Lieferbedingungen\s*(.+)"],
        "en": [r"Delivery\s*Terms\s*(.+)"],
    },
    "delivery_date": {
        "de": [r"Gewünschtes\s+Lieferdatum\s*(.+)"],
        "en": [r"Delivery\s*Date\s*(.+)"],
    },
    "currency": {
        "de": [r"Preis\s+in\s+([A-Z]{3})"],
        "en": [r"Currency[:\s]*([A-Z]{3})"],
    },
}


def _search_patterns(field: str, lang: str, text: str) -> Optional[str]:
    candidates = PATTERNS.get(field, {}).get(lang, []) + PATTERNS.get(field, {}).get(
        "en", []
    )
    for pattern in candidates:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            groups = [g for g in m.groups() if g]
            if groups:
                return groups[-1].strip()
    return None


def _extract_totals(text: str) -> Dict[str, Optional[float]]:
    net_total = None
    tax_rate = None
    tax_amount = None
    gross_total = None


    m_net = re.search(
        r"Gesamtwert\s+EUR\s*([\d\.,]+)", text, flags=re.IGNORECASE
    ) or re.search(
        r"Netto(?:betrag)?[:\s]*([\d\.,]+)", text, flags=re.IGNORECASE
    )
    if m_net:
        net_total = parse_number(m_net.group(1))

    m_tax = re.search(
        r"MwSt\.?\s*([\d\.,]+)\s*%.*?([\d\.,]+)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m_tax:
        tax_rate = parse_number(m_tax.group(1))
        tax_amount = parse_number(m_tax.group(2))

    # Gesamtwert inkl. MwSt. EUR
    m_gross = re.search(
        r"Gesamtwert\s+inkl\.?\s+MwSt\.?\s*EUR\s*([\d\.,]+)",
        text,
        flags=re.IGNORECASE,
    )
    if m_gross:
        gross_total = parse_number(m_gross.group(1))

    return {
        "net_total": net_total,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "gross_total": gross_total,
    }


def _extract_parties(text: str) -> Dict[str, Optional[str]]:
    """
    Very rough heuristic: look for blocks near known German labels.
    In a real system you'd tune this for the actual invoices.
    """
    seller_name = None
    seller_address = None
    buyer_name = None
    buyer_address = None

    m_buyer = re.search(
        r"Kundenanschrift(.*?)(?:Unsere Kundennummer|Seite\s+\d+)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if m_buyer:
        block = m_buyer.group(1).strip()
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if lines:
            buyer_name = lines[0]
            buyer_address = ", ".join(lines[1:]) if len(lines) > 1 else None

    m_seller = re.search(
        r"(Beispielname.*?)(?:Ihre Faxnummer|Seite\s+\d+)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if m_seller:
        block = m_seller.group(1).strip()
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if lines:
            seller_name = lines[0]
            seller_address = ", ".join(lines[1:]) if len(lines) > 1 else None

    return {
        "seller_name": seller_name,
        "seller_address": seller_address,
        "buyer_name": buyer_name,
        "buyer_address": buyer_address,
    }


def _extract_purchase_order(text: str) -> Optional[str]:
    m = re.search(
        r"Bestellung\s+([A-Z0-9]+).*?(im Auftrag von\s*[0-9A-Za-z]+)?",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        return " ".join(g for g in m.groups() if g).strip()
    return None


def _extract_line_items(text: str) -> List[LineItem]:
    """
    Very simplified line item extraction; tuned for the sample format.
    Looks for lines after 'Pos.' header.
    """
    items: List[LineItem] = []

    # Find table start
    table_match = re.search(
        r"Pos\.\s+Artikelbeschreibung.*?Bestellwert\s+in\s+EUR(.*)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not table_match:
        return items

    table_text = table_match.group(1)
    lines = [l.strip() for l in table_text.splitlines() if l.strip()]


    description_match = re.search(
        r"Sterilisationsmittel", text, flags=re.IGNORECASE
    )
    description = "Sterilisationsmittel" if description_match else None

    for line in lines:
        if re.match(r"^\d+\s", line):
            parts = line.split()
            try:
                position = int(parts[0])
            except ValueError:
                position = None

            quantity = None
            unit = None
            unit_conversion = None
            unit_price = None
            line_total = None

            qty_unit_match = re.search(r"(\d+[,\.]?\d*)\s*([A-Za-z]+)", line)
            if qty_unit_match:
                quantity = parse_number(qty_unit_match.group(1))
                unit = qty_unit_match.group(2)

            conv_match = re.search(r"(1\s*[A-Za-z=0-9\s]*Stück)", line)
            if conv_match:
                unit_conversion = conv_match.group(1)

            price_match = re.search(
                r"([\d\.,]+)\s*pro", line, flags=re.IGNORECASE
            )
            if price_match:
                unit_price = parse_number(price_match.group(1))


            items.append(
                LineItem(
                    position=position,
                    description=description,
                    quantity=quantity,
                    unit=unit,
                    unit_conversion=unit_conversion,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )
            break

    return items


def extract_invoice_from_text(text: str, source_file: str | None = None) -> Invoice:
    lang = detect_language(text)
    invoice_number = _search_patterns("invoice_number", lang, text)
    invoice_date = _search_patterns("invoice_date", lang, text)
    customer_number = _search_patterns("customer_number", lang, text)
    end_customer_number = _search_patterns("end_customer_number", lang, text)
    payment_terms = _search_patterns("payment_terms", lang, text)
    delivery_terms = _search_patterns("delivery_terms", lang, text)
    delivery_date = _search_patterns("delivery_date", lang, text)
    currency = _search_patterns("currency", lang, text) or "EUR"

    totals = _extract_totals(text)
    parties = _extract_parties(text)
    purchase_order_number = _extract_purchase_order(text)
    line_items = _extract_line_items(text)

    return Invoice(
        invoice_number=invoice_number,
        purchase_order_number=purchase_order_number,
        invoice_date=invoice_date,
        customer_number=customer_number,
        end_customer_number=end_customer_number,
        payment_terms=payment_terms,
        delivery_terms=delivery_terms,
        delivery_date=delivery_date,
        currency=currency,
        net_total=totals["net_total"],
        tax_rate=totals["tax_rate"],
        tax_amount=totals["tax_amount"],
        gross_total=totals["gross_total"],
        seller_name=parties["seller_name"],
        seller_address=parties["seller_address"],
        buyer_name=parties["buyer_name"],
        buyer_address=parties["buyer_address"],
        line_items=line_items,
        notes=None,
        source_file=source_file,
    )


def extract_invoices_from_dir(pdf_dir: str) -> List[Invoice]:
    invoices: List[Invoice] = []
    for filename in os.listdir(pdf_dir):
        if not filename.lower().endswith(".pdf"):
            continue
        path = os.path.join(pdf_dir, filename)
        text = extract_text_from_pdf(path)
        invoice = extract_invoice_from_text(text, source_file=filename)
        invoices.append(invoice)
    return invoices
