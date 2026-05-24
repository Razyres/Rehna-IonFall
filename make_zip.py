"""
Cree installer_src/game.zip a partir de la sortie PyInstaller.
A executer apres pyinstaller IonFall.spec.
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
    out_zip    = os.path.join("installer_src", "game.zip")

    if not os.path.isdir(client_dir):
        print(f"[ERREUR] Dossier introuvable : {client_dir}")
        print("         Lance build_windows.bat d'abord pour generer les executables.")
        sys.exit(1)

    os.makedirs("installer_src", exist_ok=True)

    print(f"Creation de {out_zip}...")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        n = add_dir(zf, client_dir, "")
    print(f"  {n} fichiers client -> {out_zip}")
    size_mb = os.path.getsize(out_zip) / 1024 / 1024
    print(f"  Taille : {size_mb:.1f} Mo")


if __name__ == "__main__":
    main()
