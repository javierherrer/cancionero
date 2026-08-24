# -*- coding: utf-8 -*-
"""
Motor de acordes para el cancionero.

Convierte entre notación española de acordes (Do, Rem, Sol7, Mibdim, Fa#m...)
y grados romanos relativos a una tonalidad (I, ii, V7, biii°, bVII...), y
renderiza grados a acordes en cualquier tonalidad con el enarmónico correcto.

Convención de grados (la que pidió el usuario):
  - Numeral romano relativo a la ESCALA MAYOR de la tónica (regla fija).
  - MAYÚSCULA = tríada mayor, minúscula = tríada menor.
  - prefijo b / # = alteración cromática de la fundamental.
  - sufijo = 7, maj7, 6, °, 7sus4, sus4, sus2, +, ø, add9, 9...
Ejemplos en Do:  Do=I  Rem=ii  Mi7=III7  Fa=IV  Sol7=V7  Lam=vi  Sib=bVII  Mibdim=biii°
"""

import re

# --- Notas ------------------------------------------------------------------
BASE = {'Do': 0, 'Re': 2, 'Mi': 4, 'Fa': 5, 'Sol': 7, 'La': 9, 'Si': 11}
SHARP = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
FLAT  = ['Do', 'Reb', 'Re', 'Mib', 'Mi', 'Fa', 'Solb', 'Sol', 'Lab', 'La', 'Sib', 'Si']

_ROOT_RE = re.compile(r'^(Do|Re|Mi|Fa|Sol|La|Si)([#b\u266f\u266d]?)')

def _acc_delta(a):
    if a in ('#', '\u266f'):
        return 1
    if a in ('b', '\u266d'):
        return -1
    return 0

def note_pc(name):
    """Pitch-class de una nota (Do=0..Si=11). None si no es nota."""
    m = _ROOT_RE.match(name.strip())
    if not m:
        return None
    return (BASE[m.group(1)] + _acc_delta(m.group(2))) % 12

def spell(pc, prefer):
    return (SHARP if prefer in ('#', '\u266f') else FLAT)[pc % 12]

# --- Calidades --------------------------------------------------------------
# code -> (sufijo de grado, caso mayor '+'/menor '-')
DEG_SUFFIX = {
    'maj': ('', '+'), 'min': ('', '-'), 'dim': ('\u00b0', '-'), 'aug': ('+', '+'),
    'dom7': ('7', '+'), 'min7': ('7', '-'), 'maj7': ('maj7', '+'),
    '6': ('6', '+'), 'min6': ('6', '-'),
    'dom7sus4': ('7sus4', '+'), 'sus4': ('sus4', '+'), 'sus2': ('sus2', '+'),
    'dim7': ('\u00b07', '-'), 'm7b5': ('\u00f8', '-'),
    'add9': ('add9', '+'), 'dom9': ('9', '+'), 'min9': ('9', '-'),
}
# code -> sufijo del nombre de acorde
NAME_SUFFIX = {
    'maj': '', 'min': 'm', 'dim': 'dim', 'aug': 'aug',
    'dom7': '7', 'min7': 'm7', 'maj7': 'maj7', '6': '6', 'min6': 'm6',
    'dom7sus4': '7sus', 'sus4': 'sus4', 'sus2': 'sus2',
    'dim7': 'dim7', 'm7b5': 'm7b5', 'add9': 'add9', 'dom9': '9', 'min9': 'm9',
}
# texto de calidad (tras la fundamental) -> code
_QUAL = {
    '': 'maj', 'm': 'min', 'min': 'min', '-': 'min',
    'm7': 'min7', 'min7': 'min7', '-7': 'min7',
    'maj7': 'maj7', 'Maj7': 'maj7', 'M7': 'maj7', '7M': 'maj7', '7+': 'maj7',
    '7': 'dom7', '6': '6', 'm6': 'min6', 'min6': 'min6',
    'dim': 'dim', '\u00b0': 'dim', '\u00ba': 'dim', 'o': 'dim',
    'dim7': 'dim7', '\u00b07': 'dim7', '\u00ba7': 'dim7',
    'm7b5': 'm7b5', '\u00f8': 'm7b5',
    'aug': 'aug', '+': 'aug', '5+': 'aug', 'aug5': 'aug',
    'sus': 'sus4', 'sus4': 'sus4', 'sus2': 'sus2',
    '7sus': 'dom7sus4', '7sus4': 'dom7sus4',
    'add9': 'add9', '9': 'dom9', 'm9': 'min9', 'min9': 'min9',
}

