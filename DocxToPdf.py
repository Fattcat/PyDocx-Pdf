from flask import Flask, request, send_file, render_template, jsonify
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'   # CREATE THIS FOLDER
OUTPUT_FOLDER = 'output'    # AND ALSO CREATE THIS FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.docx'):
        return "Neplatný súbor! Nahrajte DOCX súbor."

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    pdf_path = convert_docx_to_pdf(filepath)
    pdf_filename = os.path.basename(pdf_path)

    return jsonify({"filename": pdf_filename})

def convert_docx_to_pdf(docx_path):
    document = Document(docx_path)
    pdf_path = os.path.join(OUTPUT_FOLDER, os.path.basename(docx_path).replace('.docx', '.pdf'))

    pdf = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    style = getSampleStyleSheet()["Normal"]

    for paragraph in document.paragraphs:
        text = escape(paragraph.text)
        story.append(Paragraph(text, style))

    pdf.build(story)
    return pdf_path

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filename = os.path.basename(filename)  # safety
    path = os.path.join(OUTPUT_FOLDER, filename)

    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "Súbor neexistuje!"

if __name__ == '__main__':
    app.run(debug=True)
