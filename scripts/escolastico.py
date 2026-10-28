"""Léxico escolástico para os textos de Tomás de Aquino.

Palavras frequentes na Suma Teológica, na Suma contra os Gentios e no De ente et essentia que o Morpheus
não analisa — em geral porque são termos técnicos medievais (quidditas, sensitivus, totaliter), ausentes
do Lewis & Short. Para cada lema há uma classe de flexão, da qual se geram as formas com análises no mesmo
formato do Morpheus, e uma glosa curta em português (gerada por IA, como a camada PT do dicionário).

Se o lema existir no L&S (ens, adipiscor, hypostasis), build_text.py liga as formas ao verbete; senão o
painel do leitor mostra a glosa daqui.
"""

# (lema, classe, gramática, glosa PT)
LEXICO = [
    # substantivos
    ("quidditas", "n3tas", "f.", "qüididade, o que a coisa é (essência expressa na definição)"),
    ("animalitas", "n3tas", "f.", "animalidade"),
    ("praedicabilitas", "n3tas", "f.", "predicabilidade, aptidão a ser predicado"),
    ("intelligibilitas", "n3tas", "f.", "inteligibilidade"),
    ("causalitas", "n3tas", "f.", "causalidade"),
    ("totalitas", "n3tas", "f.", "totalidade"),
    ("personalitas", "n3tas", "f.", "personalidade, o ser pessoa"),
    ("poenalitas", "n3tas", "f.", "penalidade, caráter penal; pena"),
    ("conformitas", "n3tas", "f.", "conformidade"),
    ("identitas", "n3tas", "f.", "identidade"),
    ("congruitas", "n3tas", "f.", "congruência, conveniência"),
    ("studiositas", "n3tas", "f.", "estudiosidade (virtude que modera o desejo de saber)"),
    ("individuatio", "n3io", "f.", "individuação"),
    ("incarnatio", "n3io", "f.", "encarnação"),
    ("filiatio", "n3io", "f.", "filiação"),
    ("recompensatio", "n3io", "f.", "recompensa, compensação"),
    ("duratio", "n3io", "f.", "duração"),
    ("inchoatio", "n3io", "f.", "início, começo"),
    ("alteratio", "n3io", "f.", "alteração (mudança de qualidade)"),
    ("mixtio", "n3io", "f.", "mistura, combinação dos elementos"),
    ("aequivocatio", "n3io", "f.", "equivocidade, equívoco"),
    ("indeterminatio", "n3io", "f.", "indeterminação"),
    ("certitudo", "n3do", "f.", "certeza"),
    ("aptitudo", "n3do", "f.", "aptidão"),
    ("gratitudo", "n3do", "f.", "gratidão"),
    ("contingentia", "n1", "f.", "contingência"),
    ("influentia", "n1", "f.", "influência, influxo"),
    ("concomitantia", "n1", "f.", "concomitância"),
    ("exigentia", "n1", "f.", "exigência"),
    ("inobedientia", "n1", "f.", "desobediência"),
    ("acedia", "n1", "f.", "acídia (tristeza diante do bem espiritual)"),
    ("homilia", "n1", "f.", "homilia, sermão"),
    ("hierarchia", "n1", "f.", "hierarquia"),
    ("simonia", "n1", "f.", "simonia (compra ou venda de coisas espirituais)"),
    ("dulia", "n1", "f.", "dulia (culto de honra aos santos)"),
    ("eubulia", "n1", "f.", "eubulia, bom conselho"),
    ("epieikeia", "n1", "f.", "epiqueia, eqüidade"),
    ("metaphysica", "n1", "f.", "metafísica"),
    ("hypostasis", "n3is", "f.", "hipóstase, subsistência individual"),
    ("synderesis", "n3is", "f.", "sindérese (hábito dos primeiros princípios morais)"),
    ("haeresis", "n3is", "f.", "heresia"),
    ("nocumentum", "n2n", "n.", "dano, prejuízo"),
    ("vituperium", "n2n", "n.", "vitupério, censura"),
    ("diaphanum", "n2n", "n.", "o diáfano, o meio transparente"),
    ("artificiatum", "n2n", "n.", "artefato, obra de arte"),
    ("empyreum", "n2n", "n.", "o céu empíreo"),
    ("comprehensor", "n3or", "m.", "compreensor, o bem-aventurado que já possui a Deus"),
    ("motor", "n3or", "m.", "motor, o que move"),
    # adjetivos -us, -a, -um
    ("sensitivus", "a212", "adj.", "sensitivo, dos sentidos"),
    ("appetitivus", "a212", "adj.", "apetitivo"),
    ("cognoscitivus", "a212", "adj.", "cognoscitivo"),
    ("cognitivus", "a212", "adj.", "cognitivo"),
    ("apprehensivus", "a212", "adj.", "apreensivo, que apreende"),
    ("motivus", "a212", "adj.", "motor, motivo, que move"),
    ("nutritivus", "a212", "adj.", "nutritivo"),
    ("generativus", "a212", "adj.", "generativo"),
    ("memorativus", "a212", "adj.", "memorativo"),
    ("cogitativus", "a212", "adj.", "cogitativo (a cogitativa: razão particular)"),
    ("imaginativus", "a212", "adj.", "imaginativo"),
    ("visivus", "a212", "adj.", "visivo, da visão"),
    ("dimensivus", "a212", "adj.", "dimensivo, de dimensão"),
    ("directivus", "a212", "adj.", "diretivo"),
    ("discursivus", "a212", "adj.", "discursivo"),
    ("electivus", "a212", "adj.", "eletivo"),
    ("factivus", "a212", "adj.", "factivo, produtivo"),
    ("regnativus", "a212", "adj.", "régio, de governo (prudência regnativa)"),
    ("coactivus", "a212", "adj.", "coativo"),
    ("iudicativus", "a212", "adj.", "judicativo"),
    ("moderativus", "a212", "adj.", "moderador"),
    ("conservativus", "a212", "adj.", "conservativo"),
    ("constitutivus", "a212", "adj.", "constitutivo"),
    ("susceptivus", "a212", "adj.", "suscetível, receptivo"),
    ("impeditivus", "a212", "adj.", "impeditivo"),
    ("consiliativus", "a212", "adj.", "consultivo, que delibera"),
    ("commutativus", "a212", "adj.", "comutativo"),
    ("speculativus", "a212", "adj.", "especulativo"),
    ("satisfactorius", "a212", "adj.", "satisfatório, que satisfaz (pela culpa)"),
    ("specificus", "a212", "adj.", "específico"),
    ("immediatus", "a212", "adj.", "imediato"),
    ("miraculosus", "a212", "adj.", "milagroso"),
    ("virtuosus", "a212", "adj.", "virtuoso"),
    ("metaphysicus", "a212", "adj.", "metafísico"),
    # adjetivos -is, -e
    ("accidentalis", "a3", "adj.", "acidental"),
    ("essentialis", "a3", "adj.", "essencial"),
    ("integralis", "a3", "adj.", "integral (parte integral)"),
    ("individualis", "a3", "adj.", "individual"),
    ("immaterialis", "a3", "adj.", "imaterial"),
    ("habitualis", "a3", "adj.", "habitual"),
    ("instrumentalis", "a3", "adj.", "instrumental"),
    ("supernaturalis", "a3", "adj.", "sobrenatural"),
    ("connaturalis", "a3", "adj.", "conatural"),
    ("figuralis", "a3", "adj.", "figurativo, figural"),
    ("realis", "a3", "adj.", "real"),
    ("notionalis", "a3", "adj.", "nocional (próprio de uma Pessoa divina)"),
    ("aliqualis", "a3", "adj.", "algum, de alguma qualidade"),
    ("agibilis", "a3", "adj.", "factível, que pode ser feito (agibilia: as ações)"),
    ("operabilis", "a3", "adj.", "operável, que pode ser feito"),
    ("enuntiabilis", "a3", "adj.", "enunciável (enuntiabilia: proposições)"),
    ("communicabilis", "a3", "adj.", "comunicável"),
    ("assumptibilis", "a3", "adj.", "assumível"),
    ("universalis", "a3", "adj.", "universal"),
    ("totalis", "a3", "adj.", "total"),
    ("formalis", "a3", "adj.", "formal"),
    ("materialis", "a3", "adj.", "material"),
    ("virtualis", "a3", "adj.", "virtual (presente pela potência ou eficácia)"),
    ("substantialis", "a3", "adj.", "substancial"),
    ("intellectualis", "a3", "adj.", "intelectual"),
    ("praesentialis", "a3", "adj.", "presencial"),
    ("sufficiens", "a3ns", "adj.", "suficiente"),
    # verbos
    ("causo", "v1", "v.", "causar"),
    ("individuo", "v1", "v.", "individuar"),
    ("diversifico", "v1", "v.", "diversificar"),
    ("specifico", "v1", "v.", "especificar"),
    ("verifico", "v1", "v.", "verificar; ser verdadeiro de"),
    ("assimilo", "v1", "v.", "assimilar, tornar semelhante"),
    ("proportiono", "v1", "v.", "proporcionar"),
    ("recompenso", "v1", "v.", "recompensar, compensar"),
    ("contrario", "v1", "v.", "contrariar, opor-se"),
    ("unio", "v4", "v.", "unir"),
    ("medio", "v1", "v.", "mediar; estar no meio (mediante: por meio de)"),
    ("odio", "v4", "v.", "odiar (forma medieval de odi)"),
    # nomes próprios
    ("Gregorius", "n2m", "n. pr.", "Gregório (Magno, papa; ou de Nissa)"),
    ("Chrysostomus", "n2m", "n. pr.", "(João) Crisóstomo"),
    ("Petrus", "n2m", "n. pr.", "Pedro"),
    ("Basilius", "n2m", "n. pr.", "Basílio"),
    ("Anselmus", "n2m", "n. pr.", "Anselmo"),
    ("Cyrillus", "n2m", "n. pr.", "Cirilo"),
    ("Iacobus", "n2m", "n. pr.", "Tiago"),
    ("Bernardus", "n2m", "n. pr.", "Bernardo"),
    ("Nyssenus", "n2m", "n. pr.", "o Nisseno (Gregório de Nissa)"),
    ("Beda", "n1m", "n. pr.", "Beda"),
    ("Avicenna", "n1m", "n. pr.", "Avicena"),
    ("Tobias", "n1m", "n. pr.", "Tobias"),
    ("Hugo", "n3on", "n. pr.", "Hugo (de São Vítor)"),
    ("Averroes", "indecl", "n. pr.", "Averróis (o Comentador)"),
    ("Adam", "adam", "n. pr.", "Adão"),
    ("Abraham", "abraham", "n. pr.", "Abraão"),
    ("Moyses", "moyses", "n. pr.", "Moisés"),
    ("Ierusalem", "indecl", "n. pr.", "Jerusalém"),
    ("Melchisedech", "indecl", "n. pr.", "Melquisedec"),
    ("Esau", "indecl", "n. pr.", "Esaú"),
    ("cherubim", "indecl", "n. pl.", "querubins"),
    ("seraphim", "indecl", "n. pl.", "serafins"),
    ("rabbi", "indecl", "indecl.", "rabi, mestre"),
    ("ly", "indecl", "art.", "o termo (artigo escolástico: ly homo = o termo “homem”)"),
]

