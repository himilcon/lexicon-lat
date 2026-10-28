#!/usr/bin/env python3
"""Gera os textos do leitor: texto latino da Perseus (canonical-latinLit, CC BY-SA 4.0) com cada
palavra analisada pelo Morpheus (Perseus) e ligada ao verbete do Lewis & Short.

A análise é feita por consulta de formas, sem desambiguação pelo contexto: cada palavra traz todas
as análises possíveis, ordenadas pela frequência do lema no conjunto dos textos.

Uso: python3 scripts/build_text.py <pasta canonical-latinLit/data> docs [<pasta AquinasOperaOmnia/summa>]
"""
import collections
import hashlib
import json
import os
import pickle
import re
import sys
import unicodedata

from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
SUMMA = sys.argv[3] if len(sys.argv) > 3 else None
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import summa  # noqa: E402
import latim_medieval as LM  # noqa: E402
MORPH = pickle.load(open(os.path.join(HERE, "morph.pkl"), "rb"))
LSKEYS = json.load(open(os.path.join(HERE, "ls_keys.json"), encoding="utf-8"))   # id -> [chave, chave normalizada]
INDEX = json.load(open(os.path.join(OUT, "data", "index.json"), encoding="utf-8"))["entries"]
HEAD = {e[0]: e[2] for e in INDEX}
GRAM = {e[0]: e[3] for e in INDEX}
ENG = {e[0]: e[4] for e in INDEX}
INDECL_GRAM = {"", "adv.", "prep.", "conj.", "interj.", "adv., prep.", "indecl."}
BY_KEY = collections.defaultdict(list)
for i, (k, nk) in LSKEYS.items():
    BY_KEY[k].append(i)

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

WORKS = [
    {
        "id": "cesar-guerra-gaulesa", "arquivo": "phi0448/phi001/phi0448.phi001.perseus-lat2.xml",
        "autor": "César", "autorLa": "C. Iulius Caesar", "titulo": "A Guerra da Gália", "tituloLa": "Commentarii de Bello Gallico",
        "cts": "urn:cts:latinLit:phi0448.phi001",
        "edicao": "C. Iuli Caesaris Commentarii rerum in Gallia gestarum VII, A. Hirti commentarius VIII, ed. T. Rice Holmes. Oxford: Clarendon Press, 1914.",
        "edicaoCurta": "Rice Holmes, 1914", "referencia": "livro.capítulo.seção", "exemploRef": "1.1.1",
        "notaEdicao": "Os números à margem são as seções; os capítulos vêm em destaque. Cite como livro.capítulo.seção (1.1.1 = livro I, capítulo 1, seção 1). Entre ⟨ ⟩, palavras acrescentadas pelo editor. O livro VIII é de Aulo Hírcio.",
        "descricao": "Os comentários de César sobre as campanhas na Gália (58–51 a.C.): os helvécios e Ariovisto, os belgas, a Bretanha, a travessia do Reno e a grande revolta de Vercingetórix até Alésia. O livro VIII é de Aulo Hírcio.",
        "tipo": "caesar",
    },
    {
        "id": "cicero-catilinarias", "arquivo": "phi0474/phi013/phi0474.phi013.perseus-lat2.xml",
        "autor": "Cícero", "autorLa": "M. Tullius Cicero", "titulo": "Catilinárias", "tituloLa": "Orationes in Catilinam",
        "cts": "urn:cts:latinLit:phi0474.phi013",
        "edicao": "M. Tulli Ciceronis Orationes, vol. I, ed. Albert Curtis Clark. Oxford: Clarendon Press, 1905 (Oxford Classical Texts).",
        "edicaoCurta": "Clark, 1905", "referencia": "discurso.seção", "exemploRef": "1.1",
        "notaEdicao": "Os números à margem são as seções de cada discurso; cite como discurso.seção (1.1 = Primeira Catilinária, seção 1). As notas de aparato crítico da edição foram omitidas.",
        "descricao": "Os quatro discursos de Cícero, cônsul em 63 a.C., contra a conjuração de Catilina: “Quo usque tandem abutere, Catilina, patientia nostra?”, a saída de Catilina de Roma, as provas contra os conjurados e o debate sobre a pena.",
        "tipo": "cicero",
    },
    {
        "id": "virgilio-eneida", "arquivo": "phi0690/phi003/phi0690.phi003.perseus-lat2.xml",
        "autor": "Virgílio", "autorLa": "P. Vergilius Maro", "titulo": "Eneida", "tituloLa": "Aeneis",
        "cts": "urn:cts:latinLit:phi0690.phi003",
        "edicao": "Vergil, Bucolics, Aeneid, and Georgics, ed. J. B. Greenough. Boston: Ginn & Co., 1900.",
        "edicaoCurta": "Greenough, 1900", "referencia": "livro.verso", "exemploRef": "6.851",
        "notaEdicao": "Os números à margem são os versos, de cinco em cinco; cite como livro.verso (6.851). O campo “ir” aceita qualquer verso.",
        "descricao": "A epopeia de Eneias, da queda de Troia à guerra no Lácio: a tempestade e Cartago, Dido, a descida aos infernos, a chegada à Itália e o duelo com Turno. “Arma virumque cano…”",
        "tipo": "vergil",
    },
]

