$version = "18"
$binDir = "bin"
$stockfishPath = "$binDir\stockfish.exe"

if (Test-Path $stockfishPath) {
    Write-Host "Stockfish already installed at $stockfishPath"
    exit 0
}

New-Item -ItemType Directory -Force -Path $binDir | Out-Null

$url = "https://github.com/official-stockfish/Stockfish/releases/download/sf_$version/stockfish-windows-x86-64-avx2.zip"
$zipPath = "$binDir\stockfish.zip"

Write-Host "Downloading Stockfish $version..."
Invoke-WebRequest -Uri $url -OutFile $zipPath

Write-Host "Extracting..."
$tmpDir = "$binDir\_tmp"
Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force
Get-ChildItem -Path $tmpDir -Recurse -Filter "*.exe" | Select-Object -First 1 | Move-Item -Destination $stockfishPath -Force
Remove-Item $zipPath, $tmpDir -Recurse -Force

Write-Host "Stockfish installed at $stockfishPath"
