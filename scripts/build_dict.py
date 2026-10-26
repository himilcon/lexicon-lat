#!/usr/bin/env python3
"""Converte o Lewis & Short (TEI-XML da Perseus) para os arquivos JSON do site.

Fontes (CC BY-SA 4.0, Perseus Digital Library, https://github.com/PerseusDL/lexica):
  - lat.ls.perseus-eng2.xml           Lewis & Short, A Latin Dictionary (1879)
  - viaf2845558.viaf001.xml           Lewis, An Elementary Latin Dictionary (1890) — só as glosas curtas

Saída (em docs/data/):
  - index.json         lista de verbetes: [id, chave, cabeçalho, gramática, glosa EN, bloco]
  - ls/NNN.json        corpo dos verbetes em HTML simples, em blocos de BLOCK verbetes
  - glosas-en.json     glosas curtas em inglês por id (entrada para a tradução automática)

Uso: python3 scripts/build_dict.py <pasta lexica/CTS_XML_TEI/perseus/pdllex/lat> docs/data
"""
import html
import html.entities
import json
import os
import re
import sys
import unicodedata

from lxml import etree

BLOCK = 500

SRC, OUT = sys.argv[1], sys.argv[2]
LS = os.path.join(SRC, "ls", "lat.ls.perseus-eng2.xml")
ELEM = os.path.join(SRC, "viaf2845558", "viaf001", "viaf2845558.viaf001.xml")


def nfc(s):
    return unicodedata.normalize("NFC", s)


def esc(s):
    return html.escape(s, quote=False)


def norm_key(s):
    """chave de busca: sem diacríticos, minúsculas, j→i, v→u, sem números de homônimo"""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("j", "i").replace("v", "u")
    s = re.sub(r"[^a-z ]", "", s)
    return s.strip()


# ---------- HTML do verbete ----------

SKIP = {"cb", "pb", "figure"}
GRAM = {"itype", "gen", "pos", "case", "number", "mood"}


def inner(el, ctx):
    out = [esc(el.text or "")]
    for ch in el:
        out.append(node(ch, ctx))
        out.append(esc(ch.tail or ""))
    return "".join(out)


def node(el, ctx):
    tag = el.tag if isinstance(el.tag, str) else ""
    if tag in SKIP or not tag:
        return ""
    if tag == "orth":
        return f'<b class="o">{inner(el, ctx)}</b>'
    if tag in GRAM:
        return f'<span class="g">{inner(el, ctx)}</span>'
    if tag == "etym":
        return f'<span class="et">{inner(el, ctx)}</span>'
    if tag == "hi":
        r = el.get("rend", "")
        if r == "sup":
            return f"<sup>{inner(el, ctx)}</sup>"
        return f"<i>{inner(el, ctx)}</i>"
    if tag == "quote":
        return f'<span class="q">{inner(el, ctx)}</span>'
    if tag == "bibl":
        return f'<span class="b">{inner(el, ctx)}</span>'
    if tag == "trans" or tag == "tr":
        return f'<span class="t">{inner(el, ctx)}</span>' if tag == "trans" else inner(el, ctx)
    if tag == "foreign":
        lang = el.get("lang", "")
        if lang == "greek":
            return f'<span lang="grc">{inner(el, ctx)}</span>'
        return f"<i>{inner(el, ctx)}</i>"
    if tag == "usg":
        return f'<span class="u">{inner(el, ctx)}</span>'
    if tag == "sense":
        lv = el.get("level", "1")
        n = el.get("n", "")
        num = f'<span class="sn">{esc(n)}</span> ' if n and n != "0" else ""
        return f'</div><div class="s l{esc(lv)}">{num}{inner(el, ctx)}</div><div class="s c">'
    # cit, author, lbl, xr, ref, sic, corr, reg, q, name, title, …: só o conteúdo
    return inner(el, ctx)


def entry_html(el):
    body = '<div class="s c">' + inner(el, {}) + "</div>"
    body = re.sub(r'<div class="s c">\s*</div>', "", body)
    body = re.sub(r"\s+", " ", body)
    body = body.replace(" </div>", "</div>")
    return nfc(body.strip())


# ---------- glosa curta em inglês ----------

STOP_EN = set("""a an the to of in on at by for with from be is are was were as or and that this
which who one any some something someone into out up down over under not no it its his her their
make made give put take bring go come have having being""".split())
NOT_GLOSS = re.compile(r"^(fin|init|l\.\s*l|ib|id|ibid|al|sq|sqq|v|cf|q\.\s*v|h\.\s*l|e\.\s*g|i\.\s*e|lit|transf|trop|"
                       r"poet|meton|esp|absol|act|pass|neutr|dep|class|post|ante|perh|prob|acc|abl|dat|gen|nom|voc|"
                       r"inf|part|plur|sing|comp|sup|adv|adj|subst|fig|freq|rare|very rare|late lat)\.?$", re.I)


