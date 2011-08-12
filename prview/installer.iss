; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=PrView-0.9.1
AppVerName=PrView 0.9.1
AppPublisher=University of Tennessee
AppPublisherURL=http://danse.chem.utk.edu/
AppSupportURL=http://danse.chem.utk.edu/
AppUpdatesURL=http://danse.chem.utk.edu/
DefaultDirName={pf}\PrView-0.9.1
DefaultGroupName=DANSE\PrView-0.9.1
DisableProgramGroupPage=yes
LicenseFile=license.txt
OutputBaseFilename=setupPrView
SetupIconFile=images\ball.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=none

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\prView.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\PrView"; Filename: "{app}\prView.exe"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,PrView}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\PrView"; Filename: "{app}\prView.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\prView.exe"; Description: "{cm:LaunchProgram,PrView}"; Flags: nowait postinstall skipifsilent

