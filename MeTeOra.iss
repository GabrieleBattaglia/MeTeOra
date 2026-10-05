; MeTeOra, l'installatore con Inno Setup 6 (1.97.0).
; Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5.5, UltraCode).
; 05/10/2026: nasce con la prima release, scelto da Gabriele.
;
; Si compila con python setup_maker.py, dopo la compilazione di PyInstaller e
; zip_maker.py: lo script passa la versione di version.py.
; Le scelte di Gabriele del 5 ottobre 2026: l'installatore affianca lo zip
; dell'aggiornamento automatico; si installa per utente, senza
; amministratore, perche' MeTeOra scrive i suoi dati accanto all'eseguibile e
; l'aggiornamento automatico sostituisce i file nella sua cartella; alla
; disinstallazione chiede se cancellare anche i dati.

#ifndef Versione
  #error Manca la versione: si compila con python setup_maker.py
#endif

[Setup]
; L'identita' dell'installazione: non cambia mai, e la usa anche
; installazione.py per tenere giusta la versione in App installate.
AppId={{64985198-5673-4D67-A490-35A62886C1F2}
AppName=MeTeOra
AppVersion={#Versione}
AppVerName=MeTeOra {#Versione}
AppPublisher=Gabriele Battaglia (IZ4APU)
AppPublisherURL=https://github.com/GabrieleBattaglia/MeTeOra
AppSupportURL=https://github.com/GabrieleBattaglia/MeTeOra/issues
AppUpdatesURL=https://github.com/GabrieleBattaglia/MeTeOra/releases
VersionInfoVersion={#Versione}
; Per utente: con PrivilegesRequired=lowest {autopf} e' la cartella
; Programs di AppData\Local.
PrivilegesRequired=lowest
DefaultDirName={autopf}\MeTeOra
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=.
OutputBaseFilename=MeTeOra-Setup-{#Versione}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=no
UninstallDisplayName=MeTeOra
UninstallDisplayIcon={app}\MeTeOra.exe
; MeTeOra aperto tiene questo mutex (istanza.py): installazione e
; disinstallazione chiedono di chiuderlo.
AppMutex=MeTeOra
CloseApplications=yes
RestartApplications=no
; Disinstallando si tolgono le associazioni dei formati: Esplora risorse
; deve rileggerle.
ChangesAssociations=yes

[Languages]
Name: "italiano"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Il pacchetto a cartella di PyInstaller, senza i dati che una prova avesse
; lasciato in dist, come fa zip_maker.py.
Source: "dist\MeTeOra\*"; DestDir: "{app}"; Excludes: "MeTeOra - *,MeTeOra-V*.txt,*.log,\copie\*,\fluidsynth\*,\banchi\*"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\MeTeOra"; Filename: "{app}\MeTeOra.exe"
Name: "{autodesktop}\MeTeOra"; Filename: "{app}\MeTeOra.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MeTeOra.exe"; Description: "{cm:LaunchProgram,MeTeOra}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; L'aggiornamento automatico puo' portare in _internal file che
; l'installatore non conosce: la cartella del programma si toglie intera.
; I dati stanno fuori da _internal, accanto all'eseguibile.
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\_internal_vecchio"
Type: filesandordirs; Name: "{app}\licenze"

[Code]
procedure CancellaIFile(const Cartella, Modello: String);
var
  Trovato: TFindRec;
begin
  if FindFirst(Cartella + '\' + Modello, Trovato) then
  begin
    try
      repeat
        if (Trovato.Attributes and FILE_ATTRIBUTE_DIRECTORY) = 0 then
          DeleteFile(Cartella + '\' + Trovato.Name);
      until not FindNext(Trovato);
    finally
      FindClose(Trovato);
    end;
  end;
end;

// I dati di MeTeOra: playlist, impostazioni, marker, posizioni, schedario,
// registri, console salvate, copie, e FluidSynth e i banchi scaricati.
procedure CancellaIDati(const Cartella: String);
begin
  CancellaIFile(Cartella, 'MeTeOra - *');
  CancellaIFile(Cartella, 'MeTeOra-V*.txt');
  DelTree(Cartella + '\copie', True, True, True);
  DelTree(Cartella + '\fluidsynth', True, True, True);
  DelTree(Cartella + '\banchi', True, True, True);
end;

// Le associazioni dei formati che MeTeOra scrive con la voce delle
// impostazioni (associazioni.py, registra), tolte come fa Togli, ma solo se
// sono di questa installazione: quelle di una copia portatile restano.
procedure TogliLeAssociazioni;
var
  Comando, Tipo: String;
  Estensioni: TArrayOfString;
  I: Integer;
begin
  if not RegQueryStringValue(HKCU, 'Software\Classes\Applications\MeTeOra.exe\shell\open\command', '', Comando) then
    exit;
  if Pos(Lowercase(ExpandConstant('{app}\MeTeOra.exe')), Lowercase(Comando)) = 0 then
    exit;
  if RegGetValueNames(HKCU, 'Software\MeTeOra\Capabilities\FileAssociations', Estensioni) then
    for I := 0 to GetArrayLength(Estensioni) - 1 do
      if RegQueryStringValue(HKCU, 'Software\MeTeOra\Capabilities\FileAssociations', Estensioni[I], Tipo) then
        RegDeleteValue(HKCU, 'Software\Classes\' + Estensioni[I] + '\OpenWithProgids', Tipo);
  RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\Applications\MeTeOra.exe');
  RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\MeTeOra.Audio');
  RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\MeTeOra.Video');
  RegDeleteKeyIncludingSubkeys(HKCU, 'Software\MeTeOra');
  RegDeleteValue(HKCU, 'Software\RegisteredApplications', 'MeTeOra');
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    TogliLeAssociazioni;
  if (CurUninstallStep = usPostUninstall) and not UninstallSilent then
  begin
    if MsgBox('Cancello anche i dati di MeTeOra? Playlist, Preferiti, impostazioni, marker e le loro copie. ' +
        'Con No restano nella cartella, e reinstallando MeTeOra li ritrovi.', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      CancellaIDati(ExpandConstant('{app}'));
    // La cartella si toglie solo se e' rimasta vuota.
    RemoveDir(ExpandConstant('{app}'));
  end;
end;
