# invoice_qc/validator.py
from collections import Counter
from typing import List, Dict, Any, Tuple, Set

from .schemas import Invoice
from .utils import approx_equal


def validate_invoice(
    invoice: Invoice, seen_keys: Set[Tuple[str, str, str]]
) -> Dict[str, Any]:
    errors: List[str] = []

    inv_num = invoice.invoice_number or ""
    inv_date = invoice.invoice_date or ""
    seller_name = invoice.seller_name or ""

    # --- Completeness ---
    if not invoice.invoice_number:
        errors.append("missing_field: invoice_number")
    if not invoice.invoice_date:
        errors.append("missing_field: invoice_date")
    if not invoice.seller_name:
        errors.append("missing_field: seller_name")
    if not invoice.buyer_name:
        errors.append("missing_field: buyer_name")

    if invoice.net_total is None:
        errors.append("missing_field: net_total")
    if invoice.tax_amount is None:
        errors.append("missing_field: tax_amount")
    if invoice.gross_total is None:
        errors.append("missing_field: gross_total")

    # --- Format / type rules ---
    allowed_currencies = {"EUR", "USD", "INR"}
    if invoice.currency and invoice.currency.upper() not in allowed_currencies:
        errors.append("format_error: unsupported_currency")

    for field_name in ["net_total", "tax_amount", "gross_total"]:
        value = getattr(invoice, field_name)
        if value is not None and not isinstance(value, (int, float)):
            errors.append(f"format_error: {field_name}_not_numeric")

    # --- Business rules ---
    # Sum of line item totals ≈ net_total
    if invoice.line_items and invoice.net_total is not None:
        sum_lines = sum(
            li.line_total or 0.0 for li in invoice.line_items if li.line_total is not None
        )
        if sum_lines and not approx_equal(sum_lines, invoice.net_total):
            errors.append("business_rule_failed: net_total_mismatch_line_items")

    # net_total + tax_amount ≈ gross_total
    if (
        invoice.net_total is not None
        and invoice.tax_amount is not None
        and invoice.gross_total is not None
    ):
        if not approx_equal(
            invoice.net_total + invoice.tax_amount, invoice.gross_total
        ):
            errors.append("business_rule_failed: totals_mismatch")

    # --- Anomaly rules ---
    for field_name in ["net_total", "tax_amount", "gross_total"]:
        value = getattr(invoice, field_name)
        if value is not None and value < 0:
            errors.append(f"anomaly: {field_name}_negative")

    # duplicate detection
    if inv_num and inv_date and seller_name:
        key = (inv_num, inv_date, seller_name)
        if key in seen_keys:
            errors.append("duplicate_invoice")
        else:
            seen_keys.add(key)

    is_valid = len(errors) == 0
    invoice_id = invoice.invoice_number or invoice.source_file or "unknown"

    return {
        "invoice_id": invoice_id,
        "is_valid": is_valid,
        "errors": errors,
    }


def validate_invoices(invoices: List[Invoice]) -> Dict[str, Any]:
    seen_keys: Set[Tuple[str, str, str]] = set()
    per_invoice: List[Dict[str, Any]] = []

    for inv in invoices:
        result = validate_invoice(inv, seen_keys)
        per_invoice.append(result)

    error_counter = Counter()
    for r in per_invoice:
        for e in r["errors"]:
            error_counter[e] += 1

    total = len(invoices)
    valid = sum(1 for r in per_invoice if r["is_valid"])
    invalid = total - valid

    summary = {
        "total_invoices": total,
        "valid_invoices": valid,
        "invalid_invoices": invalid,
        "error_counts": dict(error_counter),
    }

    return {
        "summary": summary,
        "results": per_invoice,
    }
