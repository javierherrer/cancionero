---
name: cancionero
description: 'Manual del cancionero con/sin cejilla (ChordPro en grados -> PDF). Usala para: anadir o transcribir una cancion, editar acordes/letra, cambiar el tono o la cejilla en setlists/*.json, gestionar setlists por evento, simplificar secciones repetidas con ruedas {grid}, marcar modulaciones {x_degkey}, regenerar PDFs (render.py + build.ps1), verificar que cada cancion cabe en 1 pagina, o publicar/actualizar una release de GitHub.'
---

# Cancionero - con y sin cejilla (ChordPro en grados)

Manual operativo de este repo: partituras estilo lacuerda.net (letra + acordes encima)
escritas en **grados romanos** como fuente unica. Cada evento tiene un JSON en
`setlists/<evento>.json` que decide orden, tono y cejilla; de ahi se generan dos PDF:
**con cejilla** (formas del tono + diagramas) y **sin cejilla** (tono real transpuesto, sin
diagramas). Cada cancion cabe en **una pagina** (para el iPad, sin scroll).

## Cuando usarla
- Anadir o transcribir una cancion nueva.
- Editar la letra o los acordes de una cancion existente.
- Cambiar el **tono** o la **cejilla** de una cancion en un setlist (`key` / `capo`).
- Crear o editar setlists por evento.
- Simplificar una seccion repetitiva con una **rueda** (`{grid}`).
- Marcar un **cambio de tono** a mitad de cancion (`{x_degkey}`).
- **Regenerar los PDFs** de una cancion o de un setlist completo.
- **Publicar/actualizar** los cancioneros en una release de GitHub.

## Arquitectura en 30 segundos
- La fuente vive en `songs/<artista>/<cancion>.cho` con acordes en **grados**
  (`[I]`, `[vi7]`, `[bVII]`...), no en notas, y **sin `{key}` ni `{capo}`**.
- El setlist vive en `setlists/<evento>.json`; cada entrada tiene:
  `path`, `order`, `key` (**tono real**, el que suena) y `capo`.
- Notacion tipo lacuerda: **"LAm +3"** = formas de Lam con cejilla 3, que suena en **Dom**
  -> se guarda como **`"key": "Dom", "capo": 3`**. La forma se deriva (`key` - `capo`).
- `scripts/render.py --setlist <evento>` expande los grados a `dist/_build/{con-cejilla,sin-cejilla}`:
  - **con-cejilla** -> tono de forma (`key` - `capo`), conserva cejilla y la anota bajo el
    titulo como `Artista · Cejilla N`; con diagramas.
  - **sin-cejilla** -> tono real (`key`), sin cejilla, sin
    diagramas ni tablaturas.
- `scripts/build.ps1` compila esos `.cho` a PDF con ChordPro.
- Notacion **espanola** (Do Re Mi Fa Sol La Si) via `config/chordpro.json`.
- La especificacion completa del formato esta en **[FORMAT.md](../../../FORMAT.md)**.

## Flujo: regenerar los PDFs
Siempre `render.py` **antes** que `build.ps1`.

```powershell
$env:PYTHONIOENCODING = 'utf-8'

# 1) expandir setlist -> dist\_build\{con-cejilla,sin-cejilla}
python scripts\render.py --setlist preboda-mercedes-alberto

# 2a) una cancion concreta (las dos variantes)
.\scripts\build.ps1 -Variant con-cejilla -Song dist\_build\con-cejilla\<artista>\<cancion>.cho
.\scripts\build.ps1 -Variant sin-cejilla -Song dist\_build\sin-cejilla\<artista>\<cancion>.cho

# 2b) cancionero completo del setlist
.\scripts\build.ps1 -Variant con-cejilla -Songbook -Setlist preboda-mercedes-alberto
.\scripts\build.ps1 -Variant sin-cejilla -Songbook -Setlist preboda-mercedes-alberto
```

Salida: `dist\{con-cejilla,sin-cejilla}\<artista>\<cancion>.pdf` y
`dist\con-cejilla\cancionero-con-cejilla.pdf` / `dist\sin-cejilla\cancionero-sin-cejilla.pdf`.
Los cancioneros empiezan con una portada que muestra el título del setlist y la variante.
La carpeta `dist/` **no** se versiona.

## Flujo: anadir una cancion nueva
1. Copia `templates/plantilla.cho` a `songs/<artista>/<cancion>.cho` (minusculas, sin acentos
   ni espacios, con guiones).
2. Rellena la cabecera: `{title}` y `{artist}`. El artista ya se imprime bajo el titulo,
   asi que **no repitas `{subtitle}`** (usalo solo si aporta algo distinto). No pongas
   `{key}` ni `{capo}`. Deja 1-2 lineas `#` con la URL/origen de la version.
3. Escribe la letra **junta** con los acordes en **grados** inline `[grado]` delante de la
   silaba del cambio (encima de la letra, estilo lacuerda; incluso a mitad de palabra). El
   estribillo se escribe una vez (`{start_of_chorus}`) y se reutiliza con `{chorus}`. Usa
   `{grid: ...}` **solo para secciones instrumentales** (intro/solo/interludio sin letra).
