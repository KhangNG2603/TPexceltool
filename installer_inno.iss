; Script Inno Setup 6 cho Thiên Phúc — Hóa đơn bán hàng & Quản lý xe
#define MyAppName "Thiên Phúc — Hóa đơn bán hàng"
#define MyAppShortName "TPexcel"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Công ty TNHH Thiết Bị Điện Thiên Phúc"
#define MyAppURL "https://github.com/KhangNG2603/TPexceltool"
#define MyAppExeName "TPexcelApp.exe"

[Setup]
AppId={{5E583344-9BF2-46A2-9EB5-CF2FE74900A1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\TPexcel
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=TPexcel_InnoSetup
SetupIconFile=assets\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng trên Màn hình nền (Desktop)"; GroupDescription: "Lối tắt bổ sung:"
Name: "startmenuicon"; Description: "Tạo biểu tượng trong Menu Start"; GroupDescription: "Lối tắt bổ sung:"

[Files]
Source: "dist\TPexcelApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\app_icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "assets\logo-thien-phuc.png"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Thiên Phúc\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Khởi chạy {#MyAppName} ngay bây giờ"; Flags: nowait postinstall skipifsilent
