$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Python virtualenv non trovata in .venv\\Scripts\\python.exe"
}

$iconScript = Join-Path $scriptDir "generate_launcher_icon.py"
$iconPath = Join-Path $scriptDir "icons\auracade_alom.ico"
$tempRoot = Join-Path $env:TEMP "auracade_pyinstaller"
$buildRoot = Join-Path $tempRoot "build"
$distRoot = Join-Path $tempRoot "dist"
$releaseRoot = Join-Path $scriptDir "release"
$portableRoot = Join-Path $releaseRoot "AuRaCADE_3BTLC_Portable"
$zipPath = Join-Path $releaseRoot "AuRaCADE_3BTLC_Portable.zip"
$specName = "AuRaCADE 3BTLC.spec"
$exeName = "AuRaCADE 3BTLC.exe"
$exePath = Join-Path $portableRoot $exeName

$topLevelItems = @(
    "auracade_assets",
    "games"
)

Write-Host "[1/6] Installo o aggiorno dipendenze packaging nella .venv..."
& $python -m pip install --upgrade pyinstaller pillow

Write-Host "[2/6] Rigenero l'icona personalizzata da Alom..."
& $python $iconScript
if (-not (Test-Path $iconPath)) {
    throw "Icona non generata: $iconPath"
}

Write-Host "[3/6] Pulisco build precedenti..."
Get-Process -Name "AuRaCADE 3BTLC" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $tempRoot, $releaseRoot -ErrorAction SilentlyContinue

Write-Host "[4/6] Creo l'eseguibile del launcher..."
& $python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --noconsole `
    --name "AuRaCADE 3BTLC" `
    --icon $iconPath `
    --specpath $scriptDir `
    --distpath $distRoot `
    --workpath $buildRoot `
    --hidden-import auracade_game_runner `
    "$projectRoot\auracade_3btlc.py"

New-Item -ItemType Directory -Path $portableRoot -Force | Out-Null
Copy-Item (Join-Path $distRoot $exeName) $portableRoot

Write-Host "[5/6] Copio catalogo, moduli e contenuti del cabinet..."
Copy-Item "$projectRoot\auracade_config.py" $portableRoot
Copy-Item "$projectRoot\auracade_audio.py" $portableRoot
Copy-Item "$projectRoot\auracade_game_runner.py" $portableRoot
Copy-Item "$projectRoot\auracade_games.json" $portableRoot
Copy-Item "$projectRoot\README.md" (Join-Path $portableRoot "README_progetto.md")

foreach ($item in $topLevelItems) {
    $sourcePath = Join-Path $projectRoot $item
    $targetPath = Join-Path $portableRoot $item
    Remove-Item -Recurse -Force $targetPath -ErrorAction SilentlyContinue
    Copy-Item $sourcePath $targetPath -Recurse
}

@"
@echo off
cd /d "%~dp0"
start "" "AuRaCADE 3BTLC.exe"
"@ | Set-Content -Encoding ASCII (Join-Path $portableRoot "Avvia AuRaCADE.bat")

@"
AuRaCADE 3BTLC - versione portable

Per usare il cabinet:
1. Lascia tutti i file e le cartelle insieme.
2. Avvia "Avvia AuRaCADE.bat" oppure "AuRaCADE 3BTLC.exe".
3. Se SmartScreen avvisa, scegli Altre informazioni > Esegui comunque.

Questa cartella deve restare completa: l'exe legge giochi, PDF e cover dalle sottocartelle qui presenti, in particolare da games/.
"@ | Set-Content -Encoding UTF8 (Join-Path $portableRoot "LEGGIMI_PORTABLE.txt")

Write-Host "[6/6] Creo lo ZIP della release..."
$zipCompleted = $false
for ($attempt = 1; $attempt -le 6 -and -not $zipCompleted; $attempt++) {
    try {
        Compress-Archive -Path $portableRoot -DestinationPath $zipPath -Force
        $zipCompleted = $true
    }
    catch {
        if ($attempt -eq 6) {
            throw
        }
        Write-Host "Tentativo ZIP $attempt fallito, riprovo..."
        [System.Threading.Thread]::Sleep(800)
    }
}

Write-Host "Build completata: $portableRoot"
Write-Host "ZIP pronto: $zipPath"
Write-Host "File principale: $exePath"
