# invoice_qc/api.py
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from .schemas import Invoice
from .validator import validate_invoices
from .extractor import extract_invoice_from_text, extract_text_from_pdf

import io
import pdfplumber

app = FastAPI(title="Invoice QC Service")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/validate-json")
def validate_json(invoices: List[Invoice]) -> Dict[str, Any]:
    result = validate_invoices(invoices)
    return result


@app.post("/extract-and-validate-pdfs")
async def extract_and_validate_pdfs(
    files: List[UploadFile] = File(...)
) -> JSONResponse:
    invoices: List[Invoice] = []
    for f in files:
        content = await f.read()
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            texts = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                texts.append(page_text)
            text = "\n".join(texts)
        invoice = extract_invoice_from_text(text, source_file=f.filename)
        invoices.append(invoice)

    validation = validate_invoices(invoices)
    response = {
        "extracted_invoices": [inv.dict() for inv in invoices],
        "validation": validation,
    }
    return JSONResponse(content=response)
