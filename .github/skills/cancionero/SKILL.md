---
name: cancionero
description: 'Manual del cancionero de guitarra/bajo (ChordPro en grados -> PDF). Usala para: anadir o transcribir una cancion (de lacuerda.net), editar acordes/letra, cambiar el tono o la cejilla ({key}/{capo}), simplificar secciones repetidas con ruedas {grid}, marcar modulaciones {x_degkey}, regenerar los PDFs (render.py + build.ps1) de las releases guitarra y bajo, verificar que cada cancion cabe en 1 pagina, o publicar/actualizar la release de GitHub. Add, edit, transpose, render or publish guitar/bass songbook songs written in ChordPro Roman-numeral degrees.'
---

# Cancionero — guitarra y bajo (ChordPro en grados)

Manual operativo de este repo: partituras estilo lacuerda.net (letra + acordes encima)
escritas en **grados romanos** como fuente unica, de las que se generan **dos releases** en
PDF: **guitarra** (tono de forma + cejilla + diagramas) y **bajo** (tono real transpuesto,
sin cejilla ni diagramas). Cada cancion cabe en **una pagina** (para el iPad, sin scroll).

## Cuando usarla
- Anadir o transcribir una cancion nueva (p. ej. de lacuerda.net).
- Editar la letra o los acordes de una cancion existente.
- Cambiar el **tono** o la **cejilla** de una cancion (`{key}` / `{capo}`).
- Simplificar una seccion repetitiva con una **rueda** (`{grid}`).
- Marcar un **cambio de tono** a mitad de cancion (`{x_degkey}`).
- **Regenerar los PDFs** de una cancion o de los cancioneros completos.
- **Publicar/actualizar** los cancioneros en la release de GitHub.

## Arquitectura en 30 segundos
- La fuente vive en `songs/<artista>/<cancion>.cho` con los acordes en **grados**
  (`[I]`, `[vi7]`, `[bVII]`...), no en notas.
- Dos directivas de cabecera fijan la tonalidad: `{key: <forma>}` + `{capo: N}`. Notacion
  tipo lacuerda: **"LAm +3" = `{key: Lam}` `{capo: 3}`** (La menor, cejilla en el 3er traste).
- `scripts/render.py` expande los grados a **dos** juegos en `dist/_build/{guitarra,bajo}`:
  - **guitarra** -> tono de forma (`{key}`), conserva `{capo}` y, si hay cejilla,
    la anota en el `{subtitle}` como `... · Cejilla N`; con diagramas.
  - **bajo** -> tono real (`{key}` transpuesto `+{capo}`), sin cejilla, sin diagramas ni tablaturas.
- `scripts/build.ps1` compila esos `.cho` a PDF con ChordPro.
- Notacion **espanola** (Do Re Mi Fa Sol La Si) via `config/chordpro.json`.
- La especificacion completa del formato esta en **[FORMAT.md](../../../FORMAT.md)**.

## Flujo: regenerar los PDFs
Siempre `render.py` **antes** que `build.ps1`.

```powershell
# 0) (una vez por sesion) consola en UTF-8 para que · y acentos no fallen
$env:PYTHONIOENCODING = 'utf-8'

# 1) expandir grados -> dist\_build\{guitarra,bajo}
python scripts\render.py

# 2a) una cancion concreta (las dos variantes)
.\scripts\build.ps1 -Variant guitarra -Song dist\_build\guitarra\<artista>\<cancion>.cho
.\scripts\build.ps1 -Variant bajo     -Song dist\_build\bajo\<artista>\<cancion>.cho

# 2b) o todo: canciones sueltas + cancionero, en ambas variantes
.\scripts\build.ps1 -Variant guitarra
.\scripts\build.ps1 -Variant guitarra -Songbook
.\scripts\build.ps1 -Variant bajo
.\scripts\build.ps1 -Variant bajo -Songbook
```

Salida: `dist\{guitarra,bajo}\<artista>\<cancion>.pdf` y
`dist\{guitarra,bajo}\cancionero-<variant>.pdf`. La carpeta `dist/` **no** se versiona.

## Flujo: anadir una cancion nueva
1. Copia `templates/plantilla.cho` a `songs/<artista>/<cancion>.cho` (minusculas, sin acentos
   ni espacios, con guiones).
2. Rellena la cabecera: `{title}`, `{subtitle}`/`{artist}`, `{key: <forma>}`, `{capo: N}`.
   Traduce el tono pedido: "LAm +3" -> `{key: Lam}` `{capo: 3}`. Deja 1-2 lineas `#` con la
   URL de origen (fuente de lacuerda).
3. Escribe la letra **junta** con los acordes en **grados** inline `[grado]` delante de la
   silaba del cambio (encima de la letra, estilo lacuerda; incluso a mitad de palabra). Si una
   seccion repite el **mismo ciclo** de acordes, ponlos **solo en la primera vuelta** y deja el
   resto limpio; si otra seccion usa la **misma rueda** que una anterior, dejala limpia. Usa
   `{grid: ...}` **solo para secciones instrumentales** (intro/solo sin letra); ver Reglas.
4. `python scripts\render.py` y compila la cancion (flujo anterior).
5. **Verifica 1 pagina** (ver Verificacion). Si se va a 2, anade `{columns: 2}` tras la
   cabecera o compacta con `{grid}`.
