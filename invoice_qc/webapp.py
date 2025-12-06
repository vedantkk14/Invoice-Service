from flask import Flask, render_template, request, jsonify
import io
import pdfplumber

from .extractor import extract_invoice_from_text
from .validator import validate_invoices

app = Flask(__name__)

import os
print("Current working dir:", os.getcwd())
print("Template folder:", os.path.abspath("templates"))


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("pdfs")

    invoices = []
    for file in files:
        content = file.read()
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            texts = []
            for page in pdf.pages:
                t = page.extract_text() or ""
                texts.append(t)
            text = "\n".join(texts)

        invoice = extract_invoice_from_text(text, source_file=file.filename)
        invoices.append(invoice)

    result = validate_invoices(invoices)

    return render_template(
        "index.html",
        extracted=[inv.dict() for inv in invoices],
        validation=result
    )
