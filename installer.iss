; NexPro PDF Installer Script for Inno Setup
; Download Inno Setup from: https://jrsoftware.org/isinfo.php
; Version should match src/version.py

#define MyAppName "NexPro PDF"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "CTPL"
#define MyAppURL "https://www.ctpl.com"
#define MyAppExeName "NexProPDF.exe"
#define MyAppAssocName "PDF Document"
#define MyAppAssocExt ".pdf"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Application information
AppId={{8F6B3E7A-5D4C-4B2A-9E1F-0A8B7C6D5E4F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/support
AppUpdatesURL={#MyAppURL}/updates
AppContact=support@ctpl.com
AppCopyright=Copyright (C) 2026 CTPL. All rights reserved.
VersionInfoVersion=1.0.0.0
VersionInfoCompany=CTPL
VersionInfoDescription=NexPro PDF - Professional PDF Editor
VersionInfoCopyright=Copyright (C) 2026 CTPL
VersionInfoProductName=NexPro PDF
VersionInfoProductVersion=1.0.0.0
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output settings
OutputDir=installer_output
OutputBaseFilename=NexProPDF_Setup
SetupIconFile=resources\nexpro_pdf.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
; Upgrade behavior
CloseApplications=yes
CloseApplicationsFilter=NexProPDF.exe
RestartApplications=yes
UsePreviousAppDir=yes
UsePreviousGroup=yes
; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main application files from PyInstaller output
Source: "dist\NexProPDF\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; File association for PDF files (optional - commented out by default)
; Uncomment if you want NexPro PDF to be associated with .pdf files
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
; Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".pdf"; ValueData: ""

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  InstalledVersion: String;
begin
  Result := True;
  { Check if NexPro PDF is already installed }
  if RegQueryStringValue(HKLM,
    'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{8F6B3E7A-5D4C-4B2A-9E1F-0A8B7C6D5E4F}_is1',
    'DisplayVersion', InstalledVersion) or
    RegQueryStringValue(HKCU,
    'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{8F6B3E7A-5D4C-4B2A-9E1F-0A8B7C6D5E4F}_is1',
    'DisplayVersion', InstalledVersion) then
  begin
    if InstalledVersion = '{#MyAppVersion}' then
    begin
      if MsgBox('{#MyAppName} v' + InstalledVersion + ' is already installed.' + #13#10 + #13#10 +
                'Do you want to repair/reinstall it?',
                mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end
    else
    begin
      if MsgBox('{#MyAppName} v' + InstalledVersion + ' is currently installed.' + #13#10 + #13#10 +
                'Do you want to upgrade to v{#MyAppVersion}?' + #13#10 +
                'Your settings will be preserved.',
                mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end;
  end;
end;
