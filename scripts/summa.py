"""Suma Teológica de Tomás de Aquino para o leitor do Lexicon.

Fonte do texto latino: coluna latina das páginas bilíngues de https://github.com/Geremia/AquinasOperaOmnia
(espelho do site de Joseph Kenny, O.P., dhspriory.org/thomas), pasta summa/. O texto segue a edição
leonina; a transcrição digital é, ao que tudo indica, a do Corpus Thomisticum (E. Alarcón, Universidad
de Navarra), mas o repositório não o declara.

A obra é dividida em arquivos de no máximo ~MAX_WORDS palavras, respeitando os tratados, para que o leitor
não precise baixar 1,5 milhão de palavras de uma vez. Cada arquivo é um "texto" da biblioteca com
obra = "tomas-suma"; a biblioteca agrupa todos num cartão só.
"""
import os
import re

import lxml.html as LH

OBRA = "tomas-suma"
MAX_WORDS = 40000

PARS = {
    "FP": ("I", "Prima Pars", "Primeira Parte"),
    "FS": ("I-II", "Prima Secundae", "Primeira Seção da Segunda Parte"),
    "SS": ("II-II", "Secunda Secundae", "Segunda Seção da Segunda Parte"),
    "TP": ("III", "Tertia Pars", "Terceira Parte"),
}