def parse_chord(token):
    """'Sol7' -> (7, 'dom7', ''). None si no parece un acorde.
    El tercer elemento es el signo escrito de la fundamental ('#', 'b' o '')."""
    t = token.strip()
    m = _ROOT_RE.match(t)
    if not m:
        return None
    rootpc = (BASE[m.group(1)] + _acc_delta(m.group(2))) % 12
    a = m.group(2)
    sign = '#' if a in ('#', '\u266f') else 'b' if a in ('b', '\u266d') else ''
    rest = t[m.end():].strip()
    code = _QUAL.get(rest)
    if code is None:
        return None
    return (rootpc, code, sign)

# --- Grados -----------------------------------------------------------------
# semitono desde la tónica -> (romano mayúscula, alteración)
_SEMI = {
    0: ('I', ''), 1: ('II', 'b'), 2: ('II', ''), 3: ('III', 'b'), 4: ('III', ''),
    5: ('IV', ''), 6: ('IV', '#'), 7: ('V', ''), 8: ('VI', 'b'), 9: ('VI', ''),
    10: ('VII', 'b'), 11: ('VII', ''),
}
_ROMAN_VAL = {'I': 0, 'II': 2, 'III': 4, 'IV': 5, 'V': 7, 'VI': 9, 'VII': 11}
# Grafía alternativa de los grados cromáticos según se escriba con # o b:
_SEMI_SHARP = {1: ('I', '#'), 3: ('II', '#'), 6: ('IV', '#'), 8: ('V', '#'), 10: ('VI', '#')}
_SEMI_FLAT  = {1: ('II', 'b'), 3: ('III', 'b'), 6: ('V', 'b'), 8: ('VI', 'b'), 10: ('VII', 'b')}
_DEG_RE = re.compile(r'^([b#\u266f\u266d]?)([IiVv]+)(.*)$')

def chord_to_degree(rootpc, code, tonicpc, root_acc=''):
    offset = (rootpc - tonicpc) % 12
    if root_acc == '#' and offset in _SEMI_SHARP:
        roman, acc = _SEMI_SHARP[offset]
    elif root_acc == 'b' and offset in _SEMI_FLAT:
        roman, acc = _SEMI_FLAT[offset]
    else:
        roman, acc = _SEMI[offset]
    suf, case = DEG_SUFFIX[code]
    rn = roman if case == '+' else roman.lower()
    return acc + rn + suf

def parse_degree(token):
    """'V7' -> (offset=7, code='dom7', acc=''). None si no es grado."""
    t = token.strip()
    m = _DEG_RE.match(t)
    if not m:
        return None
    acc, roman, suf = m.group(1), m.group(2), m.group(3)
    up = roman.upper()
    if up not in _ROMAN_VAL:
        return None
    lower = roman.islower()
    offset = (_ROMAN_VAL[up] + _acc_delta(acc)) % 12
    if suf == '':
        code = 'min' if lower else 'maj'
    elif suf == '7':
        code = 'min7' if lower else 'dom7'
    elif suf == 'maj7':
        code = 'maj7'
    elif suf == '6':
        code = 'min6' if lower else '6'
    elif suf == '\u00b0':
        code = 'dim'
    elif suf == '\u00b07':
        code = 'dim7'
    elif suf == '+':
        code = 'aug'
    elif suf == '7sus4':
        code = 'dom7sus4'
    elif suf == 'sus4':
        code = 'sus4'
    elif suf == 'sus2':
        code = 'sus2'
    elif suf == '\u00f8':
        code = 'm7b5'
    elif suf == 'add9':
        code = 'add9'
    elif suf == '9':
        code = 'min9' if lower else 'dom9'
    else:
        return None
    return (offset, code, acc)

