from flask import (
    Flask,
    render_template,
    request,
    send_file,
    after_this_request
)

import fitz
import pathlib
import tempfile
import shutil
import threading
import webbrowser
import os
import sys
import uuid


# ==================================================
# Compatibilité PyInstaller
# ==================================================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


app = Flask(
    __name__,
    template_folder=resource_path("templates")
)

# Limite d'upload : 500 Mo
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


# ==================================================
# Ouverture automatique du navigateur
# ==================================================

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


# ==================================================
# Extraction des fichiers embarqués
# ==================================================

def extract_embedded_files_from_pdfs(pdf_folder, output_folder):

    extracted_count = 0

    pdf_files = pathlib.Path(pdf_folder).rglob("*.pdf")

    for pdf_file in pdf_files:

        try:

            with fitz.open(pdf_file) as doc:

                emb_count = doc.embfile_count()

                if emb_count == 0:
                    continue

                pdf_name = pdf_file.stem

                for index in range(emb_count):

                    info = doc.embfile_info(index)

                    filename = (
                        info.get("ufilename")
                        or info.get("filename")
                        or f"attachment_{index}"
                    )

                    output_path = (
                        pathlib.Path(output_folder)
                        / pdf_name
                        / filename
                    )

                    output_path.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    output_path.write_bytes(
                        doc.embfile_get(index)
                    )

                    extracted_count += 1

        except Exception as e:

            print(
                f"[ERREUR] {pdf_file} : {e}"
            )

    return extracted_count


# ==================================================
# Création ZIP
# ==================================================

def create_zip(source_folder):

    zip_base = os.path.join(
        tempfile.gettempdir(),
        f"extracted_{uuid.uuid4().hex}"
    )

    shutil.make_archive(
        zip_base,
        "zip",
        source_folder
    )

    return f"{zip_base}.zip"


# ==================================================
# Routes
# ==================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():

    if "pdf_folder" not in request.files:
        return "Aucun fichier reçu.", 400

    uploaded_files = request.files.getlist("pdf_folder")

    if not uploaded_files:
        return "Aucun fichier reçu.", 400

    temp_pdf_folder = tempfile.mkdtemp(
        prefix="pdf_input_"
    )

    temp_output_folder = tempfile.mkdtemp(
        prefix="pdf_output_"
    )

    try:

        # ------------------------------------------
        # Sauvegarde des fichiers uploadés
        # ------------------------------------------

        for file in uploaded_files:

            if not file.filename:
                continue

            if not file.filename.lower().endswith(".pdf"):
                continue

            relative_path = (
                file.filename.replace("\\", "/")
            )

            file_path = os.path.join(
                temp_pdf_folder,
                relative_path
            )

            os.makedirs(
                os.path.dirname(file_path),
                exist_ok=True
            )

            file.save(file_path)

        # ------------------------------------------
        # Extraction
        # ------------------------------------------

        extracted_count = extract_embedded_files_from_pdfs(
            temp_pdf_folder,
            temp_output_folder
        )

        if extracted_count == 0:
            return (
                "Aucun fichier embarqué trouvé dans les PDF.",
                404
            )

        # ------------------------------------------
        # ZIP
        # ------------------------------------------

        zip_path = create_zip(
            temp_output_folder
        )

        # Suppression auto après téléchargement
        @after_this_request
        def remove_zip(response):

            try:

                if os.path.exists(zip_path):
                    os.remove(zip_path)

            except Exception as e:

                print(
                    f"Impossible de supprimer "
                    f"{zip_path} : {e}"
                )

            return response

        return send_file(
            zip_path,
            as_attachment=True,
            download_name="fichiers_extraits.zip"
        )

    finally:

        shutil.rmtree(
            temp_pdf_folder,
            ignore_errors=True
        )

        shutil.rmtree(
            temp_output_folder,
            ignore_errors=True
        )


# ==================================================
# Lancement
# ==================================================

if __name__ == "__main__":

    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Timer(
            1.5,
            open_browser
        ).start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )