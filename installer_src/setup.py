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
        self.geometry("520x300")
        self._center()

        self.install_dir = tk.StringVar(value=DEFAULT_DIR)
        self.desktop_cb  = tk.BooleanVar(value=True)
        self.startmenu_cb = tk.BooleanVar(value=True)

        self._build()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - 520) // 2
        y = (sh - 300) // 2
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
        tk.Checkbutton(opt, text="Raccourci sur le Bureau",       variable=self.desktop_cb).pack(anchor="w")
        tk.Checkbutton(opt, text="Raccourci dans le menu Demarrer", variable=self.startmenu_cb).pack(anchor="w")

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

        # --- Extraction ---
        zip_path = resource("game.zip")
        self._set_status("Extraction des fichiers...", 0)
        try:
            with zipfile.ZipFile(zip_path) as zf:
                members = zf.namelist()
                n = len(members)
                for i, member in enumerate(members):
                    zf.extract(member, dest)
                    self._set_status(f"Extraction : {member[:55]}", (i + 1) / n * 85)
        except Exception as e:
            messagebox.showerror("Erreur d'extraction", str(e))
            self.btn_install.config(state="normal")
            return

        game_exe   = os.path.join(dest, "IonFall.exe")
        server_exe = os.path.join(dest, "serveur", "IonFall_Serveur.exe")

        # --- Raccourci Bureau ---
        if self.desktop_cb.get():
            self._set_status("Creation du raccourci Bureau...", 90)
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut(game_exe, os.path.join(desktop, f"{APP_NAME}.lnk"), dest)

        # --- Raccourci Menu Demarrer ---
        if self.startmenu_cb.get():
            self._set_status("Creation du raccourci Menu Demarrer...", 95)
            sm_dir = os.path.join(
                os.environ.get("APPDATA", ""),
                "Microsoft", "Windows", "Start Menu", "Programs", APP_NAME,
            )
            os.makedirs(sm_dir, exist_ok=True)
            shortcut(game_exe,   os.path.join(sm_dir, f"{APP_NAME}.lnk"),          dest)
            shortcut(server_exe, os.path.join(sm_dir, f"{APP_NAME} - Serveur.lnk"), dest)

        self._set_status("Installation terminee !", 100)
        if messagebox.askyesno(
            "Termine",
            f"{APP_NAME} a ete installe dans :\n{dest}\n\nLancer le jeu maintenant ?",
        ):
            subprocess.Popen([game_exe], cwd=dest)
        self.destroy()


if __name__ == "__main__":
    app = Installer()
    app.mainloop()
