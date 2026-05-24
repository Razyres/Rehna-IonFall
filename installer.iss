; ============================================================
;  IonFall — Script d'installation Inno Setup 6
;  Prerequis : avoir execute build_windows.bat pour generer dist\IonFall\
; ============================================================

#define AppName      "IonFall"
#define AppVersion   "1.0"
#define AppPublisher "IonFall Team"
#define AppExeName   "IonFall.exe"

[Setup]
AppId={{F3A1B2C4-8D7E-4F1A-9C3B-2E5D6F7A8B9C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=IonFall_Installer_v{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64
MinVersion=6.1sp1
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} {#AppVersion}

[Languages]
Name: "french";  MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Types]
Name: "full";   Description: "Installation complete"
Name: "custom"; Description: "Installation personnalisee"; Flags: iscustom

[Components]
Name: "game";    Description: "Jeu IonFall (requis)";       Types: full custom; Flags: fixed
Name: "website"; Description: "Site web du projet (hors ligne)"; Types: full

[Tasks]
Name: "desktopicon"; \
  Description: "{cm:CreateDesktopIcon}"; \
  GroupDescription: "{cm:AdditionalIcons}"; \
  Flags: unchecked

[Files]
; --- Jeu client ---
Source: "dist\IonFall\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs; \
  Components: game

; --- Site web hors ligne ---
Source: "site_web\*"; \
  DestDir: "{app}\site_web"; \
  Flags: ignoreversion recursesubdirs createallsubdirs; \
  Components: website

[Icons]
; Menu Demarrer
Name: "{group}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  WorkingDir: "{app}"

Name: "{group}\Site web IonFall"; \
  Filename: "{app}\site_web\Page_accueil.html"; \
  Components: website

Name: "{group}\Desinstaller {#AppName}"; \
  Filename: "{uninstallexe}"

; Bureau (optionnel, a cocher par l'utilisateur)
Name: "{autodesktop}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  WorkingDir: "{app}"; \
  Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Supprime tout le dossier d'installation apres desinstallation
Type: filesandordirs; Name: "{app}"
