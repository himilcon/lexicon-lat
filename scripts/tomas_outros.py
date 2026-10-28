"""Summa contra Gentiles e De ente et essentia, de Tomás de Aquino, para o leitor do Lexicon.

Fonte: coluna latina das páginas bilíngues de https://github.com/Geremia/AquinasOperaOmnia (espelho do
site de Joseph Kenny, O.P.): ContraGentiles1–4.htm e DeEnte&Essentia.htm. O latim é o da edição leonina
(SCG) e o da edição leonina, t. 43 (De ente); a transcrição digital é, ao que tudo indica, a do Corpus
Thomisticum, mas o repositório não o declara.
"""
import os
import re

import lxml.html as LH

SCG = "tomas-scg"
MAX_WORDS = 40000
LIVROS = [("I", "1", "ContraGentiles1.htm", 102, "Liber primus", "Livro I",
           "Deus em si mesmo", "O ofício do sábio e o método da obra; a existência de Deus e seus atributos: eternidade, simplicidade, perfeição, bondade, unidade, infinidade; o conhecimento, a vontade, o amor e a bem-aventurança de Deus."),
          ("II", "2", "ContraGentiles2.htm", 101, "Liber secundus", "Livro II",
           "A criação", "O poder de Deus e a criação; a distinção das criaturas; as substâncias intelectuais e a alma humana, sua união com o corpo e sua imortalidade."),
          ("III", "3", "ContraGentiles3a.htm ContraGentiles3b.htm", 163, "Liber tertius", "Livro III",
           "A providência", "Deus como fim de todas as coisas; a felicidade do homem na visão de Deus; o governo divino do mundo, o destino, os milagres, a lei divina, a graça."),
          ("IV", "4", "ContraGentiles4.htm", 97, "Liber quartus", "Livro IV",
           "As verdades reveladas", "A Trindade, a Encarnação, os sacramentos, a ressurreição e o juízo: o que só se conhece pela revelação.")]


def _clean(t):
    return re.sub(r"\s+", " ", t).strip()


def _trows(path):
    d = LH.parse(path).getroot()
    out = []
    for r in d.xpath("//tr"):
        tds = r.xpath("./td")
        if len(tds) == 2:
            out.append((_clean(tds[0].text_content()), _clean(tds[1].text_content())))
    return out


def _is_title(en):
    if re.match(r"\[\d", en):
        return False
    letters = [c for c in en if c.isalpha()]
    return len(letters) > 3 and sum(c.isupper() for c in letters) / len(letters) > 0.8


def scg_chapters(src, files):
    """[(capítulo ou 'prol', título latino, [(rótulo, latim)])]"""
    caps = []
    for fn in files.split():
        rows = _trows(os.path.join(src, fn))[1:]     # a primeira linha de cada arquivo é o sumário
        for la, en in rows:
            if not la and not en:
                continue
            m = re.match(r"Caput (\d+)\b\.?\s*(.*)", la)
            me = re.match(r"Chapter (\d+)\b", en)
            cur = caps[-1] if caps else None
            if m or me:
                num = int(m.group(1) if m else me.group(1))
                tit = m.group(2) if m else la
                if cur and cur[0] == num and not cur[2]:
                    cur[1] = cur[1] or tit
                else:
                    caps.append([num, tit, []])
                continue
            mc = re.search(r"\[Chapter (\d+)\]", en)
            if mc and cur and cur[0] != int(mc.group(1)):
                caps.append([int(mc.group(1)), "", []])  # capítulos fundidos na fonte ("Chapters 51-52")
                cur = caps[-1]
            if _is_title(en) and cur and cur[2] and cur[0] != "prol":
                caps.append([cur[0] + 1, la, []])     # linha "Caput N" ausente na fonte
                continue
            if not la:
                continue
            if not caps:
                caps.append(["prol", "", []])
                cur = caps[-1]
            if not cur[1] and not cur[2] and cur[0] != "prol" and _is_title(en):
                cur[1] = la
                continue
            n = re.match(r"\[(\d+)\]", en)
            cur[2].append((n.group(1) if n else "", la))
    return caps


def _nw(caps):
    return sum(len(re.findall(r"[A-Za-z]+", t)) for c in caps for _, t in c[2]) + \
        sum(len(re.findall(r"[A-Za-z]+", c[1])) for c in caps)


FONTE = {"nome": "AquinasOperaOmnia (espelho do site de Joseph Kenny, O.P.), coluna latina",
         "licenca": "texto em domínio público; transcrição digital sem licença declarada (ver LICENSE-DATA.md)"}