# ---------- análise ----------

WORD = re.compile(r"[A-Za-zÀ-ÿ]+")


def lookup(form):
    # palavra em maiúscula no início da frase (Cum, Circa): junta as análises da forma minúscula, que vêm
    # primeiro, às do nome próprio homógrafo (Cos, Circe)
    if form[:1].isupper() and not form.isupper():
        low = MORPH.get(form.lower(), [])
        cap = MORPH.get(form, [])
        if low or cap:
            return list(low) + [a for a in cap if a not in low]
    for f in (form, form.lower(), form[:1].upper() + form[1:].lower()):
        if f in MORPH:
            return MORPH[f]
    return None


ENCL = {"que": "que", "ne": "ne", "ve": "ve"}


def enclitic_id(enc):
    ids = BY_KEY.get(enc) or BY_KEY.get(enc + "1") or []
    if enc == "ne":
        # -ne interrogativo é ne3 no L&S (ne1 = não, ne2 = verdadeiramente)
        for k in ("ne3", "ne2", "ne1"):
            if BY_KEY.get(k):
                return BY_KEY[k][0]
    return ids[0] if ids else None


ENCL_ID = {e: enclitic_id(e) for e in ENCL}


def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower().replace("j", "i").replace("v", "u"))


BY_NORM = collections.defaultdict(list)
for i, (k, nk) in LSKEYS.items():
    BY_NORM[re.sub(r"\d+$", "", nk.replace(" ", ""))].append(i)


def resolve(lemma, lid):
    """verbete do L&S para um lema do Morpheus quando o deslocamento não é exato"""
    if lid and lid in LSKEYS:
        return lid
    base, _, n = lemma.partition("#")
    for k in ((base + n) if n else None, base, base + "1"):
        if k and BY_KEY.get(k):
            return BY_KEY[k][0]
    c = BY_NORM.get(norm(base))
    if c and (len(c) == 1 or not n):
        return c[0]
    if c and n and n.isdigit() and int(n) <= len(c):
        return c[int(n) - 1]
    return None


PRAENOMEN = {"A": "Aulus", "C": "Gaius", "Cn": "Gnaeus", "D": "Decimus", "L": "Lucius", "M": "Marcus",
             "Mam": "Mamercus", "N": "Numerius", "P": "Publius", "Q": "Quintus", "Ser": "Servius", "Sex": "Sextus",
             "Sp": "Spurius", "T": "Titus", "Ti": "Tiberius", "K": "Kaeso", "Kal": "Kalendae"}
# adjetivos ou nomes raros que nenhuma forma distingue de um substantivo comum (Gallia × Gallius)
PENALTY = {"Gallius#2": 0.05, "Gallius#1": 0.05, "Troius": 0.2, "germanus": 0.5}
# homógrafos raros (nomes próprios, verbos de sentido raro) que empatam com palavras comuns
ID_PENALTY = {"357": 0.05, "8091": 0.02, "11379": 0.02, "1895": 0.02, "43274": 0.02, "32866": 0.02,
              "37286": 0.02, "8085": 0.02, "12360": 0.3}
