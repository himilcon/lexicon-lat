"""Recursos para o latim escolástico da Suma, usados por build_text.py quando o Morpheus não reconhece a forma.

1. Abreviaturas de citação (Ethic., Matth., cap.) → "citação", com o nome da obra em português.
2. Compostos escolásticos escritos juntos (inquantum, huiusmodi, seipsum).
3. Variantes gráficas medievais (poenitentia/paenitentia, intelligibilis/intellegibilis, existens/exsistens).
4. Formas cujo verbete existe no Lewis & Short mas que o Morpheus não analisa: a forma é a própria entrada
   ("forma de dicionário") ou uma flexão regular dela ("lema provável").
"""
import re

CITACAO = {
    # Bíblia
    "Gen": "Gênesis", "Exod": "Êxodo", "Levit": "Levítico", "Lev": "Levítico", "Num": "Números", "Deut": "Deuteronômio",
    "Iosue": "Josué", "Iudic": "Juízes", "Ruth": "Rute", "Reg": "Reis (Samuel e Reis)", "Paralip": "Crônicas",
    "Esdr": "Esdras", "Tob": "Tobias", "Iudith": "Judite", "Esth": "Ester", "Iob": "Jó", "Psalm": "Salmos", "Ps": "Salmos",
    "Prov": "Provérbios", "Proverb": "Provérbios", "Eccle": "Eclesiastes", "Eccles": "Eclesiastes", "Eccl": "Eclesiastes",
    "Cant": "Cântico dos Cânticos", "Sap": "Sabedoria", "Eccli": "Eclesiástico", "Isaiae": "Isaías", "Isa": "Isaías",
    "Ierem": "Jeremias", "Thren": "Lamentações", "Baruch": "Baruc", "Ezech": "Ezequiel", "Dan": "Daniel", "Osee": "Oseias",
    "Ioel": "Joel", "Amos": "Amós", "Abd": "Abdias", "Ionae": "Jonas", "Mich": "Miqueias", "Nahum": "Naum",
    "Habac": "Habacuc", "Soph": "Sofonias", "Agg": "Ageu", "Zach": "Zacarias", "Malach": "Malaquias", "Machab": "Macabeus",
    "Matth": "Mateus", "Marc": "Marcos", "Luc": "Lucas", "Ioan": "João", "Act": "Atos dos Apóstolos", "Rom": "Romanos",
    "Cor": "Coríntios", "Gal": "Gálatas", "Ephes": "Efésios", "Philipp": "Filipenses", "Coloss": "Colossenses",
    "Thess": "Tessalonicenses", "Tim": "Timóteo", "Tit": "Tito", "Philem": "Filêmon", "Heb": "Hebreus", "Hebr": "Hebreus",
    "Iac": "Tiago", "Pet": "Pedro", "Petr": "Pedro", "Iud": "Judas", "Apoc": "Apocalipse",
    # Aristóteles
    "Ethic": "Ética a Nicômaco (Aristóteles)", "Metaphys": "Metafísica (Aristóteles)", "Physic": "Física (Aristóteles)",
    "Poster": "Analíticos Posteriores (Aristóteles)", "Prior": "Analíticos Anteriores (Aristóteles)",
    "Topic": "Tópicos (Aristóteles)", "Rhetoric": "Retórica (Aristóteles)", "Rhet": "Retórica", "Polit": "Política (Aristóteles)",
    "Cael": "Do céu (Aristóteles)", "Meteor": "Meteorológicos (Aristóteles)", "Praedicam": "Categorias (Aristóteles)",
    "Elench": "Refutações sofísticas (Aristóteles)", "Perih": "Da interpretação (Aristóteles)",
    # Agostinho, Gregório, Dionísio e outros
    "Civ": "A Cidade de Deus (Agostinho)", "Confess": "Confissões (Agostinho)", "Trin": "A Trindade",
    "Enchirid": "Enchiridion (Agostinho)", "Litt": "Comentário literal ao Gênesis (Agostinho)", "Doct": "A doutrina cristã (Agostinho)",
    "Doctr": "A doutrina cristã (Agostinho)", "Arb": "O livre-arbítrio (Agostinho)", "Arbit": "O livre-arbítrio (Agostinho)",
    "Relig": "A verdadeira religião (Agostinho)", "Retract": "Retratações (Agostinho)", "Soliloq": "Solilóquios (Agostinho)",
    "Faust": "Contra Fausto (Agostinho)", "Virginit": "A santa virgindade (Agostinho)", "Serm": "Sermões",
    "Moral": "Moralia in Iob (Gregório Magno)", "Pastoral": "Regra pastoral (Gregório Magno)", "Dialog": "Diálogos (Gregório Magno)",
    "Hom": "Homilias", "Evang": "Evangelhos (homilias sobre os)", "Nom": "Os nomes divinos (Pseudo-Dionísio)",
    "Hier": "A hierarquia (Pseudo-Dionísio)", "Eccles. Hier": "A hierarquia eclesiástica",
    "Consol": "A consolação da filosofia (Boécio)", "Offic": "Dos deveres (Cícero ou Ambrósio)", "Benefic": "Dos benefícios (Sêneca)",
    "Etymol": "Etimologias (Isidoro de Sevilha)", "Sent": "Sentenças (Pedro Lombardo)", "Fid": "A fé ortodoxa (João Damasceno)",
    "Orth": "A fé ortodoxa (João Damasceno)", "Monach": "Instituições monásticas (Cassiano)", "Dogmat": "Dogmas eclesiásticos (Genádio)",
    "Caus": "Livro das causas", "Praedest": "A predestinação dos santos (Agostinho)", "Synod": "Concílio",
    "Consecr": "Decreto de Graciano, De consecratione", "Decret": "Decreto de Graciano", "Vet": "Antigo (Testamento)",
    "Nov": "Novo (Testamento)", "Verb": "Palavras (do Senhor, do Apóstolo)", "Dom": "do Senhor", "Christ": "cristão(s)",
    "Sanct": "dos santos",
    # termos técnicos de citação
    "cap": "capítulo", "ult": "último (capítulo ou livro)", "qu": "questão", "q": "questão", "art": "artigo", "dist": "distinção",
    "lect": "lição", "tract": "tratado", "hom": "homilia", "lib": "livro", "ep": "epístola", "epist": "epístola",
    "can": "cânon", "etc": "et cetera",
}