def works(src):
    out = []
    for sig, num, files, ncap, la, pt, tema, desc in LIVROS:
        caps = scg_chapters(src, files)
        total = _nw(caps)
        nchunks = max(1, -(-total // MAX_WORDS))
        target = total / nchunks
        chunks, cur, acc = [], [], 0
        for c in caps:
            n = _nw([c])
            if cur and acc + n / 2 > target * (len(chunks) + 1):
                chunks.append(cur)
                cur = []
            cur.append(c)
            acc += n
        chunks.append(cur)
        for k, cs in enumerate(chunks):
            nums = [c[0] for c in cs if c[0] != "prol"]
            a, b = nums[0], nums[-1]
            rng = f"c. {a}" if a == b else f"cc. {a}–{b}"
            parte = f" ({k + 1}/{len(chunks)})" if len(chunks) > 1 else ""
            out.append({
                "id": f"{SCG}-{num}-c{a:03d}", "tipo": "scg", "grupo": "tomas-suma", "obra": SCG,
                "pars": sig, "parsLa": la, "parsPt": pt, "qmin": a if cs[0][0] != "prol" else 0, "qmax": b,
                "tratado": tema + parte, "caps": cs, "livro": num,
                "autor": "Tomás de Aquino", "autorLa": "S. Thomas de Aquino",
                "titulo": f"Suma contra os Gentios, {sig}, {rng}", "tituloLa": f"Summa contra Gentiles, {la}, {rng}",
                "cts": "", "edicao": "Textus Leoninus: Sancti Thomae Aquinatis Opera omnia iussu Leonis XIII P. M. edita, t. 13–15 (Romae, 1918–1930).",
                "edicaoCurta": "Leonina", "referencia": "livro.capítulo", "exemploRef": f"{num}.{a}",
                "notaEdicao": "Os números à margem são os dos parágrafos de cada capítulo. Cite como livro.capítulo (3.65) ou com o livro em romanos: III, 65.",
                "descricao": desc,
                "rotPartes": "Capítulos", "obraTitulo": "Suma contra os Gentios",
                "fonteTexto": FONTE | {"url": "https://github.com/Geremia/AquinasOperaOmnia/blob/master/" + files.split()[0]}})
    return out


def build_scg(work, doc):
    num = work["livro"]
    for c, tit, pars in work["caps"]:
        if c == "prol":
            doc.heading(f"{num}.prol", "Prooemium", "Pr.", 0)
        else:
            doc.heading(f"{num}.{c}", f"Caput {c}", str(c), 0)
        if tit:
            doc.para()
            doc.mark({"lab": "tít."})
            doc.text(tit)
            doc.close()
        for lab, la in pars:
            doc.para()
            if lab:
                doc.mark({"lab": lab})
            doc.text(la)
            doc.close()


# ---------- De ente et essentia ----------

DEENTE = {
    "id": "tomas-de-ente", "tipo": "deente", "grupo": "tomas-suma",
    "autor": "Tomás de Aquino", "autorLa": "S. Thomas de Aquino",
    "titulo": "O ente e a essência", "tituloLa": "De ente et essentia",
    "cts": "", "edicao": "Textus Leoninus: Sancti Thomae de Aquino Opera omnia iussu Leonis XIII P. M. edita, t. 43 (Romae, 1976).",
    "edicaoCurta": "Leonina", "referencia": "capítulo", "exemploRef": "4",
    "notaEdicao": "Os números à margem são os parágrafos na numeração corrente das traduções (1–…).",
    "descricao": "Opúsculo da juventude de Tomás (c. 1252–1256), escrito para os confrades: o que significam “ente” e “essência”, "
                 "e como a essência se encontra nas substâncias compostas, nas substâncias separadas e nos acidentes. "
                 "Contém a distinção entre essência e ser (esse).",
    "rotPartes": "Capítulos",
    "fonteTexto": FONTE | {"url": "https://github.com/Geremia/AquinasOperaOmnia/blob/master/DeEnte%26Essentia.htm"},
}


def build_deente(src, doc):
    rows = _trows(os.path.join(src, "DeEnte&Essentia.htm"))
    for la, en in rows:
        if not la:
            continue
        m = re.match(r"(Prooemium|Caput (\d+))\s*(.*)", la)
        if m:
            if m.group(2):
                doc.heading(m.group(2), f"Caput {m.group(2)}", m.group(2), 0)
            else:
                doc.heading("prol", "Prooemium", "Pr.", 0)
            la = m.group(3)
        n = re.match(r"(\d+)\.", en)
        doc.para()
        if n:
            doc.mark({"lab": n.group(1)})
        doc.text(la)
        doc.close()
