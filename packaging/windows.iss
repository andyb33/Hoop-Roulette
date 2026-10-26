[Setup]
AppId=HoopRoulette.Desktop
AppName=Hoop Roulette
AppVersion=0.14.3
DefaultDirName={localappdata}\Programs\Hoop Roulette
DefaultGroupName=Hoop Roulette
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist\installer
OutputBaseFilename=HoopRoulette-v0.14.3-Setup
SetupIconFile=..\web\static\app-icon.ico
UninstallDisplayIcon={app}\HoopRoulette.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=no

[Files]
Source: "..\dist\HoopRoulette\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Hoop Roulette"; Filename: "{app}\HoopRoulette.exe"
Name: "{group}\Uninstall Hoop Roulette"; Filename: "{uninstallexe}"
