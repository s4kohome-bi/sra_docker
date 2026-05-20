import os
import json
import requests
import re

from flask import Flask, request, jsonify, abort, render_template
from xml.etree import ElementTree as ET

from services.line_service import line_webhook
from services.receipt_workflow import process_receipt_file
from services.db_service import init_db, save_receipt, query_db, query_db_weekly

app = Flask(__name__)

#==========================
#   測試 
#==========================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()

# =====================================================
# common functions
# =====================================================
def process_receipt(requestfile):
    if requestfile.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, requestfile.filename)
    requestfile.save(filepath)
    data = process_receipt_file(filepath, "Web", "W12345")
    return data

@app.route("/")
def home():
    return render_template("index.html")

# =====================================================
# web service
# =====================================================
@app.route("/upload-page")
def upload_page():
    return render_template("upload.html")

# web-page entry
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["receipt"]
    data = process_receipt(file)

    return f"""
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">    

    </head>
    <div class="container">
        <h3>OCR Result:</h3>
        <pre>{data}</pre>
        <br>
        <a href="/">Back</a>
    </div>
        """
# =====================================================
# show receipts in web page
# =====================================================
@app.route("/receipts")
def show_receipts():
    rows = query_db()
    return render_template("receipts.html", receipts = rows)


# =====================================================
#  API functions : return JSON
# =====================================================

@app.route("/api/process_receipt", methods=["POST"])
def process_receipt_api():
    if "receipt" not in request.files:
        return jsonify({
            "error" : "No image uploaded"
            }), 400
    file = request.files["receipt"]
    data = process_receipt(file)
    return jsonify(data)

@app.route("/api/reports/weekly")
def weekly_report():
    rows = query_db_weekly()
    return jsonify(rows)

@app.route("/api/reports/receipts")
def receipts_report():
    rows = query_db()
    return jsonify(rows)

# =====================================================
# Webhook (from Line)
# =====================================================
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    if False == line_webhook(body, signature):
        abort(400)
    return "OK"

    
if __name__ == "__main__":
#    app.run(debug=True
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
