import tkinter as tk
from tkinter import filedialog
import fitz
import pathlib

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

def browse_pdfs():
    folder_selected = filedialog.askdirectory()
    return folder_selected

def browse_output():
    folder_selected = filedialog.askdirectory()
    return folder_selected

def run_application():
    pdf_folder = browse_pdfs()
    if not pdf_folder:
        return
    output_folder = browse_output()
    if not output_folder:
        return
    extract_embedded_files_from_pdfs(pdf_folder, output_folder)
    success_label.config(text="Extraction terminée!")

# Création de la fenêtre principale
root = tk.Tk()
root.title("Extraction de fichiers embarqués PDF")

# Boutons et étiquettes
pdf_button = tk.Button(root, text="Sélectionner le dossier PDF", command=browse_pdfs)
pdf_button.pack(pady=10)

output_button = tk.Button(root, text="Sélectionner le dossier de sortie", command=browse_output)
output_button.pack(pady=10)

run_button = tk.Button(root, text="Exécuter l'extraction", command=run_application)
run_button.pack(pady=20)

success_label = tk.Label(root, text="")
success_label.pack(pady=10)

# Lancer l'interface
root.mainloop()