def degree_to_chord(token, tonicpc, key_prefer):
    """Renderiza un grado a acorde español en la tonalidad dada. Passthrough si no es grado."""
    pd = parse_degree(token)
    if pd is None:
        return token
    offset, code, acc = pd
    rootpc = (tonicpc + offset) % 12
    if acc in ('#', '\u266f'):
        prefer = '#'
    elif acc in ('b', '\u266d'):
        prefer = 'b'
    else:
        prefer = key_prefer
    return spell(rootpc, prefer) + NAME_SUFFIX[code]

# --- Tonalidad --------------------------------------------------------------
_SHARP_MAJ = {7, 2, 9, 4, 11, 6}

def parse_key(keyname):
    """'Lam' -> (tonicpc=9, is_minor=True, prefer='b')."""
    t = keyname.strip()
    m = _ROOT_RE.match(t)
    if not m:
        raise ValueError('Tonalidad no reconocida: %r' % keyname)
    tonicpc = (BASE[m.group(1)] + _acc_delta(m.group(2))) % 12
    rest = t[m.end():].strip()
    is_minor = rest.startswith('m') and not rest.startswith('maj')
    base = (tonicpc + 3) % 12 if is_minor else tonicpc
    prefer = '#' if base in _SHARP_MAJ else 'b'
    return (tonicpc, is_minor, prefer)

def transpose_key(keyname, semitones):
    """Transpone el NOMBRE de una tonalidad (mantiene mayor/menor)."""
    tonicpc, is_minor, _ = parse_key(keyname)
    newpc = (tonicpc + semitones) % 12
    base = (newpc + 3) % 12 if is_minor else newpc
    prefer = '#' if base in _SHARP_MAJ else 'b'
    return spell(newpc, prefer) + ('m' if is_minor else '')

# --- Self test --------------------------------------------------------------
def _norm(c):
    return c.replace(' ', '').replace('sus4', 'sus').replace('\u00ba', '\u00b0')


