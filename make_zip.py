"""
Cree installer_src/game.zip a partir de la sortie PyInstaller.
A executer apres pyinstaller IonFall.spec et uninstall.spec.
"""
import zipfile
import os
import sys


def add_dir(zf: zipfile.ZipFile, src_dir: str, arc_prefix: str) -> int:
    count = 0
    for root, _, files in os.walk(src_dir):
        for f in files:
            if ":" in f:  # Ignore les ADS Windows (Zone.Identifier, etc.)
                continue
            full = os.path.join(root, f)
            arcname = os.path.join(arc_prefix, os.path.relpath(full, src_dir))
            zf.write(full, arcname)
            count += 1
    return count


def main():
    client_dir    = os.path.join("dist", "IonFall")
    uninstall_exe = os.path.join("dist", "IonFall_Uninstall.exe")
    site_web_dir  = "site_web"
    out_zip       = os.path.join("installer_src", "game.zip")

    if not os.path.isdir(client_dir):
        print(f"[ERREUR] Dossier introuvable : {client_dir}")
        print("         Lance build_windows.bat d'abord pour generer les executables.")
        sys.exit(1)

    os.makedirs("installer_src", exist_ok=True)

    print(f"Creation de {out_zip}...")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        n = add_dir(zf, client_dir, "")
        print(f"  {n} fichiers jeu")

        if os.path.isfile(uninstall_exe):
            zf.write(uninstall_exe, "IonFall_Uninstall.exe")
            print(f"  + IonFall_Uninstall.exe")
        else:
            print(f"  [AVERT] {uninstall_exe} introuvable — desinstalleur non inclus")

        if os.path.isdir(site_web_dir):
            m = add_dir(zf, site_web_dir, "site_web")
            print(f"  {m} fichiers site web")
        else:
            print(f"  [AVERT] Dossier site_web/ introuvable — site web non inclus")

    size_mb = os.path.getsize(out_zip) / 1024 / 1024
    print(f"  Taille totale : {size_mb:.1f} Mo")


if __name__ == "__main__":
    main()