6. Revisa que la **variante guitarra reproduce exactamente** los acordes que querias.
7. Anade la ruta `<artista>/<cancion>.cho` a `config/orden.txt` en la posicion deseada del
   cancionero (si no aparece, va al final).

## Orden del cancionero
El orden de las canciones del cancionero (`-Songbook`) y de su indice unico lo fija
`config/orden.txt` (una ruta `<artista>/<cancion>.cho` por linea; las no listadas van al
final). El indice impreso y los marcadores del PDF usan ese orden via `songindex` en
`contents`/`pdf.outlines` de `config/chordpro.json`.

## Flujo: editar tono, cejilla o simplificar
- **Cambiar tono/cejilla**: edita solo `{key}` y/o `{capo}`; ambos releases se regeneran
  coherentes. (Subir una cancion "a DO" = ajustar `{key}`/`{capo}` para que el tono real sea Do.)
- **Simplificar seccion repetitiva (parte cantada)**: no repitas los acordes en cada vuelta.
  Deja los acordes inline `[grado]` **solo en la primera linea** del ciclo y limpia el resto; si
  otra seccion repite la **misma rueda**, dejala **limpia** entera (el label basta). Si una
  seccion es casi constante pero tiene **un acorde distinto**, conserva **solo** ese acorde
  desviado inline en su verso (ejemplo real: outro de *el-secreto-de-las-tortugas* con `[#I]`).
- **Seccion instrumental** (intro/solo/interludio sin letra): usa `{grid: <rueda en grados>}`
  (se transpone al tono real del bajo); nunca notas sueltas en `{comment}`.
- **Modulacion** (cambia de tono a mitad): a partir del cambio sigue escribiendo grados
  relativos a la **nueva** tonica y marca el punto con `{x_degkey: +N}` (N semitonos; "sube un
  tono" = `+2`). No se imprime.

## Flujo: publicar en la release de GitHub
Repo: `javierherrer/cancionero`. La release **"San Roque 2026"** (tag `v1.0`) contiene
`cancionero-guitarra.pdf` y `cancionero-bajo.pdf`.

```powershell
# regenera antes los dos cancioneros completos (flujo de arriba con -Songbook)
gh release upload v1.0 `
  "dist\guitarra\cancionero-guitarra.pdf" `
  "dist\bajo\cancionero-bajo.pdf" `
  --clobber
gh release view v1.0 --json name,assets --jq '{name:.name, assets:[.assets[].name]}'
```

`--clobber` reemplaza los assets existentes. Renombrar la release:
`gh release edit v1.0 --title "<nuevo>"`.

## Reglas y trampas
- **Una pagina por cancion**: `config/chordpro.json` esta ajustado para eso. Si una se pasa,
  usa `{columns: 2}` o simplifica con `{grid}`.
- **Letra junta**: sin lineas en blanco entre versos de una misma seccion.
- **Acordes encima de la letra**: en partes cantadas, inline `[grado]` sobre la silaba (estilo
  lacuerda). **No repitas acordes en cada verso** ni **el estribillo** (`{start_of_chorus}` una
  vez + `{chorus}` para repetir): pon los acordes solo en la 1a vuelta del ciclo y deja limpias
  las secciones que repiten la misma rueda.
- **`[grado]` inline en lo cantado; `{grid}` para acordes instrumentales que se transponen;
  `{comment}` solo para prosa**. No metas acordes dependientes del tono en un `{comment}`:
  saldrian mal en el bajo.
- **Solo ASCII en lineas visibles** (`{comment}`, `{grid}`, `{subtitle}`, `{title}`...): nada
  de `—`, `–`, `↑`, `→` (el PDF los pinta como `?`). Usa `-`, `·`, `x2`, "sube un tono". En
  lineas `#` (no se imprimen) da igual.
- **Grados = numero romano relativo a la escala MAYOR** de la tonica (tambien en tonos
  menores). Mayuscula = mayor, minuscula = menor; `b`/`#` altera la fundamental; sufijos `7`,
  `maj7`, `sus4`... La `m` de menor ya esta implicita en la minuscula (un `vi` con 7a menor se
  escribe `vi7`).
- **Consola cp1252**: exporta `$env:PYTHONIOENCODING = 'utf-8'` antes de scripts que imprimen `·`.
- **Autor de commits**: `Javier Herrer Torres <jherrerzgz@gmail.com>` (ya en la config local).

## Verificacion
```powershell
# el motor grados<->espanol tiene autotest
python scripts\chordlib.py --selftest        # espera "OK"

# nº de paginas de un PDF (pymupdf disponible como 'fitz')
python -c "import fitz; print(fitz.open(r'dist\guitarra\<artista>\<cancion>.pdf').page_count)"
```
Cada cancion debe dar **1**; los cancioneros dan (nº de canciones + indice).

## Referencias
- **[FORMAT.md](../../../FORMAT.md)** — especificacion completa (grados, directivas, `{grid}`,
  `{x_degkey}`, reglas de estilo, esqueleto minimo).
- **[README.md](../../../README.md)** — vision general y estructura del repo.
- `scripts/chordlib.py` — motor grados <-> notacion espanola (nucleo).
- `scripts/render.py` — expande grados -> `dist/_build/{guitarra,bajo}`.
- `scripts/build.ps1` — compila los PDF (`-Variant`, `-Song`, `-Songbook`).
- `templates/plantilla.cho` — plantilla para empezar una cancion nueva.
