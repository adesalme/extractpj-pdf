from flask import Flask, render_template, request, send_file
import pathlib
import fitz
import os
import shutil
import zipfile

app = Flask(__name__)

# Fonction pour extraire les fichiers embarqués des PDFs
def extract_embedded_files_from_pdfs(pdf_folder, output_folder):
    pdf_files = pathlib.Path(pdf_folder).rglob("*.pdf")
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    for pdf_file in pdf_files:
        doc = fitz.open(pdf_file)
        for item in range(doc.embfile_count()):
            info = doc.embfile_info(item)
            output_path = pathlib.Path(output_folder) / info["ufilename"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(doc.embfile_get(item))

# Fonction pour compresser le dossier en un fichier ZIP
def zip_directory(output_folder, zip_filename):
    shutil.make_archive(zip_filename, 'zip', output_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    if 'pdf_folder' not in request.files:
        return "Aucun dossier PDF n'a été téléchargé."

    pdf_folder = request.files.getlist('pdf_folder')

    if not pdf_folder:
        return "Aucun fichier trouvé dans le dossier PDF."

    # Créer un répertoire temporaire pour les fichiers reçus
    temp_pdf_folder = 'temp_pdf_folder'
    temp_output_folder = 'temp_output_folder'

    # Créer les répertoires temporaires s'ils n'existent pas
    os.makedirs(temp_pdf_folder, exist_ok=True)
    os.makedirs(temp_output_folder, exist_ok=True)

    # Sauvegarder les fichiers reçus dans le répertoire temporaire
    for file in pdf_folder:
        file_path = os.path.join(temp_pdf_folder, file.filename)
        # Créer le dossier parent s'il n'existe pas
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

    # Exécuter l'extraction des fichiers embarqués
    extract_embedded_files_from_pdfs(temp_pdf_folder, temp_output_folder)

    # Créer un fichier ZIP contenant les fichiers extraits
    extracted_zip = 'extracted_files.zip'
    zip_directory(temp_output_folder, extracted_zip.replace('.zip', ''))

    # Nettoyer les dossiers temporaires
    shutil.rmtree(temp_pdf_folder)
    shutil.rmtree(temp_output_folder)

    # Retourner le fichier ZIP contenant les fichiers extraits
    return send_file(extracted_zip, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
