import time
from cue import pdf_queue  # Ensure the correct import name
import pdfplumber  # or PyPDF2
from fiscalisation_service import fiscalize
from datetime import datetime
from fiscalisation_service import stamp_pdf

def extract_data_from_pdf(pdf_path):
    """Extract relevant data from the PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or '' for page in pdf.pages)
        
        lines = text.splitlines()

        # Determine document type
        if "CREDIT NOTE" in text:
            return extract_credit_note_data(lines)
        elif "Fiscal Tax Invoice" in text:
            return extract_invoice_data(lines)
        else:
            raise ValueError("Unsupported document type")

    except Exception as e:
        print(f"Error extracting data from {pdf_path}: {e}")
        return None

def extract_invoice_data(lines):
    """Extract invoice data dynamically."""
    device_id = 19014
    invoice_no = extract_field(lines, "Document No.")
    receipt_date = extract_field(lines, "Date")
    formatted_date = datetime.strptime(receipt_date, '%d/%m/%Y').strftime('%Y-%m-%dT%H:%M:%S')
    currency = "USD" if "USD" in lines[-1] else extract_currency(lines)
    
    receipt_lines = extract_items(lines)
    total_payment = sum(item["quantity"] * item["unit_price"] for item in receipt_lines)

    return {
        "deviceID": device_id,
        "receiptType": "FISCALINVOICE",
        "receiptCurrency": currency,
        "receiptCounter": None,  # Placeholder for dynamic value
        "receiptGlobalNo": None,  # Placeholder for dynamic value
        "invoiceNo": invoice_no,
        "receiptDate": formatted_date,
        "receiptLines": receipt_lines,
        "receiptPayments": [{"moneyTypeCode": 1, "paymentAmount": total_payment}]
    }

def extract_credit_note_data(lines):
    """Extract credit note data dynamically."""
    device_id = 19250
    invoice_no = extract_field(lines, "Document No.")
    receipt_date = extract_field(lines, "Date")
    fiscal_day_no = extract_field(lines, "Fiscal Day#")
    referenced_receipt_no = extract_field(lines, "Zimra Invoice#")
    
    formatted_date = datetime.strptime(receipt_date, '%d/%m/%Y').strftime('%Y-%m-%dT%H:%M:%S')
    currency = "USD" if "USD" in lines[-1] else extract_currency(lines)
    
    receipt_lines = extract_items(lines, is_credit=True)
    total_payment = sum(item["quantity"] * item["unit_price"] for item in receipt_lines)

    return {
        "deviceID": device_id,
        "receiptType": "CREDITNOTE",
        "receiptCurrency": currency,
        "receiptCounter": None,  # Placeholder for dynamic value
        "receiptGlobalNo": None,  # Placeholder for dynamic value
        "invoiceNo": invoice_no,
        "receiptNotes": "Incorrectly supplied goods",  # Example note
        "receiptDate": formatted_date,
        "creditDebitNote": {
            "deviceID": device_id,
            "receiptGlobalNo": int(referenced_receipt_no),
            "fiscalDayNo": int(fiscal_day_no)
        },
        "receiptLines": receipt_lines,
        "receiptPayments": [{"moneyTypeCode": 1, "paymentAmount": total_payment}]
    }

def extract_currency(lines):
    """Find the currency in the document if USD isn't explicitly mentioned."""
    for line in lines:
        if "USD" in line:
            return "USD"
        elif "ZWL" in line:
            return "ZWL"
    return "Unknown"

def extract_items(lines, is_credit=False):
    """Extract item lines for invoices or credit notes."""
    receipt_lines = []
    item_start = False

    for line in lines:
        if "Description" in line:
            item_start = True
            continue
        if item_start and "USD" not in line:
            parts = line.split()
            if len(parts) >= 4:
                item_name = parts[0]
                try:
                    qty = int(parts[1])
                except ValueError:
                    item_name += f" {parts[1]}"
                    try:
                        qty = int(parts[2])
                    except ValueError:
                        item_name += f" {parts[2]}"
                        qty = int(parts[3])
                unit_price = float(parts[-2])
                tax_percent = float(parts[-1].strip('%')) if '%' in parts[-1] else 0.0

                if is_credit:
                    qty = abs(qty) * -1
                    unit_price = abs(unit_price) * -1
                
                receipt_lines.append({
                    "item_name": item_name,
                    "tax_percent": tax_percent,
                    "quantity": qty,
                    "unit_price": unit_price
                })
    return receipt_lines

def extract_field(lines, field_name):
    """Helper to extract fields from the text based on the field name."""
    for line in lines:
        if field_name in line:
            return line.split(field_name)[-1].strip()
    return None

def send_to_fiscalization(payload, pdf_path):
    """Send extracted data to the fiscalization engine."""
    try:
        response = fiscalize(payload)
        if response.get("success"):
            qr_url = response["qr_url"]
            stamp_pdf(pdf_path, qr_url)
            print(f"Successfully stamped QR on {pdf_path}")
        else:
            raise ValueError(response.get("error", "Unknown error"))
    except Exception as e:
        print(f"Fiscalization failed for {pdf_path}: {e}")

def process_queue():
    """Continuously process files from the queue."""
    while True:
        if not pdf_queue.empty():
            pdf_path = pdf_queue.get()
            print(f"Processing {pdf_path}")
            
            payload = extract_data_from_pdf(pdf_path)
            if payload:
                send_to_fiscalization(payload, pdf_path)
            else:
                print(f"Skipping {pdf_path} due to extraction failure.")
        else:
            time.sleep(1)

if __name__ == "__main__":
    print("Starting PDF extraction engine...")
    process_queue()