# (pars, q inicial, q final, tratado, descrição)
TRATADOS = [
    ("FP", 1, 1, "A doutrina sagrada", "Natureza e extensão da sacra doctrina: se é necessária, se é ciência, seu objeto, o uso da autoridade e os sentidos da Escritura."),
    ("FP", 2, 26, "Deus: a essência divina", "A existência de Deus (as cinco vias), a simplicidade, a perfeição, a bondade, a infinidade, a eternidade e a unidade de Deus; os nomes divinos, a ciência, a vontade, a providência e o poder de Deus."),
    ("FP", 27, 43, "A Santíssima Trindade", "As processões e relações divinas, as Pessoas do Pai, do Filho e do Espírito Santo, a igualdade e as missões das Pessoas."),
    ("FP", 44, 49, "A criação", "A primeira causa dos seres, o modo da criação, o início da duração das criaturas, a distinção das coisas e a questão do mal."),
    ("FP", 50, 64, "Os anjos", "A natureza dos anjos, seu conhecimento e sua vontade, sua criação, a queda dos demônios."),
    ("FP", 65, 74, "A obra dos seis dias", "Comentário ao relato da criação no Gênesis, dia por dia."),
    ("FP", 75, 102, "O homem", "A alma humana e sua união com o corpo, as potências da alma, o intelecto e o conhecimento, a criação do primeiro homem e o estado de inocência."),
    ("FP", 103, 119, "O governo das criaturas", "O governo divino do mundo, a ação das criaturas umas sobre as outras, os anjos e os demônios, os corpos celestes, a propagação do homem."),
    ("FS", 1, 5, "O fim último e a bem-aventurança", "O fim último do homem e em que consiste a felicidade; como se alcança."),
    ("FS", 6, 21, "Os atos humanos", "O voluntário e o involuntário, as circunstâncias, a vontade e a intenção, a escolha, a bondade e a malícia dos atos."),
    ("FS", 22, 48, "As paixões", "As paixões da alma em geral e em particular: amor e ódio, desejo, prazer e dor, esperança, temor, audácia, ira."),
    ("FS", 49, 54, "Os hábitos", "A natureza dos hábitos, seu sujeito, sua causa, seu aumento e sua diminuição."),
    ("FS", 55, 70, "As virtudes", "As virtudes intelectuais, morais e teologais; os dons do Espírito Santo, as bem-aventuranças e os frutos."),
    ("FS", 71, 89, "Os vícios e os pecados", "A natureza e a distinção dos pecados, suas causas, o pecado original, os efeitos do pecado, o pecado venial e o mortal."),
    ("FS", 90, 108, "A lei", "A essência da lei; a lei eterna, natural e humana; a lei antiga e a lei nova."),
    ("FS", 109, 114, "A graça", "A necessidade, a essência, a divisão e a causa da graça; a justificação e o mérito."),
    ("SS", 1, 16, "A fé", "O objeto e o ato da fé, a virtude da fé, os dons de entendimento e de ciência, a infidelidade, a heresia e a apostasia."),
    ("SS", 17, 22, "A esperança", "A virtude da esperança, o dom do temor, o desespero e a presunção."),
    ("SS", 23, 46, "A caridade", "A caridade em si, seu objeto e sua ordem, seus atos e efeitos, os vícios opostos; o dom da sabedoria."),
    ("SS", 47, 56, "A prudência", "A prudência em si, suas partes, o dom do conselho e os vícios opostos."),
    ("SS", 57, 122, "A justiça", "O direito e a justiça, a justiça distributiva e comutativa, os vícios contra ela; as virtudes anexas: religião, piedade, observância, gratidão, veracidade, liberalidade."),
    ("SS", 123, 140, "A fortaleza", "A fortaleza, o martírio, os vícios opostos; magnanimidade, magnificência, paciência e perseverança; o dom de fortaleza."),
    ("SS", 141, 170, "A temperança", "A temperança e suas partes: abstinência, sobriedade, castidade, virgindade; mansidão, clemência, modéstia, humildade, estudiosidade."),
    ("SS", 171, 178, "A profecia e as graças carismáticas", "A profecia, o arrebatamento, o dom de línguas, a graça da palavra e o dom dos milagres."),
    ("SS", 179, 182, "A vida ativa e a vida contemplativa", "A divisão da vida em ativa e contemplativa e a comparação entre elas."),
    ("SS", 183, 189, "Os estados de vida", "Os estados de perfeição: o episcopado e a vida religiosa."),
    ("TP", 1, 26, "O mistério da Encarnação", "A conveniência da Encarnação, a união hipostática, a natureza assumida, a graça e a ciência de Cristo, as consequências da união."),
    ("TP", 27, 59, "A vida de Cristo", "Maria, a concepção e o nascimento de Cristo, o batismo, a vida pública, a paixão, a morte, a ressurreição e a ascensão."),
    ("TP", 60, 65, "Os sacramentos em geral", "A natureza dos sacramentos, sua necessidade, seus efeitos (graça e caráter), sua causa e seu número."),
    ("TP", 66, 72, "O batismo e a confirmação", "O sacramento do batismo e o da confirmação."),
    ("TP", 73, 83, "A Eucaristia", "O sacramento da Eucaristia: a matéria, a conversão do pão e do vinho, a presença de Cristo, os efeitos e o rito."),
    ("TP", 84, 90, "A penitência", "O sacramento da penitência e a virtude da penitência. Aqui termina a obra de Tomás, interrompida em 1273."),
]

ORD = {w: i for i, w in enumerate("primum secundum tertium quartum quintum sextum septimum octavum nonum decimum "
                                  "undecimum duodecimum".split(), 1)}


def _rows(path):
    """[(latim, rótulo inglês)] de cada linha bilíngue"""
    d = LH.parse(path).getroot()
    out = []
    for r in d.xpath("//tr"):
        tds = r.xpath("./td")
        if len(tds) != 2:
            continue
        lat = re.sub(r"\s+", " ", tds[0].text_content()).strip()
        b = tds[1].xpath(".//b")
        lab = re.sub(r"\s+", " ", b[0].text_content()).strip() if b else ""
        if lat:
            out.append((lat, lab))
    return out


# Fonte complementar para as questões que faltam na coluna latina do AquinasOperaOmnia (17 questões,
# sobretudo da II-II): Markdown por artigo de https://github.com/AnthropologieBiblique/SummaTheologiae
# (mesmo texto leonino, do Corpus Thomisticum). Os rótulos são convertidos para os da fonte principal.
MD_SRC = None
MD_PARS = {"FP": ("Prima Pars", "Ia"), "FS": ("Prima Secundae", "Ia-IIæ"),
           "SS": ("Secunda Secundae", "IIa-IIæ"), "TP": ("Tertia Pars", "IIIa")}
