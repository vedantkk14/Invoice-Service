<h1 align="center">📄 Invoice Extraction & Quality Control Service</h1>
<p align="center">A complete PDF → JSON → Validation pipeline with CLI, API, and Web UI</p>

<hr/>

<h2>📌 Overview</h2>
<p>This project implements a small but realistic <b>Invoice Extraction & Quality Control (QC) Service</b>.</p>

<p>It automatically:</p>
<ul>
  <li>Reads invoice PDFs</li>
  <li>Extracts structured JSON fields</li>
  <li>Validates extracted data using completeness, format, business, and anomaly rules</li>
  <li>Exposes functionality via:
    <ul>
      <li>✔ Python CLI</li>
      <li>✔ FastAPI HTTP service</li>
      <li>✔ Simple Flask-based UI (Web QC Console)</li>
    </ul>
  </li>
</ul>

<h3>✔ Completed Components</h3>
<table>
  <tr><th>Component</th><th>Status</th></tr>
  <tr><td>PDF Extraction</td><td>✅ Completed</td></tr>
  <tr><td>Validation Core</td><td>✅ Completed</td></tr>
  <tr><td>CLI Tool</td><td>✅ Completed</td></tr>
  <tr><td>HTTP API (FastAPI)</td><td>✅ Completed</td></tr>
  <tr><td>Web UI Console (Flask)</td><td>✅ Completed</td></tr>
  <tr><td>README + Architecture Docs</td><td>✅ Completed</td></tr>
</table>

<hr/>

<h2>📌 Schema & Validation Design</h2>

<h3>🧱 Invoice Schema (Key Fields)</h3>

<table>
  <tr><th>Field</th><th>Description</th></tr>
  <tr><td>invoice_number</td><td>Unique invoice identifier</td></tr>
  <tr><td>purchase_order_number</td><td>Customer purchase order number</td></tr>
  <tr><td>invoice_date</td><td>Invoice issue date</td></tr>
  <tr><td>due_date</td><td>Payment due date</td></tr>
  <tr><td>customer_number</td><td>Customer reference number</td></tr>
  <tr><td>end_customer_number</td><td>Final client identifier</td></tr>
  <tr><td>seller_name</td><td>Merchant / Supplier name</td></tr>
  <tr><td>seller_address</td><td>Supplier address block</td></tr>
  <tr><td>buyer_name</td><td>Customer name</td></tr>
  <tr><td>buyer_address</td><td>Customer address</td></tr>
  <tr><td>currency</td><td>Currency used (EUR, USD, INR)</td></tr>
  <tr><td>net_total</td><td>Total amount excluding taxes</td></tr>
  <tr><td>tax_rate</td><td>Tax percentage</td></tr>
  <tr><td>tax_amount</td><td>Tax amount</td></tr>
  <tr><td>gross_total</td><td>Total including tax</td></tr>
  <tr><td>line_items[]</td><td>Rows: description, quantity, unit, price</td></tr>
</table>

<h3>📌 Validation Rules</h3>

<h4>✔ Completeness Rules</h4>
<ul>
  <li>Invoice number must not be empty</li>
  <li>Invoice date must be present</li>
  <li>Seller & buyer names must exist</li>
  <li>Net, tax, and gross totals must not be missing</li>
</ul>
<b>Rationale:</b> Essential for billing and audit processes.

<hr/>

<h4>✔ Type / Format Rules</h4>
<ul>
  <li>Currency must be one of: <code>EUR / USD / INR</code></li>
  <li>Totals must be numeric</li>
  <li>Date fields must be valid strings</li>
</ul>
<b>Rationale:</b> Prevents incorrect calculations.

<hr/>

<h4>✔ Business Rules</h4>
<ul>
  <li>Sum(line_item_totals) ≈ net_total</li>
  <li>net_total + tax_amount ≈ gross_total</li>
</ul>
<b>Rationale:</b> Ensures invoice math consistency.

<hr/>

<h4>✔ Anomaly / Duplicate Rules</h4>
<ul>
  <li>Totals must not be negative</li>
  <li>Duplicate invoices detected via <code>(invoice_number, invoice_date, seller_name)</code></li>
</ul>

<hr/>

<h2>📌 Architecture</h2>

<h3>📁 Folder Structure</h3>

<pre>
invoice-qc-service/
│
├── invoice_qc/
│   ├── extractor.py        # PDF → Text → Field extraction
│   ├── validator.py        # All validation rules
│   ├── schemas.py          # Pydantic models
│   ├── cli.py              # CLI interface
│   ├── api.py              # FastAPI service
│   └── webapp.py           # Flask web UI
│
├── templates/
│   └── index.html          # Web interface UI
│
├── static/                 # Optional CSS/JS
├── pdfs/                   # Sample invoices
│
├── main.py                 # API server (FastAPI)
├── main_web.py             # Flask Web UI launcher
├── requirements.txt
└── README.md
</pre>

