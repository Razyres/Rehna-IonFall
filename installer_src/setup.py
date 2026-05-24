"""
IonFall - Installeur autonome
Genere par PyInstaller, embarque game.zip, aucune dependance externe requise.
"""
import os
import sys
import subprocess
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "IonFall"
APP_VERSION = "1.0"
APP_PUBLISHER = "IonFall Team"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\IonFall"
DEFAULT_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), APP_NAME)


def resource(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, rel)


def shortcut(target: str, lnk_path: str, work_dir: str) -> None:
    ps = (
        f"$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{lnk_path}'); "
        f"$s.TargetPath = '{target}'; "
        f"$s.WorkingDirectory = '{work_dir}'; "
        f"$s.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)


class Installer(tk.Tk):
    PAD = 20

    def __init__(self):
        super().__init__()
        self.title(f"Installation de {APP_NAME}")
        self.resizable(False, False)
        self.geometry("520x340")
        self._center()

        self.install_dir   = tk.StringVar(value=DEFAULT_DIR)
        self.desktop_cb    = tk.BooleanVar(value=True)
        self.startmenu_cb  = tk.BooleanVar(value=True)
        self.site_web_cb   = tk.BooleanVar(value=True)

        # Icone avant tout affichage pour qu'elle apparaisse des l'ouverture
        try:
            self._icon = tk.PhotoImage(file=resource("IonFall_48x48.png"))
            self.iconphoto(True, self._icon)
        except Exception:
            pass

        self._build()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 520) // 2
        y = (sh - 340) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self):
        tk.Label(self, text=f"Installation de {APP_NAME}", font=("Segoe UI", 15, "bold")).pack(pady=(18, 8))

        # --- Dossier destination ---
        frm = tk.LabelFrame(self, text="Dossier d'installation", padx=self.PAD, pady=8)
        frm.pack(fill="x", padx=self.PAD, pady=4)
        row = tk.Frame(frm)
        row.pack(fill="x")
        tk.Entry(row, textvariable=self.install_dir, width=48).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="...", width=3, command=self._browse).pack(side="left", padx=(6, 0))

        # --- Options ---
        opt = tk.Frame(self)
        opt.pack(fill="x", padx=self.PAD, pady=4)
        tk.Checkbutton(opt, text="Raccourci sur le Bureau",           variable=self.desktop_cb).pack(anchor="w")
        tk.Checkbutton(opt, text="Raccourci dans le menu Demarrer",   variable=self.startmenu_cb).pack(anchor="w")
        tk.Checkbutton(opt, text="Installer le site web du projet",   variable=self.site_web_cb).pack(anchor="w")

        # --- Barre de progression ---
        self.progress = ttk.Progressbar(self, length=480, mode="determinate")
        self.progress.pack(padx=self.PAD, pady=(8, 2))
        self.status = tk.Label(self, text="", fg="gray")
        self.status.pack()

        # --- Boutons ---
        btn = tk.Frame(self)
        btn.pack(pady=(6, 12))
        self.btn_install = tk.Button(btn, text="Installer", width=14, command=self._install)
        self.btn_install.pack(side="left", padx=8)
        tk.Button(btn, text="Annuler", width=14, command=self.destroy).pack(side="left", padx=8)

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.install_dir.get())
        if d:
            self.install_dir.set(d)

    def _set_status(self, text: str, pct: float):
        self.progress["value"] = pct
        self.status.config(text=text)
        self.update()

    def _write_registry(self, dest: str, game_exe: str, uninstall_exe: str) -> None:
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
                winreg.SetValueEx(key, "DisplayName",     0, winreg.REG_SZ,    APP_NAME)
                winreg.SetValueEx(key, "DisplayVersion",  0, winreg.REG_SZ,    APP_VERSION)
                winreg.SetValueEx(key, "Publisher",       0, winreg.REG_SZ,    APP_PUBLISHER)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ,    dest)
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,    uninstall_exe)
                winreg.SetValueEx(key, "DisplayIcon",     0, winreg.REG_SZ,    game_exe)
                winreg.SetValueEx(key, "NoModify",        0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair",        0, winreg.REG_DWORD, 1)
        except Exception:
            pass

    def _install(self):
        self.btn_install.config(state="disabled")
        dest = self.install_dir.get().strip()
        if not dest:
            messagebox.showerror("Erreur", "Choisis un dossier d'installation.")
            self.btn_install.config(state="normal")
            return

        try:
            os.makedirs(dest, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Erreur", f"Impossible de creer le dossier :\n{e}")
            self.btn_install.config(state="normal")
            return

        install_site_web = self.site_web_cb.get()

        # --- Extraction (filtre site_web si non demande) ---
        zip_path = resource("game.zip")
        self._set_status("Extraction des fichiers...", 0)
        try:
            with zipfile.ZipFile(zip_path) as zf:
                members = zf.namelist()
                to_extract = [
                    m for m in members
                    if install_site_web or not m.startswith("site_web/")
                ]
                n = len(to_extract)
                extracted = []
                for i, member in enumerate(to_extract):
                    zf.extract(member, dest)
                    extracted.append(member)
                    self._set_status(f"Extraction : {member[:55]}", (i + 1) / n * 75)
        except Exception as e:
            messagebox.showerror("Erreur d'extraction", str(e))
            self.btn_install.config(state="normal")
            return

        # Manifeste pour le desinstalleur (liste uniquement les fichiers, pas les dossiers)
        manifest_path = os.path.join(dest, "ionfall_files.txt")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            for m in extracted:
                if not m.endswith("/"):
                    mf.write(m + "\n")
            mf.write("IonFall_Uninstall.exe\n")
            mf.write("ionfall_files.txt\n")

        game_exe      = os.path.join(dest, "IonFall.exe")
        uninstall_exe = os.path.join(dest, "IonFall_Uninstall.exe")

        # --- Enregistrement Windows (Parametres > Applications) ---
        self._set_status("Enregistrement dans Windows...", 80)
        self._write_registry(dest, game_exe, uninstall_exe)

        # --- Raccourci Bureau ---
        if self.desktop_cb.get():
            self._set_status("Creation du raccourci Bureau...", 85)
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut(game_exe, os.path.join(desktop, f"{APP_NAME}.lnk"), dest)

        # --- Raccourcis Menu Demarrer ---
        if self.startmenu_cb.get():
            self._set_status("Creation du raccourci Menu Demarrer...", 90)
            sm_dir = os.path.join(
                os.environ.get("APPDATA", ""),
                "Microsoft", "Windows", "Start Menu", "Programs", APP_NAME,
            )
            os.makedirs(sm_dir, exist_ok=True)
            shortcut(game_exe,      os.path.join(sm_dir, f"{APP_NAME}.lnk"),              dest)
            shortcut(uninstall_exe, os.path.join(sm_dir, f"Desinstaller {APP_NAME}.lnk"), dest)
            if install_site_web:
                site_index = os.path.join(dest, "site_web", "Page_accueil.html")
                shortcut(site_index, os.path.join(sm_dir, f"{APP_NAME} - Site web.lnk"),  dest)

        self._set_status("Installation terminee !", 100)
        if messagebox.askyesno(
            "Termine",
            f"{APP_NAME} a ete installe dans :\n{dest}\n\nLancer le jeu maintenant ?",
        ):
            subprocess.Popen([game_exe], cwd=dest)
        if messagebox.askyesno(
            "Jouer en ligne",
            "IonFall est un jeu multijoueur en reseau local.\n\n"
            "Pour jouer en ligne avec un ami, Hamachi (VPN gratuit) est recommande :\n"
            "il simule un reseau local entre deux ordinateurs distants.\n\n"
            "Ouvrir la page de telechargement de Hamachi ?",
        ):
            import webbrowser
            webbrowser.open("https://vpn.net/")
        self.destroy()


if __name__ == "__main__":
    app = Installer()
    app.mainloop()