# na Suma, substantivos técnicos preferidos ao particípio ou verbo homógrafo (actus, habitus, intellectus…)
GROUP_BOOST = {"tomas-suma": {i: 20 for i in (
    "636", "20093", "24109", "29779", "3151", "15204", "42500", "18566", "37285", "32947", "11508",
    "37388", "32865", "43664", "45298", "49973", "356", "39974", "50588", "44684")}}
ROMAN_RE = re.compile(r"^(M{0,4})(CM|CD|D?C{0,4})(XC|XL|L?X{0,4})(IX|IV|V?I{0,4})$")
RV = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}


def roman(s):
    if not s or not ROMAN_RE.match(s):
        return None
    t = 0
    for i, ch in enumerate(s):
        v = RV[ch]
        t += -v if i + 1 < len(s) and RV[s[i + 1]] > v else v
    return t


def analyze(form, nxt=""):
    """[(lema, id, análise)] — com tentativa de separar -que, -ne, -ve; nxt = texto logo depois da palavra"""
    out = [(l, resolve(l, i), m) for l, i, m in _analyze(form, nxt)]
    # partículas compostas com verbete próprio no L&S (itaque, namque), que o Morpheus decompõe
    k = form.lower()
    if out and BY_KEY.get(k) and len(BY_KEY[k]) == 1 and BY_KEY[k][0] not in {i for _, i, _ in out}:
        ind = [m for _, _, m in out if m.startswith("indeclform")]
        if ind:
            out.insert(0, (k, BY_KEY[k][0], ind[0]))
    # palavras invariáveis do L&S que o Morpheus não oferece (circa "ao redor"; cum "quando"):
    # entram primeiro se as outras análises forem só formas verbais de 1ª/2ª pessoa ou imperativos
    if out:
        have = {i for _, i, _ in out}
        extra = []
        for key in [k] + [k + str(n) for n in range(1, 5)]:
            for i in BY_KEY.get(key, []):
                if i not in have and GRAM.get(i, "x") in INDECL_GRAM and ENG.get(i):
                    kind = {"adv.": "adverb", "prep.": "prep", "conj.": "conj", "interj.": "exclam"}.get(GRAM.get(i, ""), "indecl")
                    extra.append((HEAD.get(i, key), i, f"indeclform ({kind}) ls"))
        if extra:
            if all(re.search(r"imperat|1st|2nd", m) for _, _, m in out):
                out = extra + out
            else:
                out = out + extra
    return out


def _analyze(form, nxt):
    if nxt.startswith(".") and form in PRAENOMEN:
        full = PRAENOMEN[form]
        an = lookup(full)
        if an:
            return [(a[0], a[1], "abbreviation") for a in an[:1]]
        return [(full, None, "abbreviation")]
    if nxt.startswith(".") and form in LM.CITACAO:
        return [(LM.CITACAO[form], None, "citation")]
    if form.lower() in LM.COMPOSTOS:
        return _medieval(form)
    if form.isupper() and (len(form) > 1 or nxt[:1] in (" ", ",", ".", "")) and roman(form):
        return [(str(roman(form)), None, "roman")]
    plain = unicodedata.normalize("NFD", form)
    plain = unicodedata.normalize("NFC", "".join(c for c in plain if c not in "\u0308\u0301\u0300\u0302"))
    for f in dict.fromkeys((form, plain)):
        an = lookup(f)
        if an:
            return list(an)
        for enc in ("que", "ne", "ve"):
            if f.lower().endswith(enc) and len(f) > len(enc) + 1:
                base = lookup(f[: -len(enc)])
                if base:
                    return list(base) + [("-" + enc, ENCL_ID[enc], "enclitic")]
        for g in (f.replace("j", "i").replace("J", "I"), f.replace("v", "u").replace("V", "U")):
            if g != f:
                an = lookup(g)
                if an:
                    return list(an)
    return _medieval(form)


def _ls_id(key):
    ids = BY_KEY.get(key) or BY_KEY.get(key + "1") or BY_NORM.get(norm(key)) or []
    return ids[0] if ids else None


