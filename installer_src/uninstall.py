"""IonFall - Desinstalleur"""
import os
import sys
import shutil
import subprocess
import tempfile
import tkinter as tk
from tkinter import messagebox

APP_NAME = "IonFall"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\IonFall"


def resource(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def _install_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _remove_registry() -> None:
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    except Exception:
        pass


def _remove_shortcuts() -> None:
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    sm_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        "Microsoft", "Windows", "Start Menu", "Programs", APP_NAME,
    )
    for path in (os.path.join(desktop, f"{APP_NAME}.lnk"), sm_dir):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


def _schedule_deletion(install_dir: str) -> None:
    # On ecrit un .bat dans %TEMP% pour supprimer le dossier apres la fermeture de l'exe.
    # CREATE_NO_WINDOW est necessaire pour cmd.exe — DETACHED_PROCESS est incompatible.
    bat = os.path.join(tempfile.gettempdir(), "ionfall_cleanup.bat")
    with open(bat, "w") as f:
        f.write("@echo off\r\n")
        f.write("timeout /t 3 /nobreak >nul\r\n")
        f.write(f"rd /s /q \"{install_dir}\"\r\n")
        f.write("del /f /q \"%~f0\"\r\n")  # auto-suppression du .bat
    subprocess.Popen(
        ["cmd", "/c", bat],
        creationflags=0x08000200,  # CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
    )


def main() -> None:
    root = tk.Tk()

    # Icone AVANT withdraw() pour qu'elle soit heritee par les fenetres de dialogue
    try:
        icon = tk.PhotoImage(file=resource("IonFall_48x48.png"))
        root.iconphoto(True, icon)
        root._icon = icon
    except Exception:
        pass

    root.withdraw()

    if not messagebox.askyesno(
        f"Desinstaller {APP_NAME}",
        f"Voulez-vous vraiment desinstaller {APP_NAME} ?\n\n"
        f"Tous les fichiers du dossier d'installation seront supprimes.",
    ):
        root.destroy()
        return

    install_dir = _install_dir()
    _remove_registry()
    _remove_shortcuts()
    _schedule_deletion(install_dir)

    messagebox.showinfo(f"Desinstaller {APP_NAME}", f"{APP_NAME} a ete desinstalle avec succes.")
    root.destroy()


if __name__ == "__main__":
    main()
