@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Building Alhamd Traders Executable...
pyinstaller --noconfirm --onedir --windowed --icon "assets/icon.ico" --name "Alhamd Traders" --add-data "app/styles.qss;app/" --add-data "assets/*;assets/" "app/main.py"

echo Build complete! You can find the executable in the "dist/Alhamd Traders/" folder.
pause
