; Don't Touch - Inno Setup Installer Script
; Supports: Windows 10/11 (64-bit)

#define MyAppName "Don't Touch"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Si Hyeong Lee"
#define MyAppURL "https://github.com/writingdeveloper/dont-touch"
#define MyAppExeName "DontTouch.exe"

[Setup]
; Application info
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=DontTouch_Setup_{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Require 64-bit Windows
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Minimum Windows version (Windows 10)
MinVersion=10.0

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "chinesesimplified"; MessagesFile: "assets\ChineseSimplified.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[CustomMessages]
; English
english.LaunchAfterInstall=Launch {#MyAppName} after installation
english.CreateDesktopIcon=Create a &desktop shortcut
english.AddToStartup=Start {#MyAppName} when Windows starts
english.AppDescription=Face touch detection application to help with Trichotillomania

; Korean
korean.LaunchAfterInstall=설치 후 {#MyAppName} 실행
korean.CreateDesktopIcon=바탕화면에 바로가기 만들기(&D)
korean.AddToStartup=Windows 시작 시 {#MyAppName} 자동 실행
korean.AppDescription=발모벽 개선을 위한 얼굴 터치 감지 애플리케이션

; Japanese
japanese.LaunchAfterInstall=インストール後に {#MyAppName} を起動
japanese.CreateDesktopIcon=デスクトップにショートカットを作成(&D)
japanese.AddToStartup=Windows起動時に {#MyAppName} を自動起動
japanese.AppDescription=抜毛症改善のための顔タッチ検出アプリケーション

; Chinese Simplified
chinesesimplified.LaunchAfterInstall=安装后启动 {#MyAppName}
chinesesimplified.CreateDesktopIcon=创建桌面快捷方式(&D)
chinesesimplified.AddToStartup=Windows启动时自动运行 {#MyAppName}
chinesesimplified.AppDescription=帮助改善拔毛癖的面部触摸检测应用程序

; Spanish
spanish.LaunchAfterInstall=Iniciar {#MyAppName} después de la instalación
spanish.CreateDesktopIcon=Crear acceso directo en el escritorio(&D)
spanish.AddToStartup=Iniciar {#MyAppName} con Windows
spanish.AppDescription=Aplicación de detección de toque facial para ayudar con la Tricotilomanía

; Russian
russian.LaunchAfterInstall=Запустить {#MyAppName} после установки
russian.CreateDesktopIcon=Создать ярлык на рабочем столе(&D)
russian.AddToStartup=Запускать {#MyAppName} при старте Windows
russian.AppDescription=Приложение для обнаружения касаний лица для помощи при трихотилломании

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "{cm:AddToStartup}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main application and all files from dist folder
Source: "dist\DontTouch\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Locale files
Source: "locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{cm:AppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{cm:AppDescription}"

[Registry]
; Add to startup (if task selected)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startup

[Run]
; Launch after install (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchAfterInstall}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data folder on uninstall (optional - commented out to preserve settings)
; Type: filesandordirs; Name: "{userappdata}\.dont-touch"

[Code]
// Check if app is running before install/uninstall
function IsAppRunning(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('tasklist', '/FI "IMAGENAME eq {#MyAppExeName}" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    // If tasklist finds the process, it returns specific output
    Result := ResultCode = 0;
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Check if already installed and running
  if IsAppRunning() then
  begin
    MsgBox('Don''t Touch is currently running. Please close it before installing.', mbError, MB_OK);
    Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if IsAppRunning() then
  begin
    MsgBox('Don''t Touch is currently running. Please close it before uninstalling.', mbError, MB_OK);
    Result := False;
  end;
end;

// Uninstall previous version before installing new one
procedure CurStepChanged(CurStep: TSetupStep);
var
  UninstallKey: String;
  UninstallString: String;
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
  begin
    UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1';
    if RegQueryStringValue(HKLM, UninstallKey, 'UninstallString', UninstallString) or
       RegQueryStringValue(HKCU, UninstallKey, 'UninstallString', UninstallString) then
    begin
      // Previous version found, uninstall silently
      UninstallString := RemoveQuotes(UninstallString);
      Exec(UninstallString, '/VERYSILENT /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
