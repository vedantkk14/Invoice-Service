# invoice_qc/cli.py
import argparse
import json
import sys
from pathlib import Path
from typing import List

from .extractor import extract_invoices_from_dir
from .validator import validate_invoices
from .schemas import Invoice


def _save_json(data, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_invoices_from_json(path: str) -> List[Invoice]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Invoice(**item) for item in raw]


def cmd_extract(args: argparse.Namespace):
    invoices = extract_invoices_from_dir(args.pdf_dir)
    data = [inv.dict() for inv in invoices]
    _save_json(data, args.output)
    print(f"Extracted {len(invoices)} invoices to {args.output}")


def cmd_validate(args: argparse.Namespace):
    invoices = _load_invoices_from_json(args.input)
    result = validate_invoices(invoices)
    _save_json(result, args.report)

    summary = result["summary"]
    print("Validation Summary:")
    print(f"  Total invoices : {summary['total_invoices']}")
    print(f"  Valid          : {summary['valid_invoices']}")
    print(f"  Invalid        : {summary['invalid_invoices']}")
    print("  Error counts:")
    for err, count in summary["error_counts"].items():
        print(f"    {err}: {count}")

    if summary["invalid_invoices"] > 0:
        sys.exit(1)


def cmd_full_run(args: argparse.Namespace):
    # 1) Extract
    invoices = extract_invoices_from_dir(args.pdf_dir)
    # 2) Validate
    result = validate_invoices(invoices)
    _save_json(result, args.report)

    summary = result["summary"]
    print("Full Run Summary:")
    print(f"  Total invoices : {summary['total_invoices']}")
    print(f"  Valid          : {summary['valid_invoices']}")
    print(f"  Invalid        : {summary['invalid_invoices']}")
    print("  Error counts:")
    for err, count in summary["error_counts"].items():
        print(f"    {err}: {count}")

    if summary["invalid_invoices"] > 0:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="invoice-qc",
        description="Invoice extraction and quality control CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract
    p_extract = subparsers.add_parser("extract", help="Extract invoices from PDFs")
    p_extract.add_argument("--pdf-dir", required=True, help="Directory with PDF files")
    p_extract.add_argument(
        "--output",
        required=True,
        help="Path to output JSON file with extracted invoices",
    )
    p_extract.set_defaults(func=cmd_extract)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate extracted invoices")
    p_validate.add_argument(
        "--input", required=True, help="Input JSON with invoices (from extract)"
    )
    p_validate.add_argument(
        "--report",
        required=True,
        help="Path to output validation report JSON",
    )
    p_validate.set_defaults(func=cmd_validate)

    # full-run
    p_full = subparsers.add_parser(
        "full-run", help="Extract and validate in one step"
    )
    p_full.add_argument("--pdf-dir", required=True, help="Directory with PDF files")
    p_full.add_argument(
        "--report",
        required=True,
        help="Path to output validation report JSON",
    )
    p_full.set_defaults(func=cmd_full_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
