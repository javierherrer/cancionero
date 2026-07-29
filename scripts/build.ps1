<#
.SYNOPSIS
    Genera los PDF de las canciones (.cho) del cancionero usando ChordPro.

.DESCRIPTION
    - Sin parámetros: convierte todas las canciones de songs\ a dist\ (misma estructura de carpetas).
    - -Song <ruta>: genera solo esa canción.
    - -Songbook: genera un único PDF (dist\cancionero.pdf) con todas las canciones e índice.
    - -Variant guitarra|bajo: compila el release correspondiente desde dist\_build\<variant>
      (generado por scripts\render.py) hacia dist\<variant>. Combínalo con -Songbook para
      obtener dist\cancionero-<variant>.pdf.

.EXAMPLE
    .\scripts\build.ps1
    .\scripts\build.ps1 -Song songs\los-moles\el-legionario-y-la-morita.cho
    .\scripts\build.ps1 -Songbook
    .\scripts\build.ps1 -Variant guitarra -Songbook
    .\scripts\build.ps1 -Variant bajo
#>
[CmdletBinding()]
param(
    [string]$Song,
    [switch]$Songbook,
    [ValidateSet('guitarra','bajo')]
    [string]$Variant,
    [string]$Config,
    [string]$Root
)

$ErrorActionPreference = 'Stop'

if (-not $Root) {
    $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    $Root = Split-Path -Parent $scriptDir
}

function Find-ChordPro {
    $cmd = Get-Command chordpro -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $candidates = @(
        (Join-Path $env:ProgramFiles 'ChordPro.ORG\ChordPro\chordpro.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'ChordPro.ORG\ChordPro\chordpro.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\ChordPro.ORG\ChordPro\chordpro.exe')
    )
    foreach ($c in $candidates) { if ($c -and (Test-Path $c)) { return $c } }
    $found = Get-ChildItem -Path $env:ProgramFiles, ${env:ProgramFiles(x86)} `
        -Filter chordpro.exe -Recurse -ErrorAction SilentlyContinue -Depth 3 | Select-Object -First 1
    if ($found) { return $found.FullName }
    throw "No se encontró 'chordpro'. Instálalo con:  winget install --id Vromans.ChordPro -e"
}

$chordpro = Find-ChordPro
if (-not $Config)  { $Config  = Join-Path $Root 'config\chordpro.json' }

if ($Variant) {
    $songsDir = Join-Path $Root "dist\_build\$Variant"
    $distDir  = Join-Path $Root "dist\$Variant"
    if (-not (Test-Path $songsDir)) {
        throw "No existe $songsDir. Ejecuta primero:  python scripts\render.py"
    }
} else {
    $songsDir = Join-Path $Root 'songs'
    $distDir  = Join-Path $Root 'dist'
}
New-Item -ItemType Directory -Force -Path $distDir | Out-Null

if ($Song) {
    $songs = @((Resolve-Path $Song).Path)
} else {
    $songs = Get-ChildItem -Path $songsDir -Filter *.cho -Recurse | Select-Object -ExpandProperty FullName
}
if (-not $songs) { Write-Warning "No hay canciones .cho en $songsDir"; return }

Write-Host "chordpro : $chordpro" -ForegroundColor DarkGray
Write-Host "config   : $Config"   -ForegroundColor DarkGray
if ($Variant) { Write-Host "variant  : $Variant" -ForegroundColor DarkGray }

if ($Songbook) {
    $name = if ($Variant) { "cancionero-$Variant.pdf" } else { 'cancionero.pdf' }
    $out  = Join-Path $distDir $name
    & $chordpro --config=$Config --toc $songs -o $out
    if ($LASTEXITCODE -eq 0) { Write-Host "OK  $out" -ForegroundColor Green }
    else { throw "Falló la generación del cancionero" }
    return
}

$fail = 0
foreach ($s in $songs) {
    $rel    = $s.Substring($songsDir.Length).TrimStart('\', '/')
    $outRel = [System.IO.Path]::ChangeExtension($rel, '.pdf')
    $out    = Join-Path $distDir $outRel
    New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
    & $chordpro --config=$Config $s -o $out
    if ($LASTEXITCODE -eq 0) { Write-Host "OK  $outRel" -ForegroundColor Green }
    else { Write-Host "ERR $rel" -ForegroundColor Red; $fail++ }
}
if ($fail) { throw "$fail canción(es) fallaron" }
Write-Host "Listo: $($songs.Count) PDF(s) en dist\" -ForegroundColor Green
