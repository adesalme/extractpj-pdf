build sur linux

pyinstaller \
  --clean \
  --noconfirm \
  --onefile \
  --windowed \
  --add-data "templates:templates" \
  app.py

build sur windows

pyinstaller ^
--onefile ^
--windowed ^
--add-data "templates;templates" ^
app.py