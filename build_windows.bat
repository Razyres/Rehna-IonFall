@echo off
echo === IonFall - Build Windows ===
echo.

echo Installation des dependances...
python -m pip install "pygame>=2.6.1" PyTMX==3.32 pyinstaller
echo.

echo Build du jeu (IonFall.exe)...
python -m PyInstaller IonFall.spec --noconfirm
if errorlevel 1 (
    echo ERREUR : le build du jeu a echoue.
    pause & exit /b 1
)

echo Build du desinstalleur (IonFall_Uninstall.exe)...
python -m PyInstaller uninstall.spec --noconfirm
if errorlevel 1 (
    echo ERREUR : le build du desinstalleur a echoue.
    pause & exit /b 1
)

echo Compression des fichiers dans game.zip...
python make_zip.py
if errorlevel 1 (
    echo ERREUR : la creation du zip a echoue.
    pause & exit /b 1
)

echo Build de l installeur (IonFall_Setup.exe)...
python -m PyInstaller setup.spec --noconfirm
if errorlevel 1 (
    echo ERREUR : le build de l installeur a echoue.
    pause & exit /b 1
)

echo.
echo === Build complet ! ===
echo Installeur pret : dist\IonFall_Setup.exe
echo.
echo Distribue uniquement ce fichier. Il contient le jeu et le site web.
echo.
pause
