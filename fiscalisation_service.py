import requests
import qrcode
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

# Fiscalization engine
def fiscalize(payload):
    url = "https://remote-backend/api/fiscalize"
    response = requests.post(url, json=payload)
    return response.json()

# Stamping engine
def stamp_pdf(pdf_path, qr_url):
    qr_code_path = "qr_code.png"
    generate_qr(qr_url, qr_code_path)

    output_path = pdf_path.replace('unprocessed', 'processed')
    overlay = create_qr_overlay(qr_code_path)
    merge_pdfs(pdf_path, overlay, output_path)

def generate_qr(data, output_path):
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make()
    img = qr.make_image()
    img.save(output_path)

def create_qr_overlay(qr_code_path):
    overlay_path = "overlay.pdf"
    c = canvas.Canvas(overlay_path)
    c.drawImage(qr_code_path, 50, 750, width=100, height=100)
    c.save()
    return overlay_path

def merge_pdfs(original, overlay, output):
    original_reader = PdfReader(original)
    overlay_reader = PdfReader(overlay)
    writer = PdfWriter()

    for page in original_reader.pages:
        writer.add_page(page)
    writer.add_page(overlay_reader.pages[0])

    with open(output, 'wb') as out_file:
        writer.write(out_file)

if __name__ == "__main__":
    # Test fiscalization and stamping
    payload = {"type": "invoice", "content": "Sample data"}
    print(fiscalize(payload))
