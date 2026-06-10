# AuRaCADE 3BTLC

Launcher Pygame che raccoglie i progetti finali della 3BTLC in un cabinet unico con avvio uniforme, schede riassuntive e credits.

## Struttura

- `auracade_3btlc.py`: launcher principale.
- `auracade_config.py`: configurazione, tema, percorsi e credits statici.
- `auracade_audio.py`: generazione e gestione delle due tracce 8-bit del launcher.
- `auracade_game_runner.py`: wrapper che lancia i giochi in finestra normale e aggiunge un'uscita uniforme con `Esc`.
- `auracade_games.json`: catalogo dei giochi letto dal launcher.
- `auracade_assets/covers/`: copertine mostrate nel launcher.
- `games/`: cartelle degli studenti con giochi, asset e relazioni PDF.

## Cosa cambia rispetto alla versione precedente

- Nessun gioco viene lanciato in fullscreen forzato dal launcher.
- La musica del launcher viene mutata mentre un gioco e in esecuzione, poi riparte al ritorno al menu.
- `P` apre una scheda riassuntiva scritta apposta per il gioco, non la trascrizione completa del PDF.
- `O` continua ad aprire la relazione PDF esternamente.
- `C` apre la schermata About / Credits.

## Avvio

Da PowerShell nella root del progetto:

```powershell
.\.venv\Scripts\python.exe .\auracade_3btlc.py
```

Il workspace VS Code e gia configurato per usare la virtualenv locale tramite `.vscode/settings.json`.

## Versione portable per i ragazzi

Ho preparato anche una distribuzione pronta in [packaging/release/AuRaCADE_3BTLC_Portable](packaging/release/AuRaCADE_3BTLC_Portable).

- Avvio rapido: [packaging/release/AuRaCADE_3BTLC_Portable/Avvia AuRaCADE.bat](packaging/release/AuRaCADE_3BTLC_Portable/Avvia%20AuRaCADE.bat)
- Eseguibile diretto: [packaging/release/AuRaCADE_3BTLC_Portable/AuRaCADE 3BTLC.exe](packaging/release/AuRaCADE_3BTLC_Portable/AuRaCADE%203BTLC.exe)
- Nota rapida per la consegna: [packaging/release/AuRaCADE_3BTLC_Portable/LEGGIMI_PORTABLE.txt](packaging/release/AuRaCADE_3BTLC_Portable/LEGGIMI_PORTABLE.txt)
- ZIP pronto da condividere: [packaging/release/AuRaCADE_3BTLC_Portable.zip](packaging/release/AuRaCADE_3BTLC_Portable.zip)

Questa cartella deve restare intera, perche l'eseguibile legge giochi, PDF, cover e dati dalle sottocartelle accanto, in particolare da `games/`.

Per rigenerare la release portable:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\packaging\build_portable_release.ps1
```

## Comandi del launcher

- `Freccia su/giu` oppure `W/S`: selezione gioco
- `Invio`: avvia il gioco selezionato
- `P`: apre la scheda riassuntiva del gioco
- `O`: apre il PDF della relazione esternamente
- `F`: apre la cartella del gioco
- `C`: apre About / Credits
- `M`: attiva o disattiva la musica del launcher
- `Esc`: chiude pannelli o esce dal launcher

## Ambiente Python

Pacchetti necessari al launcher:

- `pygame`

Se serve reinstallare l'ambiente minimo:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip pygame
```

## Note sulle copertine

Le copertine gia presenti continuano a essere usate dal launcher.
Ho verificato le relazioni PDF disponibili: non contengono immagini estraibili, quindi non e stato possibile rigenerare nuove cover direttamente dai documenti. Dove esistevano screenshot o asset locali dei giochi, le cover reali gia preparate restano in uso.
