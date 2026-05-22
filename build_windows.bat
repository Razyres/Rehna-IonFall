@echo off
echo === IonFall - Build Windows ===
echo.

echo Installation des dependances...
pip install pygame==2.6.1 PyTMX==3.32 pyinstaller
echo.

echo Build du client (IonFall.exe)...
pyinstaller IonFall.spec --noconfirm
echo.

echo Build du serveur (IonFall_Serveur.exe)...
pyinstaller serveur.spec --noconfirm
echo.

echo === Build termine ! ===
echo Client  : dist\IonFall\IonFall.exe
echo Serveur : dist\IonFall_Serveur\IonFall_Serveur.exe
echo.
echo Pour distribuer le jeu, zippe le dossier dist\IonFall\
echo Le serveur peut tourner sur n'importe quel PC (ou un des deux joueurs).
pause
