$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Plugin = Join-Path $Root "zotero-plugin"
$Dist = Join-Path $Root "dist"
$Zip = Join-Path $Dist "codex-zotero-bridge.zip"
$Xpi = Join-Path $Dist "codex-zotero-bridge.xpi"

New-Item -ItemType Directory -Force -Path $Dist | Out-Null
if (Test-Path $Zip) { Remove-Item $Zip -Force }
if (Test-Path $Xpi) { Remove-Item $Xpi -Force }

Compress-Archive -Path (Join-Path $Plugin "*") -DestinationPath $Zip -Force
Rename-Item -Path $Zip -NewName "codex-zotero-bridge.xpi"
Write-Host "Built $Xpi"