def _medieval(form):
    """formas que o Morpheus não reconhece: compostos, grafias medievais, verbetes só do L&S"""
    low = form.lower()
    if low in LM.COMPOSTOS:
        return [(lem, _ls_id(key), "compound" + (":" + lab if lab else "")) for lem, key, lab in LM.COMPOSTOS[low]]
    for v in LM.variantes(form):
        an = lookup(v)
        if an:
            return list(an)
        for enc in ("que", "ne", "ve"):
            if v.lower().endswith(enc) and len(v) > len(enc) + 1:
                base = lookup(v[: -len(enc)])
                if base:
                    return list(base) + [("-" + enc, ENCL_ID[enc], "enclitic")]
    cands = [form] + LM.variantes(form)
    for c in cands:
        ids = BY_NORM.get(norm(c)) if len(c) >= 3 else None
        if ids:
            return [(HEAD.get(i, c), i, "lsonly") for i in ids[:2]]
    if len(form) >= 5:
        for c in cands:
            for g in LM.flexao_candidatas(c):
                ids = BY_NORM.get(norm(g))
                if ids:
                    return [(HEAD.get(ids[0], g), ids[0], "guess")]
    return []


# ---------- leitura do TEI ----------

class Doc:
    def __init__(self):
        self.blocks = []          # [{"t": "c"|"p", ...}]
        self.cur = None           # parágrafo aberto: lista x
        self.tokens = []          # referências (bloco, índice) dos itens-palavra

    def heading(self, ref, rot, chip, lv):
        self.close()
        self.blocks.append({"t": "c", "c": ref, "rot": rot, "chip": chip, "lv": lv})

    def para(self):
        self.close()
        self.cur = []

    def close(self):
        if self.cur:
            # junta textos vizinhos
            x = []
            for it in self.cur:
                if isinstance(it, str) and x and isinstance(x[-1], str):
                    x[-1] += it
                else:
                    x.append(it)
            if x and isinstance(x[0], str):
                x[0] = x[0].lstrip()
            if x and isinstance(x[-1], str):
                x[-1] = x[-1].rstrip()
            self.blocks.append({"t": "p", "x": [i for i in x if i != ""]})
        self.cur = None

    def text(self, s, abbr_of=None):
        if self.cur is None:
            self.cur = []
        s = re.sub(r"\s+", " ", s)
        if abbr_of is not None:
            # abreviatura de prenome (C. = Gaius): a palavra mostrada é a abreviatura,
            # a análise é a da forma por extenso
            self.cur.append(["W", s, abbr_of])
            return
        pos = 0
        for m in WORD.finditer(s):
            if m.start() > pos:
                self.cur.append(s[pos:m.start()])
            self.cur.append(["W", m.group(0), None])
            pos = m.end()
        if pos < len(s):
            self.cur.append(s[pos:])

    def mark(self, obj):
        if self.cur is None:
            self.cur = []
        self.cur.append(obj)


def walk_inline(el, doc):
    """conteúdo de um <p> ou <l>: texto e elementos em linha"""
    def rec(e, top=False):
        tag = etree.QName(e).localname if isinstance(e.tag, str) else ""
        if not top:
            if tag in ("note", "gap", "expan", "rdg", "sic", "pb", "lb", "figure"):
                doc.text(" " if tag == "gap" else "")
                return
            if tag == "milestone":
                return
            if tag == "choice":
                ab = e.find("{*}abbr")
                ex = e.find("{*}expan")
                cor = e.find("{*}corr")
                if ab is not None and ex is not None:
                    full = "".join(ex.itertext()).strip()
                    doc.text("".join(ab.itertext()).strip(), abbr_of=full)
                    return
                if cor is not None:
                    rec(cor)
                    return
            if tag == "add":
                doc.text("⟨")
            if tag == "del":
                doc.text("[")
        if e.text and not (tag in ("choice", "app") and not top):
            doc.text(e.text)
        for ch in e:
            rec(ch)
            if ch.tail:
                doc.text(ch.tail)
        if not top:
            if tag == "add":
                doc.text("⟩")
            if tag == "del":
                doc.text("]")
    rec(el, True)


def divs(el, sub):
    return [d for d in el.iter("{*}div") if d.get("subtype") == sub and d.get("n") and d.get("type") == "textpart"]


