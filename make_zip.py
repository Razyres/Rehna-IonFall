"""
Cree installer_src/game.zip a partir des sorties PyInstaller.
A executer apres pyinstaller IonFall.spec et pyinstaller serveur.spec.
"""
import zipfile
import os
import sys


def add_dir(zf: zipfile.ZipFile, src_dir: str, arc_prefix: str) -> int:
    count = 0
    for root, _, files in os.walk(src_dir):
        for f in files:
            full = os.path.join(root, f)
            arcname = os.path.join(arc_prefix, os.path.relpath(full, src_dir))
            zf.write(full, arcname)
            count += 1
    return count


def main():
    client_dir = os.path.join("dist", "IonFall")
    server_dir = os.path.join("dist", "IonFall_Serveur")
    out_zip    = os.path.join("installer_src", "game.zip")

    for d in (client_dir, server_dir):
        if not os.path.isdir(d):
            print(f"[ERREUR] Dossier introuvable : {d}")
            print("         Lance build_windows.bat d'abord pour generer les executables.")
            sys.exit(1)

    os.makedirs("installer_src", exist_ok=True)

    print(f"Creation de {out_zip}...")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        n1 = add_dir(zf, client_dir, "")        # client a la racine
        n2 = add_dir(zf, server_dir, "serveur") # serveur dans sous-dossier
    print(f"  {n1} fichiers client + {n2} fichiers serveur -> {out_zip}")
    size_mb = os.path.getsize(out_zip) / 1024 / 1024
    print(f"  Taille : {size_mb:.1f} Mo")


if __name__ == "__main__":
    main()