def looks_english(s):
    w = re.findall(r"[a-z]+", s.lower())
    if not w:
        return False
    if NOT_GLOSS.match(s.strip(" ,;:.")):
        return False
    if any(x in STOP_EN for x in w):
        return True
    # palavras inglesas comuns terminam assim; latim raramente
    return len(w) <= 4 and all(re.search(r"(ing|ed|ly|ness|ful|ous|ion|er|y|e|t|d|k|w|l|p|h|g)$", x) for x in w) \
        and not any(re.search(r"(us|um|ae|am|is|os|ibus|orum|arum|o)$", x) for x in w)


END_BAD = {"the", "a", "an", "of", "in", "to", "with", "and", "or", "by", "for", "from", "as", "at", "on"}


def bad_fragment(t):
    w = re.findall(r"[A-Za-z]+", t)
    if not w:
        return True
    if all(x.lower() in STOP_EN for x in w):
        return True
    if w[-1].lower() in END_BAD:
        return True
    return len(w) == 1 and len(w[0]) <= 3 and w[0][0].isupper()


LABELS = r"(Fig|Meton|Praegn|Poet|Pass|Absol|Transf|Trop|Lit|Trans|Colloq|Prov|Esp|Sc|Rarely|Act|Neutr?|Impers|" \
         r"Part|Adj|Adv|Subst|Of [a-z]+|In gen|In partic|In a good sense|In a bad sense|In mal\. part|Comp|Sup|Plur|Sing|Lit)\.?"


def clean_gap(g):
    """texto entre dois elementos, sem colchetes, parênteses, rótulos e pontuação"""
    g = re.sub(r"\[[^\]]*\]", " ", g)
    g = re.sub(r"\([^)]*\)", " ", g)
    g = re.sub(LABELS, " ", g)
    return re.sub(r"[\s,:;.\-—–]+", "", g)


def gap_before(el):
    prev = el.getprevious()
    return (prev.tail or "") if prev is not None else (el.getparent().text or ""), prev


GRAM_WORDS = set("""m f n sing plur dem predic pleonast supin abl acc dat gen nom voc rel adverb collect neutr absol
pass act part adj adv subst comp sup cum esp sc transf trop lit fig meton poet impers dep v a""".split())


def polish(gl):
    """tira das glosas rótulos gramaticais soltos (n., sing.; Supin. abl.) e prefixos como 'n., '"""
    out = []
    for g in gl:
        g = re.sub(r"^((m|f|n|plur|sing|subst|absol|pass|act|adv|rel|adverb|collect|neutr)\.,?\s+)+", "", g).strip(" ,;:.")
        w = re.findall(r"[A-Za-z]+", g)
        if not w or all(x.lower() in GRAM_WORDS for x in w):
            continue
        if len(w) <= 2 and any(x.lower() in GRAM_WORDS for x in w) and not looks_english(" ".join(w[-1:])):
            continue
        out.append(g)
    return out


def ls_glosses(el, limit=4):
    """glosas em itálico do L&S: itálicos diretamente no verbete ou numa acepção, numa sequência
    só de itálicos (to like, to love) — itálicos isolados no meio de frases são outra coisa"""
    found = []
    for hi in el.iter("hi"):
        if hi.get("rend") != "ital" or hi.getparent().tag not in ("entryFree", "sense"):
            continue
        gap, prev = gap_before(hi)
        if clean_gap(gap):
            continue
        if prev is not None and prev.tag not in ("hi", "itype", "gen", "pos", "orth", "etym", "usg", "bibl", "cit", "foreign"):
            continue
        t = re.sub(r"\s+", " ", "".join(hi.itertext())).strip(" ,;:.—-")
        if len(t) < 3 or len(t) > 80 or not looks_english(t) or bad_fragment(t):
            continue
        if t.lower() not in [f.lower() for f in found]:
            found.append(t)
        if len(found) >= limit:
            break
    return found