def _selftest():
    """Test unitario autonomo del motor (no depende del corpus de canciones)."""
    fails = []

    # 1) Round-trip exhaustivo acorde -> grado -> acorde en varias tonalidades.
    #    Para cada tono se generan acordes con la grafia natural del tono (SHARP en
    #    tonos con sostenidos, FLAT en el resto), de modo que las notas diatonicas se
    #    escriben como el tono espera y las cromaticas conservan su alteracion.
    quals = ['', 'm', '7', 'm7', 'maj7', '6', 'm6', 'dim', 'sus4', 'sus2',
             'aug', 'add9', '9', 'm9', '7sus', 'dim7', 'm7b5']
    keys = ['Do', 'Sol', 'Re', 'La', 'Mi', 'Si', 'Fa', 'Sib', 'Mib',
            'Lam', 'Mim', 'Rem', 'Fa#m', 'Dom', 'Solm']
    total = ok = 0
    for key in keys:
        tonicpc, _is_minor, prefer = parse_key(key)
        names = SHARP if prefer in ('#', '\u266f') else FLAT
        for root in names:
            for q in quals:
                chord = root + q
                pc = parse_chord(chord)
                if pc is None:
                    fails.append((key, chord, 'no-parse'))
                    total += 1
                    continue
                deg = chord_to_degree(pc[0], pc[1], tonicpc, pc[2])
                if parse_degree(deg) is None:
                    fails.append((key, chord, 'grado-no-parse:%s' % deg))
                    total += 1
                    continue
                back = degree_to_chord(deg, tonicpc, prefer)
                total += 1
                if _norm(back) == _norm(chord):
                    ok += 1
                else:
                    fails.append((key, chord, '%s->%s->%s' % (chord, deg, back)))

    # 2) Grados concretos esperados (bloquea la convencion).
    expect_deg = [
        ('Lam', 'Lam', 'i'), ('Lam', 'Sol', 'bVII'), ('Lam', 'Fa', 'bVI'),
        ('Lam', 'Mi', 'V'), ('Lam', 'Mi7', 'V7'), ('Lam', 'Rem', 'iv'),
        ('Do', 'Do', 'I'), ('Do', 'Rem', 'ii'), ('Do', 'Mi7', 'III7'),
        ('Do', 'Sol7', 'V7'), ('Do', 'Lam', 'vi'), ('Do', 'Sib', 'bVII'),
        ('Do', 'Domaj7', 'Imaj7'), ('Do', 'Lam7', 'vi7'), ('Do', 'Rem7', 'ii7'),
        ('Do', 'Mi7sus', 'III7sus4'),
        ('Mi', 'Mi', 'I'), ('Mi', 'Fa#m', 'ii'), ('Mi', 'La', 'IV'), ('Mi', 'Si', 'V'),
    ]
    for key, chord, deg in expect_deg:
        tonicpc, _im, _pf = parse_key(key)
        pc = parse_chord(chord)
        got = chord_to_degree(pc[0], pc[1], tonicpc, pc[2])
        if got != deg:
            fails.append((key, chord, 'grado esperado %s, obtenido %s' % (deg, got)))

    # 3) Expansion de grados al tono (color chords transpuestos).
    expect_chord = [
        # todos-los-besos: con-cejilla Do vs sin-cejilla Mib (+3)
        ('Domaj7', 'Do', 'Domaj7'), ('Imaj7', 'Mib', 'Mibmaj7'),
        ('vi7', 'Mib', 'Dom7'), ('ii7', 'Mib', 'Fam7'),
        # cadencia andaluza en el tono real sin cejilla (Dom)
        ('i', 'Dom', 'Dom'), ('bVII', 'Dom', 'Sib'),
        ('bVI', 'Dom', 'Lab'), ('V', 'Dom', 'Sol'),
    ]
    for deg, key, want in expect_chord:
        tonicpc, _im, prefer = parse_key(key)
        got = degree_to_chord(deg, tonicpc, prefer)
        if _norm(got) != _norm(want):
            fails.append((key, deg, 'esperado %s, obtenido %s' % (want, got)))

    # 4) transpose_key (forma + cejilla -> tono real sin cejilla).
    expect_tk = [('Lam', 3, 'Dom'), ('Do', 3, 'Mib'), ('Mi', 0, 'Mi'),
                 ('La', 2, 'Si'), ('Fa', 0, 'Fa'), ('Do', 5, 'Fa')]
    for key, semis, want in expect_tk:
        got = transpose_key(key, semis)
        if got != want:
            fails.append((key, '+%d' % semis, 'esperado %s, obtenido %s' % (want, got)))

    # 5) parse_degree: los grados parsean; las palabras/notas NO.
    for good in ('I', 'V7', 'vi7', 'bVII', 'bVI', 'III7', 'Imaj7', 'iv', 'i', 'III7sus4', 'iv6'):
        if parse_degree(good) is None:
            fails.append(('parse_degree', good, 'deberia parsear'))
    for bad in ('Intro', 'andaluza', 'La', 'Do', 'base', 'x2', 'Interludio', 'Estrofa'):
        if parse_degree(bad) is not None:
            fails.append(('parse_degree', bad, 'no deberia parsear'))

    print('Round-trip matriz: %d/%d OK' % (ok, total))
    print('Aserciones extra : %s' % ('todas OK' if not any(f for f in fails) else '%d fallos' % len(fails)))
    for f in fails:
        print('  FAIL', f)
    return not fails

if __name__ == '__main__':
    import sys
    if '--selftest' in sys.argv:
        sys.exit(0 if _selftest() else 1)
    # demo rápida
    for tok, key in [('Sol7', 'Do'), ('Rem', 'Do'), ('Lam', 'Do'), ('Mibdim', 'Do'),
                     ('Fa#m', 'Mi'), ('Domaj7', 'Do'), ('Lam7', 'Do'), ('Mi7sus', 'La')]:
        tpc, mi, pf = parse_key(key)
        pc = parse_chord(tok)
        deg = chord_to_degree(pc[0], pc[1], tpc, pc[2])
        back = degree_to_chord(deg, tpc, pf)
        print('%-8s en %-4s -> %-7s -> %s' % (tok, key, deg, back))
