# invoice_qc/utils.py
import re
from typing import Optional


def parse_number(value: str) -> Optional[float]:
    """
    Convert strings like '64,00', '64.00', ' 64,00 EUR' to float.
    Returns None if parsing fails.
    """
    if value is None:
        return None
    text = value.strip()
    # Remove currency symbols/words
    text = re.sub(r"[^\d,.\-]", "", text)
    if not text:
        return None
    # If comma is decimal separator and dot is thousands separator
    if "," in text and "." in text:
        # assume European style: 1.234,56 -> 1234.56
        text = text.replace(".", "").replace(",", ".")
    elif "," in text and "." not in text:
        # 64,00 -> 64.00
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def approx_equal(a: Optional[float], b: Optional[float], tol: float = 0.5) -> bool:
    if a is None or b is None:
        return False
    return abs(a - b) <= tol
