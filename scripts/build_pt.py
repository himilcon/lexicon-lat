#!/usr/bin/env python3
"""Junta a camada de tradução PT (traducao/lotes/pt-*.tsv: id \\t glosa) em docs/data/pt.json.

As glosas em português foram geradas por IA (Claude) a partir das glosas inglesas do Lewis & Short
e do Elementary Latin Dictionary (traducao/lotes/en-*.tsv, c-*.tsv). Para ampliar a camada, traduza um
novo lote no mesmo formato, salve como traducao/lotes/pt-NN.tsv e rode este script.

Uso: python3 scripts/build_pt.py
"""
import glob
import json
import os
import datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INDEX = json.load(open(os.path.join(ROOT, "docs", "data", "index.json"), encoding="utf-8"))["entries"]
IDS = {e[0] for e in INDEX}

pt = {}
for fn in sorted(glob.glob(os.path.join(ROOT, "traducao", "lotes", "pt-*.tsv"))):
    for n, line in enumerate(open(fn, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        i, _, txt = line.partition("\t")
        if i not in IDS or not txt.strip():
            print(f"{os.path.basename(fn)}:{n}: id desconhecido ou glosa vazia: {line[:60]}")
            continue
        pt[i] = txt.strip()

out = {"versao": datetime.date.today().isoformat() + f"-{len(pt)}",
       "fonte": "Glosas traduzidas do inglês por IA (Claude, Anthropic) a partir do Lewis & Short e do "
                "Elementary Latin Dictionary de Lewis (Perseus, CC BY-SA 4.0). Obra derivada, CC BY-SA 4.0.",
       "pt": pt}
with open(os.path.join(ROOT, "docs", "data", "pt.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

# cobertura do vocabulário dos textos
vocab = json.load(open(os.path.join(ROOT, "scripts", "vocab_textos.json")))
tot = sum(n for _, n in vocab)
cov = sum(n for i, n in vocab if i in pt)
print(f"{len(pt)} verbetes traduzidos; cobrem {cov / tot:.1%} das palavras dos textos (pelo lema mais provável)")
