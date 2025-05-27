import PyInstaller.__main__

PyInstaller.__main__.run([
    'PDFAPP.py',
    '--onefile',
    '--windowed',
    '--name=PDFExtractor',
    '--add-data=README.md;.'
]) 