rem    --icon
rem    if Pillow is installed
rem    If an image file is entered that isn¡¯t in the platform format (ico on Windows, icns on Mac), PyInstaller tries to use Pillow to translate the icon into the correct format (if Pillow is installed).

python -m PyInstaller ^
  --windowed ^
  --clean ^
  --onedir ^
  --name JKui ^
  --contents-directory _jkui^
  --add-data  JKui\my_resource:my_resource ^
  --icon JKui\my_resource\icon_for_mainwindow.png ^
  JKui\__main__.py


