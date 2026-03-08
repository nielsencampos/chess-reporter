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
Expand-Archive -Path $zipPath -DestinationPath $binDir -Force
Get-ChildItem -Path $binDir -Recurse -Filter "*.exe" | Select-Object -First 1 | Move-Item -Destination $stockfishPath
Remove-Item $zipPath -Recurse

Write-Host "Stockfish installed at $stockfishPath"