# formas soltas: forma → [(lema, chave L&S ou None, análise)]
FORMAS = {
    "entis": [("ens", "ens", "pres part masc/fem/neut gen sg")],
    "enti": [("ens", "ens", "pres part masc/fem/neut dat sg")],
    "ente": [("ens", "ens", "pres part masc/fem/neut abl sg")],
    "entia": [("ens", "ens", "pres part neut nom/acc pl")],
    "entium": [("ens", "ens", "pres part masc/fem/neut gen pl")],
    "entibus": [("ens", "ens", "pres part masc/fem/neut dat/abl pl")],
    "entes": [("ens", "ens", "pres part masc/fem nom/acc pl")],
    "entem": [("ens", "ens", "pres part masc/fem acc sg")],
    "essendi": [("sum", "sum1", "gerundive neut gen sg")], "essendo": [("sum", "sum1", "gerundive neut dat/abl sg")],
    "volendi": [("volo", "volo2", "gerundive neut gen sg")], "volendo": [("volo", "volo2", "gerundive neut dat/abl sg")],
    "volendum": [("volo", "volo2", "gerundive neut acc sg")],
    "volitum": [("volo", "volo2", "perf part pass neut nom/acc sg")], "volita": [("volo", "volo2", "perf part pass neut nom/acc pl")],
    "volitus": [("volo", "volo2", "perf part pass masc nom sg")], "voliti": [("volo", "volo2", "perf part pass masc gen sg")],
    "incoepit": [("incipio", "incipio", "perf ind act 3rd sg")], "incoeperit": [("incipio", "incipio", "perf subj act 3rd sg")],
    "incoeperunt": [("incipio", "incipio", "perf ind act 3rd pl")],
    "quinimmo": [("quin", "quin", "compound"), ("immo", "immo", "compound")],
    "unaquaeque": [("unusquisque", "unusquisque", "fem nom sg")], "unaquaque": [("unusquisque", "unusquisque", "fem abl sg")],
    "unamquamque": [("unusquisque", "unusquisque", "fem acc sg")], "unumquemque": [("unusquisque", "unusquisque", "masc acc sg")],
    "diversimode": [("diversus", "diversus", "compound"), ("modus", "modus", "compound")],
    "animabus": [("anima", "anima", "fem dat/abl pl")],
    "adipisci": [("adipiscor", "adipiscor", "pres inf pass")], "adipiscitur": [("adipiscor", "adipiscor", "pres ind pass 3rd sg")],
    "adipiscuntur": [("adipiscor", "adipiscor", "pres ind pass 3rd pl")], "adipiscatur": [("adipiscor", "adipiscor", "pres subj pass 3rd sg")],
    "adipiscantur": [("adipiscor", "adipiscor", "pres subj pass 3rd pl")], "adipiscendi": [("adipiscor", "adipiscor", "gerundive neut gen sg")],
    "adipiscendam": [("adipiscor", "adipiscor", "gerundive fem acc sg")], "adipiscendum": [("adipiscor", "adipiscor", "gerundive neut acc sg")],
    "multoties": [("multotiens", "multotiens", "indeclform (adverb)")],
    "octogintatrium": [("octoginta", "octoginta", "compound"), ("tres", "tres", "compound")],
}
for _f, _c in (("semetipsum", "acc"), ("semetipso", "abl"), ("semetipsam", "acc"), ("semetipsa", "abl")):
    FORMAS[_f] = [("sui", "sui", "compound:pron. reflexivo, " + _c), ("ipse", "ipse", "compound")]
