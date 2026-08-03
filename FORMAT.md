# Formato de las canciones

Las canciones se escriben en **[ChordPro](https://www.chordpro.org/)** (`.cho`), pero en
este repo la **fuente canónica guarda los acordes en grados** (números romanos), no en un
tono concreto. A partir de esa fuente se generan automáticamente **dos versiones** de cada
canción:

- **Guitarra** — con las **formas** del tono pedido y la **cejilla** indicada (`{capo}`),
  con diagramas de acordes.
- **Bajo** — con los acordes ya **transpuestos al tono real** (sin cejilla), sin diagramas
  ni tablaturas.

> **¿Por qué grados?** Así una sola fuente sirve para cualquier instrumento/tono. El
> guitarrista toca con cejilla usando formas cómodas; el bajista necesita las notas reales.
> Escribiendo en grados no hay que mantener dos transcripciones a mano.

---

## Flujo de trabajo

```
songs/**/*.cho              (fuente en GRADOS  ← esto es lo que editas)
        │
        │  python scripts/render.py     (expande grados → acordes)
        ▼
dist/_build/guitarra/**     dist/_build/bajo/**      (.cho ya en notas)
        │                           │
        │  build.ps1 -Variant guitarra / bajo
        ▼                           ▼
dist/guitarra/**.pdf        dist/bajo/**.pdf
dist/guitarra/cancionero-guitarra.pdf   dist/bajo/cancionero-bajo.pdf
```

Comandos:

```powershell
# 1) expandir grados a las dos variantes en dist\_build\
python scripts\render.py

# 2) compilar PDFs de cada release
.\scripts\build.ps1 -Variant guitarra            # dist\guitarra\<artista>\<cancion>.pdf
.\scripts\build.ps1 -Variant bajo                # dist\bajo\<artista>\<cancion>.pdf

# 3) cancionero completo (un PDF con índice) por release
.\scripts\build.ps1 -Variant guitarra -Songbook  # dist\guitarra\cancionero-guitarra.pdf
.\scripts\build.ps1 -Variant bajo   -Songbook    # dist\bajo\cancionero-bajo.pdf
```

---

## Notación de grados

El grado es un **número romano relativo a la escala MAYOR de la tónica** (regla fija,
también para tonos menores). Su capitalización indica la calidad de la tríada:

- **MAYÚSCULA** = acorde mayor · **minúscula** = acorde menor.
- Prefijo `b` / `#` = alteración cromática de la fundamental.
- Sufijo = color del acorde: `7`, `maj7`, `m7`* , `6`, `°`, `7sus`, `sus4`, `sus2`,
  `+`, `ø`, `add9`, `9`…

  \* el `m` de `m7`/`m6`/`m9` ya está implícito en la minúscula del grado, así que un
  `vi` con séptima menor se escribe `vi7` y un `ii` con séptima, `ii7`.

Equivalencias en **Do mayor** (tónica = Do):

| Grado | Acorde | Grado | Acorde | Grado | Acorde |
|---|---|---|---|---|---|
| `I`   | Do   | `ii`  | Rem  | `iii` | Mim |
| `IV`  | Fa   | `V`   | Sol  | `vi`  | Lam |
| `V7`  | Sol7 | `III7`| Mi7  | `Imaj7`| Domaj7 |
| `bVII`| Sib  | `bVI` | Lab  | `bIII`| Mib |

Ejemplo de tónica **menor** — cadencia andaluza en **Lam** = `i · bVII · bVI · V`
(= `Lam · Sol · Fa · Mi`). Fíjate: la tónica menor es `i`, y como la referencia es siempre
la escala mayor, el `Sol` de Lam sale como `bVII`.

Los acordes van **inline**, entre corchetes, justo delante de la sílaba del cambio:

```
[i]papelillos, arguililla, tu que vas tan enti[bVII]fá
```

---

## Directivas del repo

| Directiva | Para qué sirve |
|---|---|
| `{title: ...}` | Título |
| `{subtitle: ...}` / `{artist: ...}` | Artista |
| `{key: <forma>}` | **Tono de forma** para la guitarra (p. ej. `Lam`). Define la tónica de los grados |
| `{capo: N}` | **Cejilla** en el traste N (solo guitarra; se muestra como `· Cejilla N` en el subtítulo). El bajo lo convierte en transposición real |
| `{grid: ...}` | **Rueda de acordes en grados** (zona “de máquina”: se expande al tono de salida) |
| `{x_degkey: +N}` / `{x_degkey: Nota}` | **Modulación**: mueve la tónica de los grados a partir de ese punto |
| `{comment: ...}` | Nota **literal** visible (caja gris). Texto en prosa; **no** se transpone |
| `{start_of_verse: Etiqueta}` … `{end_of_verse}` | Estrofa con etiqueta |
| `{start_of_chorus: Etiqueta}` … `{end_of_chorus}` | Estribillo (barra lateral) |
| `{chorus}` | Repite el último estribillo sin reescribirlo |
| `{start_of_tab: ...}` … `{end_of_tab}` | Tablatura (solo guitarra; el bajo la **elimina**) |
| `# ...` | Comentario que **no** sale en el PDF (fuente, notas de trabajo) |

### Acordes: `[grado]` inline · `{grid}` · `{comment}`

Tres formas de mostrar acordes, cada una con su papel. **La regla por defecto es inline sobre
la letra** (como en lacuerda.net); `{grid}` y `{comment}` son casos concretos.

- **`[grado]` inline (partes cantadas)** — es lo **normal**: pon el acorde en grados justo
  delante de la sílaba del cambio (incluso a mitad de palabra), encima de la letra. Si una
  sección repite el **mismo ciclo** de acordes línea a línea, pon los acordes **solo en la
  primera vuelta** del ciclo y deja el resto de la sección limpio. Si un verso concreto tiene
  una **variación**, pon ese acorde inline solo ahí.

  ```
  {start_of_verse: Estrofa 1}
  [I]¿Dónde estabas en[V]tonces
  cuando tanto te nece[V]sité?
  ```

- **`{grid: ...}`** para **secciones instrumentales** (intro, punteo, solo, interludio **sin
  letra**) o cuando quieras rotular la rueda de una parte instrumental. Escribe los acordes en
  **grados**; puedes intercalar etiquetas y separadores (`·`, `/`, `x2`, `estrofa:`…) y se
  conservan tal cual. El `{grid}` **sí se transpone** al tono real en el bajo.

  ```
  {grid: Intro: i · bVII · bVI · V  (punteo)}
  ```

- **`{comment: ...}`** solo para **prosa** (recitados, «2ª vez cambia el final…», «mismas
  letras que la Estrofa 1»…). Su texto sale **verbatim** y **no** se transpone, así que **no
  metas acordes que dependan del tono** ahí dentro (saldrían mal en el bajo). Si necesitas
  mostrar acordes, ponlos inline o como grados en un `{grid}`.

### Modulación (`{x_degkey}`)

Cuando una canción **cambia de tono a mitad**, no reescribas todo: a partir del punto de
cambio, sigue poniendo los grados **relativos a la nueva tónica** y marca el cambio con:

- `{x_degkey: +N}` — sube la tónica **N semitonos** (relativo; sobrevive a la cejilla). Es lo
  habitual: p. ej. «sube un tono» = `{x_degkey: +2}`.
- `{x_degkey: Nota}` — fija la tónica a una **nota absoluta** (raro).

El propio `{x_degkey}` no se imprime; solo cambia cómo se expanden los grados de ahí en
adelante. Ejemplo (Insurrección, sube de La a Si tras el primer puente):

```
{start_of_chorus: Puente  [La]}
[V]Me siento hoy como un hal[IV]cón
he[V]rido por las flechas de la
[I]incertidumbre.
{end_of_chorus}

{x_degkey: +2}
{comment: Sube un tono: La a Si}

{start_of_verse: Estrofa 2  [Si]}
[I]Me corto el pelo [IV]una y otra [I]vez.
...
```

---

## Reglas de estilo

- **Una página por canción**: `config/chordpro.json` está ajustado para que cada canción
  quepa en **una sola hoja** (para verla entera en la tablet sin scroll). Si una se va a dos
  páginas, añade `{columns: 2}` tras la cabecera.
- **Letra junta**: no dejes líneas en blanco entre versos de una misma sección.
- **Acordes encima de la letra (inline)**: en las partes cantadas, los acordes van inline
  `[grado]` justo delante de la sílaba del cambio (estilo lacuerda). **No repitas los acordes
  en cada vuelta**: si una sección repite el mismo ciclo, ponlos solo en la **primera línea**
  del ciclo; y si otra sección (p. ej. Estrofa 2) usa la **misma rueda** que una anterior,
  déjala **limpia** (sin acordes) — el label de la sección basta. Reserva `{grid}` para las
  secciones **instrumentales** (sin letra).
- **No repitas el estribillo**: escríbelo una vez con `{start_of_chorus}` y reutilízalo con
  `{chorus}`.
- **Solo ASCII en líneas que se renderizan**: en `{comment}`, `{subtitle}`, `{grid}` y demás
  texto visible evita guiones largos `—`/`–` y flechas `↑→` (el PDF los pinta como `?`). Usa
  `-`, `·`, `a`, `x2`. (En líneas `#`, que no se imprimen, da igual.)
- **Cabecera con la fuente**: primeras líneas `#` indicando de dónde viene la versión.
- **Nombres de archivo**: `songs/<artista-en-minusculas>/<cancion-en-minusculas>.cho`
  (sin acentos ni espacios; usa guiones).

---

## Cómo se comportan las dos variantes

Partiendo de una canción con `{key: Lam}` + `{capo: 3}` (forma Lam, suena en Dom):

| | **Guitarra** | **Bajo** |
|---|---|---|
| Tónica de salida | `Lam` (la forma) | `Dom` (tono real = forma + cejilla) |
| `{capo}` | se conserva | se elimina; se aplica como transposición |
| `{subtitle}` | `Artista · Cejilla 3` (etiqueta visible) | `Artista` (sin cejilla) |
| Diagramas | sí | no (`{diagrams: off}`) |
| Tablaturas `{sot}` | se conservan | se eliminan |
| Un grado `i` | `Lam` | `Dom` |

---

## Esqueleto mínimo (en grados)

```chordpro
# Fuente: <url>
{title: Mi canción}
{subtitle: Artista}
{key: Lam}
{capo: 0}

{grid: Intro: i · bVII · bVI · V}

{start_of_verse: Estrofa 1}
[i]Primera línea con su a[bVII]corde
[bVI]segunda línea y su cam[V]bio
{end_of_verse}

{start_of_verse: Estrofa 2}
Misma rueda, letra limpia sin acordes
porque repite el ciclo de la Estrofa 1
{end_of_verse}

{start_of_chorus: Estribillo}
[bVI]Letra del estri[bVII]billo
{end_of_chorus}

{chorus}
```

---

## Añadir o editar una canción

1. Escribe/edita la fuente en **grados** en `songs/<artista>/<cancion>.cho`.
2. Expande y compila:
   ```powershell
   python scripts\render.py
   .\scripts\build.ps1 -Variant guitarra -Song dist\_build\guitarra\<artista>\<cancion>.cho
   ```
3. Revisa que la variante de **guitarra reproduce exactamente** los acordes que querías. El
   motor `scripts/chordlib.py` tiene un autotest:
   ```powershell
   python scripts\chordlib.py --selftest
   ```

---

## Referencias

- Sintaxis ChordPro: <https://www.chordpro.org/chordpro/chordpro-introduction/>
- Referencia de directivas: <https://www.chordpro.org/chordpro/chordpro-directives/>