LIVROS = {"Ac": "Act.", "Ap": "Apoc.", "Col": "Coloss.", "Ct": "Cant.", "Dn": "Dan.", "Dt": "Deut.",
          "Ep": "Ephes.", "Est": "Esth.", "Ex": "Exod.", "Ez": "Ezech.", "Ga": "Gal.", "Gn": "Gen.",
          "He": "Heb.", "Is": "Isaiae", "Jb": "Iob", "Jc": "Iac.", "Jdt": "Iudith", "Jn": "Ioan.",
          "Jr": "Ierem.", "Lc": "Luc.", "Mc": "Marc.", "Ml": "Malach.", "Mt": "Matth.", "Os": "Osee",
          "Ph": "Philipp.", "Pr": "Prov.", "Ps": "Psalm.", "Qo": "Eccle.", "Rm": "Rom.", "Sg": "Sap.",
          "Si": "Eccli.", "Tt": "Tit."}


def _roman(n):
    out = ""
    for v, r in ((100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += r
            n -= v
    return out


def _md_clean(t):
    def link(m):
        x = m.group(1).split("|")[-1]
        b = re.fullmatch(r"(\w+) (\d+)", x)
        if b and b.group(1) in LIVROS:
            return f"{LIVROS[b.group(1)]} {_roman(int(b.group(2)))}"
        return x
    t = re.sub(r"\[\[([^\]]+)\]\]", link, t)
    t = t.replace("*", "")
    return re.sub(r"\s+", " ", t).strip()


def _md_rows(pars, q):
    """[(latim, rótulo no formato inglês da fonte principal)] a partir do Markdown"""
    if not MD_SRC:
        return []
    d, sig = MD_PARS[pars]
    base = os.path.join(MD_SRC, d, f"Quaestio {q}")
    if not os.path.isdir(base):
        return []
    out = []
    pro = os.path.join(base, f"LEO {sig}, q. {q}.md")
    if os.path.exists(pro):
        txt = open(pro, encoding="utf-8").read().split("### Prooemium", 1)
        if len(txt) == 2:
            for par in txt[1].split("\n\n"):
                par = par.strip()
                if par and not par.startswith("!["):
                    out.append((_md_clean(par), ""))
    arts = sorted((int(re.search(r"a\. (\d+)\.md$", f).group(1)), f) for f in os.listdir(base)
                  if re.search(r"a\. \d+\.md$", f))
    for _, f in arts:
        body = open(os.path.join(base, f), encoding="utf-8").read()
        for blk in re.split(r"^###### ", body, flags=re.M)[1:]:
            head, _, txt = blk.partition("\n")
            head = head.strip()
            if (m := re.fullmatch(r"arg\. (\d+)", head)):
                lab = f"Objection {m.group(1)}"
            elif head == "s.c.":
                lab = "On the contrary"
            elif head == "resp.":
                lab = "I answer that"
            elif (m := re.fullmatch(r"ad ?(\d*)", head)):
                lab = f"Reply to Objection {m.group(1) or 1}"
            else:
                lab = ""
            for par in txt.strip().split("\n\n"):
                if par.strip():
                    out.append((_md_clean(par), lab))
                    lab = ""
    return out


def _qrows(src, pars, q):
    rows = _rows(_qfile(src, pars, q))
    return rows if _nwords(rows) > 30 else (_md_rows(pars, q) or rows)


def _qfile(src, pars, q):
    return os.path.join(src, pars, f"{pars}{q:03d}.html")


def _nwords(rows):
    return sum(len(re.findall(r"[A-Za-z]+", t)) for t, _ in rows)


def works(src):
    """lista de trabalhos para build_text.py (um por arquivo do leitor)"""
    out = []
    for pars, q0, q1, trat, desc in TRATADOS:
        sizes = [(q, _nwords(_qrows(src, pars, q))) for q in range(q0, q1 + 1)]
        total = sum(n for _, n in sizes)
        nchunks = max(1, -(-total // MAX_WORDS))
        target = total / nchunks
        chunks, cur, acc = [], [], 0
        for q, n in sizes:
            if cur and acc + n / 2 > target * (len(chunks) + 1):
                chunks.append(cur)
                cur = []
            cur.append(q)
            acc += n
        chunks.append(cur)
        sigla, la, pt = PARS[pars]
        for k, qs in enumerate(chunks):
            a, b = qs[0], qs[-1]
            rng = f"q. {a}" if a == b else f"qq. {a}–{b}"
            parte = f" ({k + 1}/{len(chunks)})" if len(chunks) > 1 else ""
            out.append({
                "id": f"{OBRA}-{sigla.lower()}-q{a:03d}", "tipo": "summa", "grupo": OBRA,
                "obra": OBRA, "pars": sigla, "parsLa": la, "parsPt": pt, "qmin": a, "qmax": b,
                "tratado": trat + parte, "fonte": src, "parsDir": pars, "qs": qs,
                "prologo": os.path.join(src, pars, f"{pars}-PROLOGUE.html") if a == 1 and pars != "FP" else None,
                "autor": "Tomás de Aquino", "autorLa": "S. Thomas de Aquino",
                "titulo": f"Suma Teológica, {sigla}, {rng}", "tituloLa": f"Summa Theologiae, {la}, {rng}",
                "cts": "", "edicao": "Textus Leoninus: Sancti Thomae Aquinatis Opera omnia iussu Leonis XIII P. M. edita, t. 4–12 (Romae, 1888–1906).",
                "edicaoCurta": "Leonina", "referencia": "questão.artigo", "exemploRef": f"{a}.1",
                "notaEdicao": "Os números à margem dos parágrafos indicam a parte de cada artigo: arg. 1, 2… (objeções), s. c. (sed contra), co. (corpo, “Respondeo”) e ad 1, 2… (respostas às objeções). Cite como questão.artigo (2.3) ou com a parte: I-II q. 90 a. 4.",
                "descricao": desc,
                "fonteTexto": {"nome": "AquinasOperaOmnia (espelho do site de Joseph Kenny, O.P.), coluna latina",
                               "url": f"https://github.com/Geremia/AquinasOperaOmnia/tree/master/summa/{pars}",
                               "licenca": "texto em domínio público; transcrição digital sem licença declarada (ver LICENSE-DATA.md)"},
            })
    return out


def build_summa(work, doc):
    pars = work["parsDir"]
    if work.get("prologo") and os.path.exists(work["prologo"]):
        doc.heading("prol", "Prólogo", "Prol.", 0)
        for lat, _ in _rows(work["prologo"]):
            doc.para()
            doc.text(lat)
            doc.close()
    for q in work["qs"]:
        doc.heading(str(q), f"Questão {q}", str(q), 0)
        art = 0
        for lat, lab in _qrows(work["fonte"], pars, q):
            m = re.match(r"Ad (\w+) sic proceditur", lat)
            if m:
                art = ORD.get(m.group(1).lower(), art + 1)
                doc.heading(f"{q}.{art}", f"Artigo {art}", str(art), 1)
            mark = ""
            if (mm := re.match(r"Objection (\d+)", lab)):
                mark = f"arg. {mm.group(1)}"
            elif lab.startswith("On the contrary"):
                mark = "s. c."
            elif lab.startswith("I answer that"):
                mark = "co."
            elif (mm := re.match(r"Reply to Objection (\d+)", lab)):
                mark = f"ad {mm.group(1)}"
            doc.para()
            if mark and art:
                doc.mark({"lab": mark})
            doc.text(lat)
            doc.close()
