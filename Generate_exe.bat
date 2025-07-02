@echo off
REM Create standalone Windows app using PyInstaller
 
REM Optional: Clean previous build artifacts
rmdir /s /q build
rmdir /s /q dist
del /q main.spec
 
REM Build the app
pyinstaller --name=VehicleSimulatorTool --onefile --noconsole --add-data "UI/mainWindow2.ui;UI" --add-data "UI/connectionDialogBox.ui;UI" Main.py --clean
 
echo.
echo Build completed. The EXE is located in the 'dist' folder.
pause