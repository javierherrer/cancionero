<#
.SYNOPSIS
    Genera los PDF de las canciones (.cho) del cancionero usando ChordPro.

.DESCRIPTION
    - Sin parámetros: convierte todas las canciones de songs\ a dist\ (misma estructura de carpetas).
    - -Song <ruta>: genera solo esa canción.
    - -Songbook: genera un único PDF con todas las canciones e índice.
    - -Variant con-cejilla|sin-cejilla: compila la versión correspondiente desde dist\_build\<variant>
      (generado por scripts\render.py) hacia dist\<variant>. Combínalo con -Songbook para
      obtener cancionero-con-cejilla.pdf o cancionero-sin-cejilla.pdf.
    - -Setlist <evento>: limita el cancionero a setlists\<evento>.json y usa su orden.

.EXAMPLE
    .\scripts\build.ps1
    .\scripts\build.ps1 -Song songs\los-moles\el-legionario-y-la-morita.cho
    .\scripts\build.ps1 -Songbook
    .\scripts\build.ps1 -Variant con-cejilla -Songbook -Setlist preboda-mercedes-alberto
    .\scripts\build.ps1 -Variant sin-cejilla
#>
[CmdletBinding()]
param(
    [string]$Song,
    [switch]$Songbook,
    [ValidateSet('con-cejilla','sin-cejilla')]
    [string]$Variant,
    [string]$Setlist,
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

function Resolve-SetlistPath {
    param([string]$Value, [string]$Root)
    if (-not $Value) { return $null }
    if ($Value.EndsWith('.json') -or $Value.Contains('\') -or $Value.Contains('/')) {
        $path = $Value
    } else {
        $path = Join-Path $Root "setlists\$Value.json"
    }
    if (-not [System.IO.Path]::IsPathRooted($path)) {
        $path = Join-Path $Root $path
    }
    return (Resolve-Path -LiteralPath $path).Path
}

function Get-SetlistSongs {
    param([string]$SetlistPath, [string]$SongsDir, [string]$Root)
    $data = Get-Content -LiteralPath $SetlistPath -Raw | ConvertFrom-Json
    if (-not $data.entries) { throw "El setlist no contiene entries: $SetlistPath" }

    $result = @()
    foreach ($entry in ($data.entries | Sort-Object order, path)) {
        $rel = [string]$entry.path
        if ($rel.StartsWith('songs/')) { $rel = $rel.Substring(6) }
        if ($rel.StartsWith('songs\')) { $rel = $rel.Substring(6) }
        $rel = $rel.Replace('/', '\')
        $path = Join-Path $SongsDir $rel
        if (-not (Test-Path -LiteralPath $path)) {
            throw "No existe la cancion del setlist: $path"
        }
        $result += (Resolve-Path -LiteralPath $path).Path
    }
    return $result
}

function New-SongbookCover {
    param([string]$Path, [string]$Title, [string]$Variant)
    $variantLabel = if ($Variant -eq 'con-cejilla') { 'Con cejilla' } else { 'Sin cejilla' }
    @(
        '{title: ' + $Title + '}'
        '{subtitle: ' + $variantLabel + '}'
        '{new_page}'
    ) | Set-Content -LiteralPath $Path -Encoding utf8
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

$setlistPath = Resolve-SetlistPath -Value $Setlist -Root $Root

if ($Song) {
    $songs = @((Resolve-Path $Song).Path)
} elseif ($setlistPath) {
    $songs = Get-SetlistSongs -SetlistPath $setlistPath -SongsDir $songsDir -Root $Root
} else {
    $songs = Get-ChildItem -Path $songsDir -Filter *.cho -Recurse | Select-Object -ExpandProperty FullName
}
if (-not $songs) { Write-Warning "No hay canciones .cho en $songsDir"; return }

# Orden explícito del cancionero (config\orden.txt). Las no listadas van al final (alfabético).
$orderFile = Join-Path $Root 'config\orden.txt'
if ((-not $Song) -and (-not $setlistPath) -and (Test-Path $orderFile)) {
    $rank = @{}
    $idx  = 0
    foreach ($line in Get-Content -LiteralPath $orderFile) {
        $rel = $line.Trim()
        if (-not $rel -or $rel.StartsWith('#')) { continue }
        $rank[$rel.Replace('/', '\')] = $idx
        $idx++
    }
    $songs = $songs | Sort-Object `
        @{ Expression = {
            $rel = $_.Substring($songsDir.Length).TrimStart('\', '/')
            if ($rank.ContainsKey($rel)) { $rank[$rel] } else { [int]::MaxValue }
        } }, `
        @{ Expression = { $_ } }
}

Write-Host "chordpro : $chordpro" -ForegroundColor DarkGray
Write-Host "config   : $Config"   -ForegroundColor DarkGray
if ($Variant) { Write-Host "variant  : $Variant" -ForegroundColor DarkGray }
if ($setlistPath) { Write-Host "setlist  : $setlistPath" -ForegroundColor DarkGray }

if ($Songbook) {
    if ($Variant -eq 'con-cejilla') {
        $name = 'cancionero-con-cejilla.pdf'
    } elseif ($Variant -eq 'sin-cejilla') {
        $name = 'cancionero-sin-cejilla.pdf'
    } else {
        $name = 'cancionero.pdf'
    }
    $out  = Join-Path $distDir $name
    $coverTitle = 'Cancionero'
    if ($setlistPath) {
        $setlistData = Get-Content -LiteralPath $setlistPath -Raw | ConvertFrom-Json
        if ($setlistData.title) { $coverTitle = [string]$setlistData.title }
    }
    $cover = Join-Path $distDir '_cover.cho'
    $coverPdf = Join-Path $distDir '_cover.pdf'
    $bodyPdf = Join-Path $distDir '_songbook.pdf'
    New-SongbookCover -Path $cover -Title $coverTitle -Variant $Variant
    & $chordpro --config=$Config --toc $songs -o $bodyPdf
    if ($LASTEXITCODE -ne 0) { throw "Falló la generación del cancionero" }
    & $chordpro --config=$Config $cover -o $coverPdf
    if ($LASTEXITCODE -ne 0) { throw "Falló la generación de la portada" }
    python -c "import fitz,sys; merged=fitz.open(); cover=fitz.open(sys.argv[1]); body=fitz.open(sys.argv[2]); merged.insert_pdf(cover); merged.insert_pdf(body); merged.save(sys.argv[3]); merged.close(); cover.close(); body.close()" $coverPdf $bodyPdf $out
    if ($LASTEXITCODE -ne 0) { throw "Falló la combinación de portada y cancionero" }
    Remove-Item -LiteralPath $cover, $coverPdf, $bodyPdf -Force
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
