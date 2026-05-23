; ============================================================
;  IonFall — Script d'installation Inno Setup 6
;  Prerequis : avoir execute build_windows.bat au prealable
;              pour generer dist\IonFall\ et dist\IonFall_Serveur\
; ============================================================

#define AppName      "IonFall"
#define AppVersion   "1.0"
#define AppPublisher "IonFall Team"
#define AppExeName   "IonFall.exe"
#define ServerExe    "IonFall_Serveur.exe"

[Setup]
AppId={{F3A1B2C4-8D7E-4F1A-9C3B-2E5D6F7A8B9C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; Decommenter la ligne suivante si tu ajoutes une icone .ico au projet :
; SetupIconFile=ionfall.ico
; UninstallDisplayIcon={app}\{#AppExeName}
OutputDir=installer_output
OutputBaseFilename=IonFall_Installer_v{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64
MinVersion=6.1sp1
; Affiche la licence si tu en as une :
; LicenseFile=LICENSE.txt

[Languages]
Name: "french";  MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; \
  Description: "{cm:CreateDesktopIcon}"; \
  GroupDescription: "{cm:AdditionalIcons}"; \
  Flags: unchecked

[Files]
; --- Client (tous les fichiers PyInstaller) ---
Source: "dist\IonFall\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

; --- Serveur dedie ---
Source: "dist\IonFall_Serveur\*"; \
  DestDir: "{app}\serveur"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Demarrer
Name: "{group}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  WorkingDir: "{app}"

Name: "{group}\{#AppName} - Serveur dedie"; \
  Filename: "{app}\serveur\{#ServerExe}"; \
  WorkingDir: "{app}\serveur"

Name: "{group}\Desinstaller {#AppName}"; \
  Filename: "{uninstallexe}"

; Bureau (optionnel, coche par l'utilisateur)
Name: "{autodesktop}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  WorkingDir: "{app}"; \
  Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Supprime les fichiers crees par le jeu au runtime s'il en reste
Type: filesandordirs; Name: "{app}"
