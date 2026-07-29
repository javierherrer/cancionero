# 🎸 Cancionero (letra + acordes → PDF, en grados)

Repositorio para escribir **partituras de guitarra** (letra con los acordes encima, estilo
[lacuerda.net](https://lacuerda.net)) en **texto plano versionable** y exportarlas a **PDF**.

La particularidad: la fuente guarda los acordes en **grados** (números romanos), y de ahí se
generan **dos releases** de cada canción:

- 🎸 **Guitarra** — formas del tono pedido + **cejilla** (`{capo}`) y diagramas de acordes.
- 🎵 **Bajo** — acordes **transpuestos al tono real** (sin cejilla), sin diagramas ni tabs.

- **Origen en texto** ([ChordPro](https://www.chordpro.org/)) → diffs limpios, control de versiones real.
- **Letra junta** y **estructura marcada** (Intro, Estrofa, Estribillo, Punteo…). No hace
  falta repetir los acordes en cada verso: se marca la rueda al principio de la sección y el
  estribillo se reutiliza sin reescribirlo.
- **Notación española** (Do · Re · Mi · Fa · Sol · La · Si).
- **Una página por canción** — pensado para leerlo entero en la tablet sin scroll.
- **PDF** con acordes en azul, barra lateral en el estribillo y etiquetas de sección.

---

## Requisitos

- **ChordPro** (genera el PDF):
  ```powershell
  winget install --id Vromans.ChordPro -e
  ```
  > El build detecta `chordpro` automáticamente aunque no esté en el `PATH`.
- **Python 3** (expande los grados a acordes: `scripts/render.py`). Sin dependencias externas
  para generar; para verificar 1 página por PDF se usa `pymupdf` (opcional).

---

## Estructura del repo

```
guitar/
├── songs/                 # 🎵 canciones (.cho) EN GRADOS — esto es lo que editas
│   └── los-moles/
│       └── el-legionario-y-la-morita.cho
├── scripts/
│   ├── chordlib.py        # motor: notación española ⇄ grados  (python chordlib.py --selftest)
│   ├── render.py          # expande grados → dist\_build\{guitarra,bajo}
│   └── build.ps1          # compila los PDF (por release)
├── config/
│   └── chordpro.json      # estilo del PDF + notación española
├── templates/
│   └── plantilla.cho      # plantilla para empezar una canción nueva
├── dist/                  # 📄 artefactos de build (no se versiona)
├── FORMAT.md              # guía del formato (grados, directivas, releases)
└── README.md
```

---

## Generar los PDF

```powershell
# 1) expandir la fuente (grados) a las dos variantes
python scripts\render.py

# 2) compilar cada release
.\scripts\build.ps1 -Variant guitarra            # dist\guitarra\<artista>\<cancion>.pdf
.\scripts\build.ps1 -Variant bajo                # dist\bajo\<artista>\<cancion>.pdf

# 3) cancionero completo con índice
.\scripts\build.ps1 -Variant guitarra -Songbook  # dist\guitarra\cancionero-guitarra.pdf
.\scripts\build.ps1 -Variant bajo   -Songbook    # dist\bajo\cancionero-bajo.pdf
```

---

## Añadir una canción nueva

1. Crea `songs/<artista>/<cancion>.cho` y escribe los acordes **en grados** (ver
   [`FORMAT.md`](FORMAT.md)). Indica el tono de forma con `{key: ...}` y la cejilla con
   `{capo: N}`.
2. Expande y compila:
   ```powershell
   python scripts\render.py
   .\scripts\build.ps1 -Variant guitarra
   ```

> Consejo: pon en las primeras líneas (con `#`) la **fuente** de la versión transcrita
> (URL de lacuerda y su valoración), para saber de dónde viene.

---

## Interpretación de los tonos (p. ej. «Lam +3»)

«Lam +3» = tocar con las **formas de Lam** y la **cejilla en el traste 3**
→ `{key: Lam}` + `{capo: 3}`. En la guitarra los acordes se escriben como la forma (Lam,
Sol, Fa, Mi); en el bajo salen transpuestos al **tono real** (Dom, Sib, Lab, Sol). Sin
número (p. ej. «Do»), sin cejilla (`{capo: 0}`).

---

## Releases

Este repo publica dos PDF de cancionero completo:

- `cancionero-guitarra.pdf`
- `cancionero-bajo.pdf`

---

## Notas

- El `dist/` **no se versiona** (son artefactos de build). Lo que se versiona es el texto
  `.cho` en grados.
- Documentación oficial de ChordPro: <https://www.chordpro.org/chordpro/>
- Las letras/acordes pertenecen a sus autores; este repo es para **uso personal** (estudio
  y práctica).