4. Anade la cancion al JSON de setlist (`path`, `order`, `key` = tono real, `capo`).
5. `python scripts\render.py --setlist <evento>` y compila la cancion.
6. **Verifica 1 pagina**. Si se va a 2, anade `{columns: 2}` tras la cabecera o compacta.
7. Revisa que la variante **con cejilla** reproduce exactamente los acordes que querias.

## Setlists
El orden de las canciones del cancionero (`-Songbook`), el tono y la cejilla los fija
`setlists/<evento>.json`:

```json
{ "order": 1, "path": "songs/artista/cancion.cho", "key": "Dom", "capo": 3 }
```

`key` es el tono **real** (lo que suena) y `capo` el traste de la cejilla. La forma que se
digita se calcula como `key` - `capo` (en el ejemplo: suena Dom, se toca con formas de Lam).

El indice impreso y los marcadores del PDF usan ese orden via `songindex` en
`contents`/`pdf.outlines` de `config/chordpro.json`. `config/orden.txt` queda como modo legacy
si compilas sin `-Setlist`.

## Flujo: editar tono, cejilla o simplificar
- **Cambiar tono/cejilla**: edita solo `key` y/o `capo` en el setlist; ambos PDF se regeneran
  coherentes. `key` es el tono **real**, asi que "subir una cancion a DO" = poner `"key": "Do"`;
  la `capo` solo decide con que formas se digita en la variante con cejilla.
- **Parte cantada**: muestra la rueda **una vez, en la 1a vuelta al principio de cada seccion**,
  y deja **limpio** el resto de la seccion si repite el mismo ciclo; **vuelvela a poner al inicio
  de cada seccion nueva**. **Conserva las variaciones** inline en su verso. Si la seccion no
  repite ciclo (through-composed), cifra cada verso.
- **Seccion instrumental** (intro/solo/interludio sin letra): usa `{grid: <rueda en grados>}`
  (se transpone al tono real del PDF sin cejilla); nunca notas sueltas en `{comment}`.
- **Modulacion**: a partir del cambio sigue escribiendo grados relativos a la nueva tonica y
  marca el punto con `{x_degkey: +N}` (N semitonos; "sube un tono" = `+2`). No se imprime.

## Flujo: publicar en una release de GitHub
Repo: `javierherrer/cancionero`. Cada evento puede tener su propia release. Los assets se llaman:
`cancionero-con-cejilla.pdf` y `cancionero-sin-cejilla.pdf`.

```powershell
# regenera antes con -Songbook -Setlist <evento>
gh release upload <tag> `
  "dist\con-cejilla\cancionero-con-cejilla.pdf" `
  "dist\sin-cejilla\cancionero-sin-cejilla.pdf" `
  --clobber
gh release view <tag> --json name,assets --jq '{name:.name, assets:[.assets[].name]}'
```

`--clobber` reemplaza los assets existentes. Renombrar la release:
`gh release edit <tag> --title "<nuevo>"`.

## Reglas y trampas
- **Una pagina por cancion**: `config/chordpro.json` esta ajustado para eso. Si una se pasa,
  usa `{columns: 2}` o simplifica con `{grid}`.
- **Letra junta**: sin lineas en blanco entre versos de una misma seccion.
- **Acordes encima de la letra**: en partes cantadas, inline `[grado]` sobre la silaba (estilo
  lacuerda). **Muestra la rueda una vez, en la 1a vuelta al principio de cada seccion**, y deja
  limpio el resto de la seccion si repite el mismo ciclo; repitela al inicio de cada seccion nueva.
- **`[grado]` inline en lo cantado; `{grid}` para acordes instrumentales que se transponen;
  `{comment}` solo para prosa**.
- **Solo ASCII en lineas visibles** (`{comment}`, `{grid}`, `{subtitle}`, `{title}`...): evita
  guiones largos y flechas; usa `-`, `·`, `x2`, "sube un tono". En lineas `#` da igual.
- **Grados = numero romano relativo a la escala MAYOR** de la tonica (tambien en tonos menores).
- **Consola cp1252**: exporta `$env:PYTHONIOENCODING = 'utf-8'`.
- **Autor de commits**: `Javier Herrer Torres <jherrerzgz@gmail.com>` (ya en la config local).

## Verificacion
```powershell
python scripts\chordlib.py --selftest
python -c "import fitz; print(fitz.open(r'dist\con-cejilla\<artista>\<cancion>.pdf').page_count)"
```

Cada cancion debe dar **1**; los cancioneros dan (nº de canciones + indice).

## Referencias
- **[FORMAT.md](../../../FORMAT.md)** — especificacion completa (grados, directivas, setlists).
- **[README.md](../../../README.md)** — vision general y estructura del repo.
- `scripts/chordlib.py` — motor grados <-> notacion espanola (nucleo).
- `scripts/render.py` — expande grados + setlist -> `dist/_build/{con-cejilla,sin-cejilla}`.
- `scripts/build.ps1` — compila los PDF (`-Variant`, `-Song`, `-Songbook`, `-Setlist`).
- `templates/plantilla.cho` — plantilla para empezar una cancion nueva.
