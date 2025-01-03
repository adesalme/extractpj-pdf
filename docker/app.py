from flask import Flask, render_template, request, redirect, url_for
import pathlib
import fitz
import os
import shutil

app = Flask(__name__)

def extract_embedded_files_from_pdfs(directory, output_directory):
    pdf_files = pathlib.Path(directory).rglob("*.pdf")
    pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)

    for pdf_file in pdf_files:
        doc = fitz.open(pdf_file)
        for item in range(doc.embfile_count()):
            info = doc.embfile_info(item)
            output_path = pathlib.Path(output_directory) / info["ufilename"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(doc.embfile_get(item))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    if 'pdf_folder' not in request.files or 'output_folder' not in request.files:
        return redirect(request.url)

    pdf_folder = request.form['pdf_folder']
    output_folder = request.form['output_folder']

    if not pdf_folder or not output_folder:
        return "Les dossiers doivent être spécifiés."

    if not os.path.exists(pdf_folder) or not os.path.exists(output_folder):
        return "Les dossiers spécifiés n'existent pas."

    # Exécuter l'extraction
    extract_embedded_files_from_pdfs(pdf_folder, output_folder)
    return "Extraction terminée!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
