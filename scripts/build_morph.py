#!/usr/bin/env python3
"""Prepara a morfologia latina (análises do Morpheus, Perseus) para o leitor de textos.

Entrada: os arquivos de dados do Diogenes (https://github.com/pjheslin/diogenes-prebuilt-data):
  latin-analyses.txt         forma \t {deslocamento flag forma_com_quantidades,lema \t \t análise}...
  lat.ls.perseus-eng1.xml    a cópia do Lewis & Short a que os deslocamentos se referem
Saída: scripts/morph.pkl  {forma: [(lema, id_LS ou None, análise), ...]}

Uso: python3 scripts/build_morph.py <pasta dependencies/data do Diogenes>
"""
import bisect
import os
import pickle
import re
import sys

D = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))

# deslocamento no XML do Diogenes -> id do verbete na Perseus (orig_id="n2280")
raw = open(os.path.join(D, "lat.ls.perseus-eng1.xml"), "rb").read()
offs, ids = [], []
for m in re.finditer(rb'<div1 [^>]*orig_id="n(\d+[a-z]?)"', raw):
    offs.append(m.start())
    ids.append(m.group(1).decode())
print("verbetes no XML do Diogenes:", len(offs))


def ls_id(off):
    i = bisect.bisect_right(offs, off) - 1
    if i < 0:
        return None
    if offs[i] == off:
        return ids[i]
    return None


ITEM = re.compile(r"\{(\d+) (\d+) ([^\t}]*)\t([^\t}]*)\t([^}]*)\}")
forms = {}
exact = loose = 0
for line in open(os.path.join(D, "latin-analyses.txt"), encoding="utf-8", errors="replace"):
    form, _, rest = line.rstrip("\n").partition("\t")
    out = []
    for m in ITEM.finditer(rest):
        off, flag, lem, _, an = m.groups()
        lemma = lem.split(",")[-1].strip()
        # flag 9: o deslocamento aponta para o verbete exato; flag 0: posição aproximada, não serve
        lid = ls_id(int(off)) if flag != "0" else None
        if lid:
            exact += 1
        else:
            loose += 1
        item = (lemma, lid, an.strip())
        if item not in out:
            out.append(item)
    if out:
        forms[form] = out
print("formas:", len(forms), "· análises com verbete exato:", exact, "· sem:", loose)
pickle.dump(forms, open(os.path.join(HERE, "morph.pkl"), "wb"))
