[Setup]
AppName=Sampsul Autoclicker
AppVersion=1.0
DefaultDirName={pf}\SampsulAutoclicker
OutputDir=Output
OutputBaseFilename=Autoclicker-Setup
SetupIconFile=installer-build\icon.ico
Compression=lzma
SolidCompression=yes
DisableDirPage=yes
DisableProgramGroupPage=no

[Files]
Source: "installer-build\autoclicker.exe"; DestDir: "{app}"
Source: "installer-build\icon.ico"; DestDir: "{app}"

[Icons]
Name: "{group}\Autoclicker"; Filename: "{app}\autoclicker.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\Autoclicker"; Filename: "{app}\autoclicker.exe"; IconFilename: "{app}\icon.ico"