def load_elementary():
    """{chave: [glosas]} do Elementary Latin Dictionary (glosas marcadas com <tr>)"""
    raw = open(ELEM, encoding="utf-8").read()
    raw = re.sub(r"<!DOCTYPE.*?\]>", "", raw, flags=re.S)
    ents = html.entities.name2codepoint

    def ent(m):
        n = m.group(1)
        if n in ("lt", "gt", "amp", "quot", "apos"):
            return m.group(0)
        if n in ents:
            return chr(ents[n])
        if n.endswith("macr") and len(n) == 5:
            return unicodedata.normalize("NFC", n[0] + "̄")
        if n == "breve":
            return "˘"
        if n == "acutemacr":
            return "̄"
        if n == "cj":
            return "ĵ"
        if n == "ast":
            return "*"
        return ""
    raw = re.sub(r"&([A-Za-z]+);", ent, raw)
    root = etree.fromstring(raw.encode("utf-8"), etree.XMLParser(recover=True, huge_tree=True))
    out = {}
    for e in root.iter("entry"):
        key = e.get("key") or ""
        trs = []
        for tr in e.iter("tr"):
            tn = tr.getparent()
            gap, prev = gap_before(tn)
            dash = "—" in gap
            if re.search(r"i\.\s*e\.\s*$", gap) or clean_gap(gap):
                continue
            if prev is not None and prev.tag == "foreign" and not dash:
                continue
            t = re.sub(r"\s+", " ", "".join(tr.itertext())).strip(" ,;:.—-")
            if t and len(t) <= 80 and t.lower() not in [x.lower() for x in trs]:
                trs.append(t)
            if len(trs) >= 4:
                break
        if trs:
            out.setdefault(key, trs)
    return out


# ---------- principal ----------

def main():
    elem = load_elementary()
    print("Elementary: glosas para", len(elem), "chaves")
    parser = etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False)
    tree = etree.parse(LS, parser)
    entries = []
    for el in tree.iter("entryFree"):
        sid = el.get("id") or ""
        m = re.match(r"n(\d+[a-z]?)$", sid)
        if not m:
            print("id estranho", sid)
            continue
        eid = m.group(1)
        key = el.get("key") or ""
        orths = [nfc(re.sub(r"\s+", " ", "".join(o.itertext())).strip()) for o in el.findall("orth")]
        head = orths[0] if orths else key
        # gramática: itype/gen/pos antes do primeiro <sense>
        gram = []
        for ch in el:
            if ch.tag == "sense":
                break
            if ch.tag in ("itype", "gen", "pos"):
                t = re.sub(r"\s+", " ", "".join(ch.itertext())).strip()
                if t:
                    gram.append(t)
        gram = nfc(", ".join(gram))
        # glosa curta: Elementary (mesma chave) ou itálicos do L&S
        base = re.sub(r"\d+$", "", key)
        gl = elem.get(key)
        if gl is None and key == base:
            gl = elem.get(key + "1") if (key + "2") not in elem else None
        if gl is None and key != base and (base + "1") not in elem:
            gl = elem.get(base)
        gl = polish(gl) if gl else gl
        src = "E" if gl else "L"
        if not gl:
            gl = polish(ls_glosses(el))
        entries.append({
            "id": eid, "key": key, "head": head, "gram": gram,
            "en": nfc("; ".join(gl)), "src": src if gl else "",
            "html": entry_html(el), "type": el.get("type", ""),
            "hom": int(el.get("n")) if (el.get("n") or "").isdigit() else 0,
        })
    print("verbetes:", len(entries))
    print("com glosa:", sum(1 for e in entries if e["en"]),
          "· do Elementary:", sum(1 for e in entries if e["src"] == "E"),
          "· do L&S:", sum(1 for e in entries if e["src"] == "L"))

    os.makedirs(os.path.join(OUT, "ls"), exist_ok=True)
    index = []
    for i, e in enumerate(entries):
        e["blk"] = i // BLOCK
        # último campo: tamanho do verbete em centenas de caracteres (palavras comuns têm verbetes longos;
        # serve para ordenar homônimos e formas flexionadas na busca)
        index.append([e["id"], e["key"], e["head"], e["gram"], e["en"], e["blk"], len(e["html"]) // 100])
    for b in range(0, len(entries), BLOCK):
        chunk = {str(e["id"]): e["html"] for e in entries[b:b + BLOCK]}
        with open(os.path.join(OUT, "ls", f"{b // BLOCK:03d}.json"), "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "..", "..", "traducao", "glosas-en.json"), "w", encoding="utf-8") as f:
        json.dump({str(e["id"]): e["en"] for e in entries if e["en"]}, f, ensure_ascii=False, indent=0)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"fonte": "Lewis & Short, A Latin Dictionary (1879) — Perseus Digital Library, CC BY-SA 4.0",
                   "bloco": BLOCK, "entries": index}, f, ensure_ascii=False, separators=(",", ":"))
    # mapa id -> chave normalizada, usado pelo leitor de textos
    with open(os.path.join(OUT, "..", "..", "scripts", "ls_keys.json"), "w", encoding="utf-8") as f:
        json.dump({e["id"]: [e["key"], norm_key(e["key"])] for e in entries}, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