def build_caesar(root, doc):
    for b in divs(root, "book"):
        bn = b.get("n")
        doc.heading(bn, f"Livro {ROMAN[int(bn)]}", ROMAN[int(bn)], 0)
        for c in [d for d in b if isinstance(d.tag, str) and d.get("subtype") == "chapter"]:
            cn = c.get("n")
            doc.heading(f"{bn}.{cn}", f"Capítulo {cn}", cn, 1)
            doc.para()
            for s in [d for d in c if isinstance(d.tag, str) and d.get("subtype") == "section"]:
                sn = s.get("n")
                doc.mark({"s": f"{bn}.{cn}.{sn}", "d": sn})
                for p in s.iter("{*}p"):
                    walk_inline(p, doc)
                    doc.text(" ")
            doc.close()


SPEECH = {"1": "Primeira Catilinária", "2": "Segunda Catilinária", "3": "Terceira Catilinária", "4": "Quarta Catilinária"}


def build_cicero(root, doc):
    for sp in divs(root, "speech"):
        n = sp.get("n")
        doc.heading(n, SPEECH[n], ROMAN[int(n)], 0)
        head = sp.find("{*}head")
        if head is not None:
            doc.blocks.append({"t": "h", "x": ["".join(head.itertext()).strip()]})
        for s in divs(sp, "section"):
            sn = s.get("n")
            doc.para()
            doc.mark({"s": f"{n}.{sn}", "d": sn})
            for p in s.iter("{*}p"):
                walk_inline(p, doc)
                doc.text(" ")
            doc.close()


def build_vergil(root, doc):
    for b in divs(root, "book"):
        bn = b.get("n")
        doc.heading(bn, f"Livro {ROMAN[int(bn)]}", ROMAN[int(bn)], 0)
        doc.para()
        first = True
        for e in b.iter("{*}l", "{*}milestone"):
            tag = etree.QName(e).localname
            if tag == "milestone":
                if e.get("unit") in ("card", "para") and not first:
                    doc.close()
                    doc.para()
                continue
            ln = e.get("n")
            if not first and doc.cur:
                doc.mark({"br": 1})
            first = False
            vis = ln.isdigit() and int(ln) % 5 == 0
            doc.mark({"s": f"{bn}.{ln}", "d": ln if vis else "", "k": "ln"})
            walk_inline(e, doc)
        doc.close()


# ---------- montagem ----------

OBRAS = [{
    "id": summa.OBRA, "autor": "Tomás de Aquino", "autorLa": "S. Thomas de Aquino",
    "titulo": "Suma Teológica", "tituloLa": "Summa Theologiae", "edicaoCurta": "Leonina",
    "descricao": "A suma da teologia de Tomás de Aquino (1265–1273), em questões e artigos: Deus e a criação (I), "
                 "o fim do homem, os atos humanos, as virtudes, a lei e a graça (I-II, II-II), Cristo e os sacramentos (III). "
                 "Texto completo das partes escritas por Tomás, dividido por tratados.",
}]


def build(work):
    if work["tipo"] == "summa":
        doc = Doc()
        summa.build_summa(work, doc)
        doc.close()
        return doc
    path = os.path.join(SRC, work["arquivo"])
    root = etree.parse(path, etree.XMLParser(remove_blank_text=False, recover=True)).getroot()
    body = root.find(".//{*}body")
    doc = Doc()
    {"caesar": build_caesar, "cicero": build_cicero, "vergil": build_vergil}[work["tipo"]](body, doc)
    doc.close()
    return doc


