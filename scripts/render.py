# -*- coding: utf-8 -*-
"""
Genera los dos cancioneros a partir de la fuente canonica en grados:

  - guitarra: acordes en el tono de FORMA (el que se digita con cejilla).
              Se mantiene {capo: N} y los diagramas.
  - bajo:     acordes transpuestos al tono REAL (forma + cejilla),
              sin cejilla ({capo} eliminado) y sin diagramas.

Fuente (songs/**/*.cho):
  - {key: <tono de forma>}   {capo: <semitonos de cejilla>}
  - inline  [I] [vi7] [bVII] ...          (grados)
  - ruedas  {grid: ... I · IV · V ...}    (zona maquina: se sustituyen grados)
  - prosa   {comment: ...}                (verbatim)
  - modulacion  {x_degkey: +N}  o  {x_degkey: Si}  (cambia la tonica relativa)

Salida: dist/_build/{guitarra,bajo}/<artista>/<cancion>.cho
"""

import os, re, glob, sys
import chordlib as cl

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, 'songs')
OUT = os.path.join(ROOT, 'dist', '_build')

# Token de grado dentro de una rueda {grid}. El guard parse_degree evita
# falsos positivos (palabras que casualmente empiecen por I/V).
_GRID_TOK = re.compile(
    r'(?<![\w#b\u266f\u266d])'
    r'([#b\u266f\u266d]?)'
    r'([IiVv]{1,3})'
    r'(maj7|m7b5|7sus4|7sus|sus4|sus2|add9|dim|m6|m7|\u00b0|\u00f8|\+|9|7|6|m)?'
    r'(?![\w])'
)

_KEY_RE   = re.compile(r'^\{key:\s*([^}]+)\}\s*$')
_CAPO_RE  = re.compile(r'^\{capo:\s*([^}]+)\}\s*$')
_SUBTITLE_RE = re.compile(r'^\{subtitle:\s*(.*)\}\s*$')
_GRID_RE  = re.compile(r'^\{grid:\s*(.*)\}\s*$')
_DEGKEY_RE = re.compile(r'^\{x_degkey:\s*([^}]+)\}\s*$')
_INLINE_RE = re.compile(r'\[([^\]]+)\]')


def render_grid(text, tonicpc, prefer):
    def repl(m):
        tok = (m.group(1) or '') + m.group(2) + (m.group(3) or '')
        if cl.parse_degree(tok) is None:
            return m.group(0)
        return cl.degree_to_chord(tok, tonicpc, prefer)
    return _GRID_TOK.sub(repl, text)


def render_inline(line, tonicpc, prefer):
    def repl(m):
        tok = m.group(1)
        if cl.parse_degree(tok) is None:
            return m.group(0)
        return '[' + cl.degree_to_chord(tok, tonicpc, prefer) + ']'
    return _INLINE_RE.sub(repl, line)


def set_reltonic(cur, value):
    """value: '+2' / '-1' (relativo) o 'Si' / 'Do#' (absoluto)."""
    v = value.strip()
    if v and v[0] in '+-':
        try:
            return (cur + int(v)) % 12
        except ValueError:
            return cur
    pc = cl.note_pc(v)
    return cur if pc is None else pc


def render_song(path, target):
    """target: 'guitarra' | 'bajo'. Devuelve lista de lineas de salida."""
    lines = open(path, encoding='utf-8').read().splitlines()

    shape_key = None
    capo = 0
    for ln in lines:
        m = _KEY_RE.match(ln)
        if m:
            shape_key = m.group(1).strip()
        m = _CAPO_RE.match(ln)
        if m:
            try:
                capo = int(m.group(1).strip())
            except ValueError:
                capo = 0
    if shape_key is None:
        raise ValueError('Sin {key} en %s' % path)

    if target == 'guitarra':
        out_key = shape_key
    else:  # bajo: tono real = forma + cejilla
        out_key = cl.transpose_key(shape_key, capo)

    tonicpc, _is_minor, prefer = cl.parse_key(out_key)
    reltonic = tonicpc

    out = []
    skip_tab = False
    for ln in lines:
        # Modulacion: mueve la tonica relativa y no se emite.
        m = _DEGKEY_RE.match(ln)
        if m:
            reltonic = set_reltonic(reltonic, m.group(1))
            continue

        # {key}
        m = _KEY_RE.match(ln)
        if m:
            out.append('{key: %s}' % out_key)
            continue

        # {capo}
        m = _CAPO_RE.match(ln)
        if m:
            if target == 'guitarra':
                out.append('{capo: %d}' % capo)
            else:
                out.append('{diagrams: off}')
            continue

        # {subtitle}: en guitarra anota la cejilla si la hay (coste vertical cero)
        m = _SUBTITLE_RE.match(ln)
        if m:
            sub = m.group(1).strip()
            if target == 'guitarra' and capo > 0:
                sub = '%s \u00b7 Cejilla %d' % (sub, capo)
            out.append('{subtitle: %s}' % sub)
            continue

        # Tabs: solo guitarra
        if ln.strip().startswith('{start_of_tab'):
            if target == 'bajo':
                skip_tab = True
                continue
        if skip_tab:
            if ln.strip().startswith('{end_of_tab'):
                skip_tab = False
            continue

        # Ruedas -> comentario con acordes del tono correspondiente
        m = _GRID_RE.match(ln)
        if m:
            out.append('{comment: %s}' % render_grid(m.group(1), reltonic, prefer))
            continue

        # Resto: sustituye grados inline (seguro; lo que no es grado pasa igual)
        out.append(render_inline(ln, reltonic, prefer))

    return out


def main():
    files = sorted(glob.glob(os.path.join(SONGS, '**', '*.cho'), recursive=True))
    for target in ('guitarra', 'bajo'):
        for f in files:
            rel = os.path.relpath(f, SONGS)
            dest = os.path.join(OUT, target, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            body = render_song(f, target)
            with open(dest, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write('\n'.join(body) + '\n')
        print('render %-9s: %d canciones -> %s' % (target, len(files), os.path.join(OUT, target)))


if __name__ == '__main__':
    main()