for _f, _p in (("teipsum", "tu"), ("teipso", "tu"), ("nosipsos", "nos"), ("vosipsos", "vos"), ("meipsum", "ego"), ("meipso", "ego")):
    FORMAS[_f] = [(_p, _p if _p != "ego" else "ego", "compound"), ("ipse", "ipse", "compound")]

CASOS = [("nom", "sg"), ("gen", "sg"), ("dat", "sg"), ("acc", "sg"), ("abl", "sg"),
         ("nom", "pl"), ("gen", "pl"), ("dat", "pl"), ("acc", "pl"), ("abl", "pl")]
DESIN = {
    "n1": ("a", "ae", "ae", "am", "a", "ae", "arum", "is", "as", "is"),
    "n2m": ("us", "i", "o", "um", "o", "i", "orum", "is", "os", "is"),
    "n2n": ("um", "i", "o", "um", "o", "a", "orum", "is", "a", "is"),
    "n3tas": ("tas", "tatis", "tati", "tatem", "tate", "tates", "tatum", "tatibus", "tates", "tatibus"),
    "n3io": ("io", "ionis", "ioni", "ionem", "ione", "iones", "ionum", "ionibus", "iones", "ionibus"),
    "n3do": ("do", "dinis", "dini", "dinem", "dine", "dines", "dinum", "dinibus", "dines", "dinibus"),
    "n3or": ("or", "oris", "ori", "orem", "ore", "ores", "orum", "oribus", "ores", "oribus"),
    "n3on": ("o", "onis", "oni", "onem", "one", "ones", "onum", "onibus", "ones", "onibus"),
    "n3is": ("is", "is", "i", "im", "i", "es", "ium", "ibus", "es", "ibus"),
}
DESIN["n1m"] = DESIN["n1"]
GENERO = {"n1": "fem", "n1m": "masc", "n2m": "masc", "n2n": "neut", "n3tas": "fem", "n3io": "fem", "n3do": "fem",
          "n3or": "masc", "n3on": "masc", "n3is": "fem"}
