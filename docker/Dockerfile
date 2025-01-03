# Utilise une image de base Python
FROM python:3.9-slim

# Mise à jour du système et installation de dépendances nécessaires pour tkinter et fitz
RUN apt-get update && apt-get install -y \
    libx11-dev \
    libxtst-dev \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Installation de PyMuPDF et Flask
RUN pip install --no-cache-dir pymupdf flask

# Créer un répertoire pour l'application
WORKDIR /app

# Copier le script Python dans l'image
COPY . /app

# Exposer le port 5000 pour l'application Flask
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["python", "app.py"]