# formas compostas → [(lema do L&S, forma de dicionário, rótulo)]
COMPOSTOS = {
    "inquantum": [("in", "in1", "prep"), ("quantus", "quantus", "")],
    "intantum": [("in", "in1", "prep"), ("tantus", "tantus", "")],
    "huiusmodi": [("hic", "hic1", "gen. sg."), ("modus", "modus", "gen. sg.")],
    "eiusmodi": [("is", "is", "gen. sg."), ("modus", "modus", "gen. sg.")],
    "cuiusmodi": [("qui", "qui1", "gen. sg."), ("modus", "modus", "gen. sg.")],
    "quodammodo": [("quodammodo", "quodammodo", "")],
    "idest": [("is", "is", "neutro"), ("sum", "sum1", "3ª pess. sing.")],
    "unumquodque": [("unusquisque", "unusquisque", "")], "unicuique": [("unusquisque", "unusquisque", "")],
    "uniuscuiusque": [("unusquisque", "unusquisque", "")], "unoquoque": [("unusquisque", "unusquisque", "")],
}
for f in ("seipsum", "seipso", "seipsam", "seipsa", "seipsis", "seipsos", "seipsas"):
    COMPOSTOS[f] = [("sui", "sui", "pron. reflexivo"), ("ipse", "ipse", "")]

VARIANTES = [
    (r"oe", "ae"), (r"ae", "oe"), (r"^obed", "oboed"), (r"intellig", "intelleg"), (r"neglig", "negleg"),
    (r"caerem", "caerim"), (r"^ex([aeiou])", r"exs\1"), (r"^exspect", "expect"), (r"ti([aeiou])", r"ci\1"),
    (r"ci([aeiou])", r"ti\1"), (r"^nichil", "nihil"), (r"michi", "mihi"), (r"^hier", "hier"), (r"y", "i"),
    (r"^Boet", "Boeth"), (r"^Hiero", "Hiero"),
]

# terminação da forma → terminações possíveis da entrada (ordem de preferência)
FLEXAO = [
    ("ibus", ["is", "us", "es", "a", "um", "e"]), ("orum", ["us", "um"]), ("arum", ["a"]),
    ("ionem", ["io"]), ("ionis", ["io"]), ("ioni", ["io"]), ("ione", ["io"]), ("iones", ["io"]),
    ("tatem", ["tas"]), ("tatis", ["tas"]), ("tati", ["tas"]), ("tate", ["tas"]), ("tates", ["tas"]),
    ("dinem", ["do"]), ("dinis", ["do"]), ("dini", ["do"]), ("dine", ["do"]),
    ("am", ["a", "us"]), ("ae", ["a", "us"]), ("as", ["a", "us"]), ("um", ["us", "um", "is"]), ("os", ["us"]),
    ("is", ["us", "um", "a", "is", "e"]), ("o", ["us", "um", "o"]), ("i", ["us", "um", "is"]), ("a", ["us", "um", "is"]),
    ("em", ["is", "es", "s"]), ("es", ["is", "es"]), ("e", ["is", "us"]), ("ia", ["e", "is"]), ("ium", ["is", "e"]),
    ("ter", ["is", "us"]), ("iter", ["is"]),
    ("atur", ["o", "or"]), ("antur", ["o", "or"]), ("at", ["o"]), ("ant", ["o"]), ("are", ["o"]), ("ari", ["o", "or"]),
    ("itur", ["o", "io"]), ("it", ["o", "io"]), ("unt", ["o"]), ("untur", ["o"]), ("ere", ["o", "eo"]), ("i", ["o"]),
]


def variantes(form):
    out = []
    for a, b in VARIANTES:
        v = re.sub(a, b, form, count=1)
        if v != form and v not in out:
            out.append(v)
    return out


def flexao_candidatas(form):
    """[(forma de dicionário candidata, terminação da forma)] por regras de flexão regulares"""
    f = form.lower()
    out = []
    for end, ents in FLEXAO:
        if f.endswith(end) and len(f) - len(end) >= 3:
            stem = f[: -len(end)]
            for e in ents:
                out.append(stem + e)
    return out