RAIZ = {"n1": "a", "n1m": "a", "n2m": "us", "n2n": "um", "n3tas": "tas", "n3io": "io", "n3do": "do", "n3or": "or",
        "n3on": "o", "n3is": "is", "a212": "us", "a3": "is", "v1": "o", "v4": "io"}

V1 = {  # terminação → análise (radical sem o -o)
    "o": "pres ind act 1st sg", "as": "pres ind act 2nd sg", "at": "pres ind act 3rd sg", "amus": "pres ind act 1st pl",
    "ant": "pres ind act 3rd pl", "or": "pres ind pass 1st sg", "atur": "pres ind pass 3rd sg", "antur": "pres ind pass 3rd pl",
    "et": "pres subj act 3rd sg", "ent": "pres subj act 3rd pl", "etur": "pres subj pass 3rd sg", "entur": "pres subj pass 3rd pl",
    "abat": "imperf ind act 3rd sg", "abant": "imperf ind act 3rd pl", "abatur": "imperf ind pass 3rd sg",
    "abantur": "imperf ind pass 3rd pl", "aret": "imperf subj act 3rd sg", "arent": "imperf subj act 3rd pl",
    "aretur": "imperf subj pass 3rd sg", "arentur": "imperf subj pass 3rd pl", "abit": "fut ind act 3rd sg",
    "abitur": "fut ind pass 3rd sg", "avit": "perf ind act 3rd sg", "averunt": "perf ind act 3rd pl",
    "are": "pres inf act", "ari": "pres inf pass", "asse": "perf inf act",
    "ans": "pres part masc/fem/neut nom sg", "antis": "pres part masc/fem/neut gen sg", "anti": "pres part masc/fem/neut dat sg",
    "antem": "pres part masc/fem acc sg", "ante": "pres part masc/fem/neut abl sg", "antes": "pres part masc/fem nom/acc pl",
    "antia": "pres part neut nom/acc pl", "antium": "pres part masc/fem/neut gen pl", "antibus": "pres part masc/fem/neut dat/abl pl",
    "andi": "gerundive neut gen sg", "ando": "gerundive neut dat/abl sg", "andum": "gerundive neut acc sg",
}
V4 = {
    "io": "pres ind act 1st sg", "it": "pres ind act 3rd sg", "iunt": "pres ind act 3rd pl", "itur": "pres ind pass 3rd sg",
    "iuntur": "pres ind pass 3rd pl", "iat": "pres subj act 3rd sg", "iant": "pres subj act 3rd pl", "iatur": "pres subj pass 3rd sg",
    "iantur": "pres subj pass 3rd pl", "iebat": "imperf ind act 3rd sg", "iebatur": "imperf ind pass 3rd sg",
    "iret": "imperf subj act 3rd sg", "irent": "imperf subj act 3rd pl", "iretur": "imperf subj pass 3rd sg",
    "irentur": "imperf subj pass 3rd pl", "iet": "fut ind act 3rd sg", "ietur": "fut ind pass 3rd sg", "ivit": "perf ind act 3rd sg",
    "ire": "pres inf act", "iri": "pres inf pass", "iens": "pres part masc/fem/neut nom sg", "ientis": "pres part masc/fem/neut gen sg",
    "ienti": "pres part masc/fem/neut dat sg", "ientem": "pres part masc/fem acc sg", "iente": "pres part masc/fem/neut abl sg",
    "ientes": "pres part masc/fem nom/acc pl", "ientia": "pres part neut nom/acc pl", "iendi": "gerundive neut gen sg", "iendo": "gerundive neut dat/abl sg",
}
A212 = {}
for _g, _ds in (("masc", DESIN["n2m"]), ("fem", DESIN["n1"]), ("neut", DESIN["n2n"])):
    for (_c, _n), _d in zip(CASOS, _ds):
        A212.setdefault(_d, []).append(f"{_g} {_c} {_n}")