def main():
    works = WORKS + (summa.works(SUMMA) if SUMMA else [])
    docs = [(w, build(w)) for w in works]

    # frequência dos lemas no conjunto dos textos, estimada por EM: cada palavra ambígua divide sua
    # ocorrência entre os lemas possíveis na proporção da frequência atual de cada um. O ponto de partida
    # é o tamanho do verbete no L&S (palavras comuns têm verbetes longos), o que desempata casos como
    # Gallia (substantivo) × Gallius (adjetivo), que nenhuma forma distingue.
    size = {}
    for fn in sorted(os.listdir(os.path.join(OUT, "data", "ls"))):
        for k, v in json.load(open(os.path.join(OUT, "data", "ls", fn), encoding="utf-8")).items():
            size[k] = len(v)
    occ = []
    for wk_, d in docs:
        grp = wk_.get("grupo", "classicos")
        for b in d.blocks:
            x = b.get("x", [])
            for j, it in enumerate(x):
                if isinstance(it, list) and it[0] == "W":
                    nxt = x[j + 1] if j + 1 < len(x) and isinstance(x[j + 1], str) else ""
                    it.append(nxt)
                    an = analyze(it[2] or it[1], nxt)
                    lems = sorted({(a[0], a[1]) for a in an if not a[0].startswith("-") and a[2] not in ("roman",)})
                    if lems:
                        occ.append((grp, lems))
    import math
    freq = collections.Counter()
    prior = {}
    for _, lems in occ:
        for l in lems:
            prior[l] = math.log(2 + size.get(l[1] or "", 0))
    # peso de cada lema: ocorrências não ambíguas nos textos + um pouco das ambíguas + tamanho do verbete.
    # (Um EM puro concentra a massa em verbos raros que aparecem em muitas posições ambíguas: ito "ir"
    # absorvia ita, itaque, item, iter.)
    # Os pesos são calculados por grupo (os clássicos juntos; a Suma à parte), para que o vocabulário
    # escolástico não altere a ordem das análises em César, Cícero e Virgílio, e vice-versa.
    W = {}
    for g in sorted({g for g, _ in occ}):
        unamb = collections.Counter()
        shared = collections.Counter()
        for gg, lems in occ:
            if gg != g:
                continue
            if len(lems) == 1:
                unamb[lems[0]] += 1
            else:
                for l in lems:
                    shared[l] += 1 / len(lems)
        W[g] = {l: unamb[l] + 0.1 * shared[l] + 0.2 * prior[l] for l in prior}

    os.makedirs(os.path.join(OUT, "textos"), exist_ok=True)
    meta_list = []
    vocab = collections.Counter()   # id do L&S -> ocorrências (para priorizar a tradução PT)
    vocab_g = collections.defaultdict(collections.Counter)
    for wk, d in docs:
        grp = wk.get("grupo", "classicos")
        w = W[grp]
        lemas, lem_ix = [], {}
        morfs, morf_ix = [], {}

        def morf_index(m):
            if m not in morf_ix:
                morf_ix[m] = len(morfs)
                morfs.append(m)
            return morf_ix[m]
        words = total = miss = 0

        def lem_index(lemma, lid):
            key = (lemma, lid)
            if key not in lem_ix:
                name = HEAD.get(lid) if lid else None
                lem_ix[key] = len(lemas)
                lemas.append([name or re.sub(r"#\d+$", "", lemma), lid or ""])
            return lem_ix[key]

        for b in d.blocks:
            if "x" not in b:
                continue
            nx = []
            for it in b["x"]:
                if isinstance(it, list) and it[0] == "W":
                    form, full, nxt = it[1], it[2], it[3]
                    an = analyze(full or form, nxt)
                    total += 1
                    if not an:
                        miss += 1
                    # agrupa por lema, ordena pela frequência
                    groups = collections.OrderedDict()
                    for lemma, lid, m in an:
                        groups.setdefault((lemma, lid), []).append(m)
                    # sem verbete no L&S (omnes, omne…): só fica se nenhum lema da palavra tiver verbete
                    if any(i for (l, i) in groups if not l.startswith("-")):
                        groups = collections.OrderedDict((k, v) for k, v in groups.items() if k[1])
                    fn = norm(form)

                    def score(kv):
                        (l, i), ms = kv
                        sc = w.get((l, i), 0)
                        # a própria forma é a de dicionário (ita, sine, nisi, iter, castra): forte indício
                        first = False
                        if i and LSKEYS.get(i) and re.sub(r"\d+$", "", LSKEYS[i][1]) == fn:
                            if any(m.startswith("indeclform") and "exclam" not in m and not m.endswith(" ls") for m in ms):
                                sc *= 10           # palavra invariável cuja forma é a própria entrada (sine, ita)
                            elif any("nom" in m for m in ms):
                                sc *= 3            # nominativo igual à entrada (castra, iter)
                        sc *= PENALTY.get(l, 1) * ID_PENALTY.get(i or "", 1)
                        sc *= GROUP_BOOST.get(grp, {}).get(i or "", 1)
                        # texto expositivo em 3ª pessoa: formas só de 1ª/2ª pessoa ou imperativo são improváveis
                        if grp == "tomas-suma" and all(re.search(r"imperat|1st|2nd", m) for m in ms):
                            sc *= 0.05
                        return (l.startswith("-"), not first, -sc)
                    order = sorted(groups.items(), key=score)
                    item = [form, [[lem_index(l, i), morf_index("|".join(dict.fromkeys(ms)))] for (l, i), ms in order]]
                    if order and order[0][0][1]:
                        vocab[order[0][0][1]] += 1
                        vocab_g[wk.get("grupo", "classicos")][order[0][0][1]] += 1
                    nx.append(item)
                else:
                    nx.append(it)
            b["x"] = nx
        meta = {k: wk[k] for k in ("id", "autor", "autorLa", "titulo", "tituloLa", "cts", "edicao", "edicaoCurta",
                                  "referencia", "exemploRef", "notaEdicao", "descricao")}
        meta["fonteTexto"] = wk.get("fonteTexto") or {
            "nome": "Perseus Digital Library (canonical-latinLit)",
            "url": "https://github.com/PerseusDL/canonical-latinLit/blob/master/data/" + wk["arquivo"],
            "licenca": "CC BY-SA 4.0"}
        OBRA_KEYS = ("obra", "pars", "parsLa", "parsPt", "qmin", "qmax", "tratado")
        meta |= {k: wk[k] for k in OBRA_KEYS if k in wk}
        meta["fonteAnotacao"] = {"nome": "Morpheus (Perseus Digital Library), via dados do Diogenes",
                                 "url": "https://github.com/perseids-tools/morpheus", "licenca": "ver LICENSE-DATA.md",
                                 "nota": "Análise por consulta de formas, sem desambiguação pelo contexto: todas as análises possíveis são mostradas, a mais provável primeiro."}
        nlem = len(lemas)
        sem = sum(1 for l in lemas if not l[1])
        out = {"id": wk["id"], "meta": meta, "lemas": lemas, "morfs": morfs, "blocos": d.blocks,
               "estat": {"palavras": total, "sem_analise": miss, "lemas": nlem, "lemas_sem_verbete": sem}}
        s = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
        with open(os.path.join(OUT, "textos", wk["id"] + ".json"), "w", encoding="utf-8") as f:
            f.write(s)
        ver = hashlib.sha1(s.encode()).hexdigest()[:10]
        meta_list.append({k: wk[k] for k in ("id", "autor", "autorLa", "titulo", "tituloLa", "descricao", "edicaoCurta")}
                         | {k: wk[k] for k in OBRA_KEYS if k in wk} | {"palavras": total, "versao": ver})
        print(f"{wk['id']}: {total} palavras, {miss} sem análise ({miss / total:.1%}), {nlem} lemas, {sem} sem verbete")
    with open(os.path.join(OUT, "textos", "index.json"), "w", encoding="utf-8") as f:
        obras = []
        for o in OBRAS:
            parts = [t for t in meta_list if t.get("obra") == o["id"]]
            if parts:
                obras.append(o | {"palavras": sum(t["palavras"] for t in parts)})
        json.dump({"textos": meta_list, "obras": obras}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "vocab_textos.json"), "w", encoding="utf-8") as f:
        json.dump(vocab.most_common(), f)
    with open(os.path.join(HERE, "vocab_grupos.json"), "w", encoding="utf-8") as f:
        json.dump({g: c.most_common() for g, c in vocab_g.items()}, f)


def build_forms():
    """formas flexionadas -> verbetes, para a busca (amabant → amo): {id: "forma forma …"}"""
    by_id = collections.defaultdict(set)
    for form, an in MORPH.items():
        f = norm(form)
        if not f:
            continue
        for lemma, lid, m in an:
            i = resolve(lemma, lid)
            if i and norm(re.sub(r"\d+$", "", LSKEYS[i][1])) != f:
                by_id[i].add(f)
    out = {i: " ".join(sorted(fs)) for i, fs in by_id.items()}
    with open(os.path.join(OUT, "data", "formas.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))
    print("formas para a busca:", sum(len(v) for v in by_id.values()), "em", len(out), "verbetes")


if __name__ == "__main__":
    main()
    build_forms()
