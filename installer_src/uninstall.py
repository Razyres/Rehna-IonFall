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
MANIFEST = "ionfall_files.txt"


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


def _delete_installed_files(install_dir: str) -> None:
    """Supprime uniquement les fichiers listes dans le manifeste d'installation."""
    manifest_path = os.path.join(install_dir, MANIFEST)

    if not os.path.exists(manifest_path):
        # Pas de manifeste : installation ancienne, on ne touche a rien de plus
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        entries = [line.strip() for line in f if line.strip()]

    # Nom de l'exe en cours (a ne pas supprimer maintenant — gere par le .bat)
    self_name = os.path.basename(sys.executable) if getattr(sys, "frozen", False) else ""

    dirs_to_try = set()
    for rel in entries:
        if rel in (self_name, MANIFEST):
            continue  # sera supprime par le .bat apres fermeture
        full = os.path.join(install_dir, rel.replace("/", os.sep))
        if os.path.isfile(full):
            try:
                os.remove(full)
                dirs_to_try.add(os.path.dirname(full))
            except OSError:
                pass

    # Supprime les sous-dossiers devenus vides (du plus profond vers le plus haut)
    for d in sorted(dirs_to_try, key=lambda x: x.count(os.sep), reverse=True):
        if d != install_dir and d.startswith(install_dir):
            try:
                os.rmdir(d)
            except OSError:
                pass


def _schedule_self_deletion(install_dir: str) -> None:
    # Supprime le .exe desinstalleur et le manifeste 3s apres fermeture,
    # puis tente de supprimer le dossier d'installation s'il est vide.
    # CREATE_NO_WINDOW requis pour cmd.exe (DETACHED_PROCESS incompatible).
    uninstall_exe = os.path.join(install_dir, "IonFall_Uninstall.exe")
    manifest_path = os.path.join(install_dir, MANIFEST)
    bat = os.path.join(tempfile.gettempdir(), "ionfall_cleanup.bat")
    with open(bat, "w") as f:
        f.write("@echo off\r\n")
        f.write("timeout /t 3 /nobreak >nul\r\n")
        f.write(f"del /f /q \"{uninstall_exe}\"\r\n")
        f.write(f"del /f /q \"{manifest_path}\"\r\n")
        # rd sans /s supprime seulement si le dossier est vide
        f.write(f"rd \"{install_dir}\"\r\n")
        f.write("del /f /q \"%~f0\"\r\n")
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
        f"Les fichiers du jeu seront supprimes.",
    ):
        root.destroy()
        return

    install_dir = _install_dir()
    _remove_registry()
    _remove_shortcuts()
    _delete_installed_files(install_dir)
    _schedule_self_deletion(install_dir)

    messagebox.showinfo(f"Desinstaller {APP_NAME}", f"{APP_NAME} a ete desinstalle avec succes.")
    root.destroy()


if __name__ == "__main__":
    main()
