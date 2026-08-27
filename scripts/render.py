# -*- coding: utf-8 -*-
"""
Genera los dos cancioneros a partir de la fuente canonica en grados y un setlist:

  - con-cejilla: acordes en el tono de FORMA (el que se digita), obtenido
              restando la cejilla al tono real. Se inyecta {capo: N} y los diagramas.
  - sin-cejilla: acordes en el tono REAL, sin cejilla ({capo} eliminado)
              y sin diagramas.

Fuente (songs/**/*.cho):
  - inline  [I] [vi7] [bVII] ...          (grados)
  - ruedas  {grid: ... I · IV · V ...}    (zona maquina: se sustituyen grados)
  - prosa   {comment: ...}                (verbatim)
  - modulacion  {x_degkey: +N}  o  {x_degkey: Si}  (cambia la tonica relativa)

Setlist (setlists/<evento>.json):
  - entries[].path, entries[].order, entries[].capo
  - entries[].key es el tono REAL (el que suena). La forma que se digita en la
    variante con cejilla se deriva como key - capo.

Salida: dist/_build/{con-cejilla,sin-cejilla}/<artista>/<cancion>.cho
"""

import argparse, json, os, re, glob, shutil, sys
import chordlib as cl

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, 'songs')
SETLISTS = os.path.join(ROOT, 'setlists')
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


def setlist_path(value):
    if not value:
        return None
    if value.lower().endswith('.json') or os.path.sep in value or '/' in value:
        path = value
    else:
        path = os.path.join(SETLISTS, value + '.json')
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    return os.path.abspath(path)


def normalize_song_ref(value):
    rel = value.replace('\\', '/').strip()
    if rel.startswith('songs/'):
        rel = rel[len('songs/'):]
    return rel


def load_setlist(value):
    path = setlist_path(value)
    if not path:
        return None, None
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    entries = data.get('entries')
    if not isinstance(entries, list):
        raise ValueError('El setlist no contiene una lista "entries": %s' % path)

    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError('Entrada de setlist no valida en %s' % path)
        rel = normalize_song_ref(entry.get('path', ''))
        if not rel:
            raise ValueError('Entrada sin "path" en %s' % path)
        if 'key' not in entry:
            raise ValueError('Entrada sin "key" para %s en %s' % (rel, path))
        normalized.append({
            'path': rel,
            'order': int(entry.get('order', len(normalized) + 1)),
            'key': str(entry['key']).strip(),
            'capo': int(entry.get('capo', 0)),
        })
    normalized.sort(key=lambda e: (e['order'], e['path']))
    return data, normalized


def find_source_key(lines):
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
    return shape_key, capo


def emit_key_and_capo(out, target, out_key, capo):
    out.append('{key: %s}' % out_key)
    if target == 'con-cejilla':
        out.append('{capo: %d}' % capo)
    else:
        out.append('{diagrams: off}')


def render_song(path, target, song_meta=None):
    """target: 'con-cejilla' | 'sin-cejilla'. Devuelve lista de lineas de salida."""
    lines = open(path, encoding='utf-8').read().splitlines()

    if song_meta:
        real_key = song_meta['key']
        capo = song_meta['capo']
    else:
        real_key, capo = find_source_key(lines)
    if real_key is None:
        raise ValueError('Sin tono para %s. Usa --setlist o anade {key} legacy.' % path)

    if target == 'con-cejilla':
        # Tono de forma: lo que se digita = tono real menos la cejilla.
        out_key = cl.transpose_key(real_key, -capo)
    else:  # sin-cejilla: se toca directamente en el tono real
        out_key = real_key

    tonicpc, _is_minor, prefer = cl.parse_key(out_key)
    reltonic = tonicpc

    out = []
    skip_tab = False
    emitted_key = False
    for ln in lines:
        # Modulacion: mueve la tonica relativa y no se emite.
        m = _DEGKEY_RE.match(ln)
        if m:
            reltonic = set_reltonic(reltonic, m.group(1))
            continue

        # {key}
        m = _KEY_RE.match(ln)
        if m:
            if not emitted_key:
                emit_key_and_capo(out, target, out_key, capo)
                emitted_key = True
            continue

        # {capo}
        m = _CAPO_RE.match(ln)
        if m:
            continue

        # {subtitle}: en la variante con cejilla anota la cejilla si la hay
        m = _SUBTITLE_RE.match(ln)
        if m:
            sub = m.group(1).strip()
            if target == 'con-cejilla' and capo > 0:
                sub = '%s \u00b7 Cejilla %d' % (sub, capo)
            out.append('{subtitle: %s}' % sub)
            continue

        if ln.strip().lower().startswith('{artist:'):
            out.append(render_inline(ln, reltonic, prefer))
            if not emitted_key:
                emit_key_and_capo(out, target, out_key, capo)
                emitted_key = True
            continue

        # Tabs: solo en la variante con cejilla
        if ln.strip().startswith('{start_of_tab'):
            if target == 'sin-cejilla':
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

    if not emitted_key:
        emit_key_and_capo(out, target, out_key, capo)

    return out


def main():
    ap = argparse.ArgumentParser(description='Expande canciones en grados a las variantes con/sin cejilla.')
    ap.add_argument('--setlist', '-s', default='san-roque-2026',
                    help='Nombre o ruta JSON del setlist (por defecto: san-roque-2026).')
    args = ap.parse_args()

    setlist, entries = load_setlist(args.setlist)
    if entries:
        files = [(os.path.join(SONGS, entry['path']), entry) for entry in entries]
    else:
        files = [(f, None) for f in sorted(glob.glob(os.path.join(SONGS, '**', '*.cho'), recursive=True))]
    for target in ('con-cejilla', 'sin-cejilla'):
        target_out = os.path.join(OUT, target)
        if os.path.isdir(target_out):
            shutil.rmtree(target_out)
        for f, meta in files:
            rel = os.path.relpath(f, SONGS)
            dest = os.path.join(OUT, target, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            body = render_song(f, target, meta)
            with open(dest, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write('\n'.join(body) + '\n')
        if setlist:
            print('render %-12s: %d canciones (%s) -> %s' % (
                target, len(files), setlist.get('slug', args.setlist), target_out))
        else:
            print('render %-9s: %d canciones -> %s' % (target, len(files), target_out))


if __name__ == '__main__':
    main()