<hr/>

<h2>📌 System Flow Diagram</h2>

``mermaid
flowchart LR
  A[PDFs] --> B[Extraction Module<br>(pdfplumber + regex)]
  B --> C[Invoice JSON Objects]
  C --> D[Validation Core]
  D --> E{Interfaces}
  E --> F[CLI Output<br>(Reports)]
  E --> G[FastAPI HTTP Endpoints]
  E --> H[Web UI Console]

  <hr/> <h2>📌 Component Explanations</h2> <h3>🔹 Extraction Pipeline</h3> <ul> <li>Reads raw PDFs using pdfplumber</li> <li>Detects language (DE/EN)</li> <li>Applies regex patterns to locate invoice fields</li> <li>Constructs structured <code>Invoice</code> objects</li> <li>Extracts line items using heuristics</li> </ul> <h3>🔹 Validation Core</h3> <ul> <li>Runs all rules</li> <li>Produces per-invoice results</li> <li>Generates aggregated error counts</li> </ul> <h3>🔹 CLI Tool</h3> <b>Extract Only:</b> <pre>python -m invoice_qc.cli extract --pdf-dir pdfs --output extracted.json</pre>

<b>Validate Only:</b>

<pre>python -m invoice_qc.cli validate --input extracted.json --report validation_report.json</pre>

<b>Full Pipeline:</b>
<pre>python -m invoice_qc.cli full-run --pdf-dir pdfs --report validation_report.json</pre> <h3>🔹 HTTP API (FastAPI)</h3> <ul> <li>GET /health</li> <li>POST /validate-json</li> <li>POST /extract-and-validate-pdfs</li> </ul> <h3>🔹 Web UI (Flask)</h3> <ul> <li>Upload multiple PDFs</li> <li>View extracted JSON</li> <li>View validation results</li> <li>Valid/Invalid badges</li> </ul> <hr/> <h2>📌 Setup & Installation</h2> <h3>🧩 Requirements</h3> <ul> <li>Python 3.10+</li> <li>pip</li> </ul> <h3>🛠 Environment Setup</h3> <pre> python -m venv .venv .venv\Scripts\activate # Windows source .venv/bin/activate # Mac/Linux pip install -r requirements.txt </pre> <hr/> <h2>📌 Running the CLI</h2>

<b>Extract:</b>

<pre>python -m invoice_qc.cli extract --pdf-dir pdfs --output extracted.json</pre>

<b>Validate:</b>

<pre>python -m invoice_qc.cli validate --input extracted.json --report validation_report.json</pre>

<b>Full Run:</b>

<pre>python -m invoice_qc.cli full-run --pdf-dir pdfs --report validation_report.json</pre> <hr/> <h2>📌 Running the API (FastAPI)</h2> <pre>python main.py</pre>

Open:

<pre>http://127.0.0.1:8000/docs</pre>

<b>Example cURL:</b>

<pre>curl http://127.0.0.1:8000/health</pre> <hr/> <h2>📌 Running the Web UI (Flask)</h2> <pre>python main_web.py</pre>

Open:

<pre>http://127.0.0.1:5000/</pre> <hr/> <h2>📌 Usage Examples</h2> <h3>CLI Example</h3> <pre>python -m invoice_qc.cli full-run --pdf-dir pdfs --report validation.json</pre> <h3>API Example (Postman)</h3> <pre>POST http://127.0.0.1:8000/validate-json</pre> Body: raw JSON list of invoices <hr/> <h2>📌 AI Usage Notes</h2> <p>AI tools were used for:</p> <ul> <li>Generating initial folder structure</li> <li>Refining regex patterns</li> <li>FastAPI + Flask boilerplate</li> <li>Documentation structure</li> </ul> <h3>⚠ Example where AI was incorrect:</h3> <p>AI-generated regex incorrectly matched unrelated numeric fields.</p> <b>Fix:</b> Targeted invoice-specific keywords such as <code>Gesamtwert EUR</code>. <hr/> <h2>📌 Assumptions & Limitations</h2> <ul> <li>Extraction logic based on German/English invoices</li> <li>Line items extracted with heuristic parsing</li> <li>Complex PDFs may require OCR/ML</li> <li>No authentication added to API</li> <li>Currency detection pattern-based only</li> </ul> <hr/> <h2>🎥 Explanation Video (10–20 min)</h2> <ul> <li>Project overview</li> <li>Architecture walkthrough</li> <li>Extractor, Validator, CLI, API explanation</li> <li>Demo of CLI + API + Web UI</li> </ul> <b>➡ Video Link: (Add after uploading to Google Drive)</b> <hr/> <h2 align="center">🚀 Project Completed Successfully</h2> <p align="center">PDF → Text → JSON → Validation → CLI/API/UI</p> ```