A3 = {"is": ["masc/fem nom sg", "masc/fem/neut gen sg"], "e": ["neut nom/acc sg"], "i": ["masc/fem/neut dat/abl sg"],
      "em": ["masc/fem acc sg"], "es": ["masc/fem nom/acc pl"], "ia": ["neut nom/acc pl"], "ium": ["masc/fem/neut gen pl"],
      "ibus": ["masc/fem/neut dat/abl pl"]}


def _part_pass(stem, out, lemma):
    for d, ms in A212.items():
        for m in ms:
            out.setdefault(stem + d, []).append((lemma, "perf part pass " + m))


def gerar():
    """forma minúscula → [(lema, análise)], e lema → (gramática, glosa)"""
    formas, info = {}, {}
    for lemma, cl, gram, gl in LEXICO:
        info[lemma] = (gram, gl)
        low = lemma.lower()
        if cl == "indecl":
            formas.setdefault(low, []).append((lemma, "indeclform (indecl)"))
            continue
        if cl == "adam":
            for f, m in (("adam", "masc nom/acc sg"), ("adae", "masc gen/dat sg"), ("adami", "masc gen sg")):
                formas.setdefault(f, []).append((lemma, m))
            continue
        if cl == "abraham":
            for f, m in (("abraham", "masc nom/acc sg"), ("abrahae", "masc gen/dat sg"), ("abrahe", "masc gen/dat sg")):
                formas.setdefault(f, []).append((lemma, m))
            continue
        if cl == "moyses":
            for f, m in (("moyses", "masc nom sg"), ("moysi", "masc gen/dat sg"), ("moysen", "masc acc sg"), ("moyse", "masc abl sg")):
                formas.setdefault(f, []).append((lemma, m))
            continue
        stem = low[: -len(RAIZ[cl])] if cl in RAIZ else low
        if cl in DESIN:
            for (c, n), d in zip(CASOS, DESIN[cl]):
                formas.setdefault(stem + d, []).append((lemma, f"{GENERO[cl]} {c} {n}"))
        elif cl == "a212":
            for d, ms in A212.items():
                for m in ms:
                    formas.setdefault(stem + d, []).append((lemma, m))
        elif cl == "a3ns":
            st = low[:-2]
            for d, ms in {"ns": ["masc/fem/neut nom sg"], "ntis": ["masc/fem/neut gen sg"], "nti": ["masc/fem/neut dat/abl sg"],
                          "ntem": ["masc/fem acc sg"], "ntes": ["masc/fem nom/acc pl"], "ntia": ["neut nom/acc pl"],
                          "ntium": ["masc/fem/neut gen pl"], "ntibus": ["masc/fem/neut dat/abl pl"]}.items():
                for m in ms:
                    formas.setdefault(st + d, []).append((lemma, m))
        elif cl == "a3":
            for d, ms in A3.items():
                for m in ms:
                    formas.setdefault(stem + d, []).append((lemma, m))
        elif cl == "v1":
            for d, m in V1.items():
                formas.setdefault(stem + d, []).append((lemma, m))
            _part_pass(stem + "at", formas, lemma)
        elif cl == "v4":
            for d, m in V4.items():
                formas.setdefault(stem + d, []).append((lemma, m))
            _part_pass(stem + "it", formas, lemma)
    for f, an in list(formas.items()):
        seen = []
        for a in an:
            if a not in seen:
                seen.append(a)
        formas[f] = seen
    return formas, info
