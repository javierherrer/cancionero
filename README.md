# 🎸 Cancionero (letra + acordes → PDF, en grados)

Repositorio para escribir **partituras de guitarra** (letra con los acordes encima, estilo
[lacuerda.net](https://lacuerda.net)) en **texto plano versionable** y exportarlas a **PDF**.

La particularidad: la fuente guarda los acordes en **grados** (números romanos), y cada
**setlist de evento** decide en qué tono/cejilla se toca cada canción. De ahí se generan
dos PDF:

- 🎸 **Con cejilla** — formas del tono del setlist + **cejilla** y diagramas de acordes.
- 🎵 **Sin cejilla** — acordes **transpuestos al tono real**, sin diagramas ni tabs.

- **Origen en texto** ([ChordPro](https://www.chordpro.org/)) → diffs limpios, control de versiones real.
- **Letra junta** y **estructura marcada** (Intro, Estrofa, Estribillo, Punteo...). La rueda de
  acordes se muestra una vez al principio de cada sección (y se repite al empezar cada sección
  nueva); el estribillo se escribe una vez y se reutiliza sin reescribirlo.
- **Notación española** (Do · Re · Mi · Fa · Sol · La · Si).
- **Una página por canción** — pensado para leerlo entero en la tablet sin scroll.
- **PDF** con acordes en azul, barra lateral en el estribillo y etiquetas de sección.
- **Portada** en los cancioneros, con el título del setlist y la variante con o sin cejilla.

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
├── setlists/              # 📋 eventos: orden + tono/cejilla por canción
│   └── san-roque-2026.json
├── scripts/
│   ├── chordlib.py        # motor: notación española ⇄ grados  (python chordlib.py --selftest)
│   ├── render.py          # expande setlist → dist\_build\{con-cejilla,sin-cejilla}
│   └── build.ps1          # compila los PDF (por setlist)
├── config/
│   ├── chordpro.json      # estilo del PDF + notación española
│   └── orden.txt          # orden legacy si no usas setlist
├── templates/
│   └── plantilla.cho      # plantilla para empezar una canción nueva
├── dist/                  # 📄 artefactos de build (no se versiona)
├── FORMAT.md              # guía del formato (grados, directivas, setlists)
└── README.md
```

---

## Generar los PDF

```powershell
# 1) expandir un setlist (grados + tono/cejilla) a las dos variantes
python scripts\render.py --setlist preboda-mercedes-alberto

# 2) compilar cada variante
.\scripts\build.ps1 -Variant con-cejilla
.\scripts\build.ps1 -Variant sin-cejilla

# 3) cancionero del setlist con índice
.\scripts\build.ps1 -Variant con-cejilla -Songbook -Setlist preboda-mercedes-alberto
.\scripts\build.ps1 -Variant sin-cejilla -Songbook -Setlist preboda-mercedes-alberto
# dist\con-cejilla\cancionero-con-cejilla.pdf
# dist\sin-cejilla\cancionero-sin-cejilla.pdf
```

---

## Añadir una canción nueva

1. Crea `songs/<artista>/<cancion>.cho` y escribe los acordes **en grados** (ver
   [`FORMAT.md`](FORMAT.md)). No pongas `{key}` ni `{capo}` en la canción.
2. Añade la canción al JSON de setlist (`setlists/<evento>.json`) indicando `path`,
   `order`, `key` y `capo`.
3. Expande y compila:
   ```powershell
   python scripts\render.py --setlist preboda-mercedes-alberto
   .\scripts\build.ps1 -Variant con-cejilla -Songbook -Setlist preboda-mercedes-alberto
   ```

> Consejo: pon en las primeras líneas (con `#`) la **fuente** de la versión transcrita
> (URL de lacuerda y su valoración, o texto aportado), para saber de dónde viene.

---

## Interpretación de los tonos (p. ej. «Lam +3»)

«Lam +3» = tocar con las **formas de Lam** y la **cejilla en el traste 3**
→ en el setlist: `"key": "Lam", "capo": 3`. En el PDF con cejilla los acordes se escriben
como la forma (Lam, Sol, Fa, Mi); en el PDF sin cejilla salen transpuestos al **tono real**
(Dom, Sib, Lab, Sol). Sin número (p. ej. «Do»), sin cejilla (`"capo": 0`).

---

## Setlists y releases

Cada evento vive en `setlists/<evento>.json`. Cada entrada guarda:

```json
{ "order": 1, "path": "songs/artista/cancion.cho", "key": "La", "capo": 0 }
```

Cada release de evento publica dos PDF:

- `cancionero-con-cejilla.pdf`
- `cancionero-sin-cejilla.pdf`

---

## Notas

- El `dist/` **no se versiona** (son artefactos de build). Lo que se versiona es el texto
  `.cho` en grados y los setlists JSON.
- Documentación oficial de ChordPro: <https://www.chordpro.org/chordpro/>
- Las letras/acordes pertenecen a sus autores; este repo es para **uso personal** (estudio
  y práctica).
