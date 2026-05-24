"""IonFall - Desinstalleur"""
import os
import sys
import shutil
import subprocess
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


def main() -> None:
    root = tk.Tk()
    root.withdraw()

    try:
        icon = tk.PhotoImage(file=resource("IonFall_48x48.png"))
        root.iconphoto(True, icon)
        root._icon = icon
    except Exception:
        pass

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

    # Suppression du dossier via cmd.exe avec delai (plus fiable que PowerShell)
    # del /f /q marque l'exe verrouille pour suppression a la fermeture du handle
    # rd /s /q supprime le reste du dossier
    uninstall_exe = os.path.join(install_dir, "IonFall_Uninstall.exe")
    cmd_str = (
        f"timeout /t 3 /nobreak >nul"
        f" & del /f /q \"{uninstall_exe}\""
        f" & rd /s /q \"{install_dir}\""
    )
    subprocess.Popen(
        ["cmd", "/c", cmd_str],
        creationflags=0x00000208,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    )

    messagebox.showinfo(f"Desinstaller {APP_NAME}", f"{APP_NAME} a ete desinstalle avec succes.")
    root.destroy()


if __name__ == "__main__":
    main()
