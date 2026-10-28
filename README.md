# Lexicon — latim · português

Aplicação web (PWA) para consultar o **Lewis & Short** (*A Latin Dictionary*, 1879), com 51.645
verbetes, mais uma **camada de tradução das acepções principais para o português**, e um **leitor de
textos latinos** em que cada palavra está ligada ao dicionário. Interface em português, verbetes em
inglês como no original. Funciona no navegador, pode ser instalada na tela de início do iPhone/iPad e
guarda o que foi consultado para uso offline.

Projeto irmão do [Λεξικόν grego–português](https://github.com/himilcon/lexikon-grc-por).

Site: https://himilcon.github.io/lexicon-lat/

## Recursos

- Busca em latim **com ou sem quantidades** (`amo`, `ămo`); `j`/`i` e `v`/`u` são equivalentes.
- Busca por **formas flexionadas** (`amabant` → *amo*, `virum` → *vir*), com as análises do Morpheus.
- Busca reversa em **português** (nas traduções) e em **inglês** (nos resumos).
- No alto de cada verbete, **resumo em português** gerado por IA (3.248 verbetes nesta versão, que cobrem
  cerca de 90% das palavras dos textos clássicos e 95% das da Suma); nos demais, resumo em inglês.
- Verbete completo do Lewis & Short, com acepções em níveis, citações e referências.
- Botões **ver no Gaffiot** (gaffiot.fr) e **Logeion**.
- Favoritos, histórico, navegação alfabética, tema claro/escuro, links diretos (`…/#/v/2280` = *amo*).
- **Textos** (`#/textos`): César, *De Bello Gallico*; Cícero, *Catilinárias*; Virgílio, *Eneida*;
  Tomás de Aquino, *Suma Teológica* (I, I-II, II-II, III; 1,6 milhão de palavras, em 57 arquivos por
  tratado, página própria em `#/obra/tomas-suma`; referências como `I q. 2 a. 3` ou `I-II 90.4`),
  *Suma contra os Gentios* (4 livros, 325 mil palavras, 10 arquivos, `#/obra/tomas-scg`; referências
  como `III, 65` ou `3.65`) e *De ente et essentia* (`#/t/tomas-de-ente/4`).
  Toque numa palavra para ver os lemas possíveis, a análise morfológica em português, a tradução e o
  verbete. Referências diretas: `#/t/cesar-guerra-gaulesa/1.1.1`, `#/t/cicero-catilinarias/1.1`,
  `#/t/virgilio-eneida/6.851`.

## Estrutura

```
docs/                     ← site publicado pelo GitHub Pages
  index.html, styles.css, app.js, reader.js, sw.js, manifest.webmanifest, icons/
  data/index.json         ← lista de verbetes (id, chave, cabeçalho, gramática, glosa EN, bloco)
  data/ls/NNN.json        ← corpo dos verbetes em HTML, 500 por arquivo, carregados sob demanda
  data/pt.json            ← camada em português
  data/formas.json        ← formas flexionadas → verbetes (busca)
  textos/                 ← textos anotados (index.json + um arquivo por texto)
scripts/build_dict.py     ← TEI-XML do L&S → index.json + ls/
scripts/build_morph.py    ← análises do Morpheus (Diogenes) → scripts/morph.pkl (não versionado)
scripts/build_text.py     ← TEI dos textos + morfologia → docs/textos/, docs/data/formas.json
scripts/build_pt.py       ← traducao/lotes/pt-*.tsv → docs/data/pt.json
scripts/summa.py, tomas_outros.py  ← Suma Teológica; Suma contra os Gentios e De ente et essentia
scripts/latim_medieval.py, escolastico.py  ← regras e léxico (com glosas PT) para o latim escolástico
traducao/                 ← glosas inglesas e lotes de tradução
```

Tudo é estático (HTML/CSS/JS puro, sem dependências nem etapa de build no navegador).

## Rodar localmente

```bash
cd docs && python3 -m http.server 8000   # abra http://localhost:8000
```

## Regenerar os dados

```bash
# Lewis & Short e Elementary Latin Dictionary (Perseus)
git clone --depth 1 --filter=blob:none --sparse https://github.com/PerseusDL/lexica /tmp/lexica
git -C /tmp/lexica sparse-checkout set CTS_XML_TEI/perseus/pdllex/lat
python3 scripts/build_dict.py /tmp/lexica/CTS_XML_TEI/perseus/pdllex/lat docs/data

# Morfologia (Morpheus, via dados pré-compilados do Diogenes)
git clone --depth 1 https://github.com/pjheslin/diogenes-prebuilt-data /tmp/diog
tar -xJf /tmp/diog/prebuilt-data.tar.xz -C /tmp/diog dependencies/data/latin-analyses.txt dependencies/data/lat.ls.perseus-eng1.xml
python3 scripts/build_morph.py /tmp/diog/dependencies/data

# Textos
git clone --depth 1 --filter=blob:none --sparse https://github.com/PerseusDL/canonical-latinLit /tmp/latlit
git -C /tmp/latlit sparse-checkout set data/phi0448/phi001 data/phi0474/phi013 data/phi0690/phi003
git clone --depth 1 --filter=blob:none --sparse https://github.com/Geremia/AquinasOperaOmnia /tmp/aq
git -C /tmp/aq sparse-checkout set --no-cone /summa/ "/ContraGentiles*.htm" "/DeEnte&Essentia.htm"
git clone --filter=blob:none https://github.com/AnthropologieBiblique/SummaTheologiae /tmp/stmd   # questões que faltam no AquinasOperaOmnia
python3 scripts/build_text.py /tmp/latlit/data docs /tmp/aq/summa /tmp/stmd

# Camada em português
python3 scripts/build_pt.py
```

Ao mudar os dados do dicionário, troque `DATA_VER` em `docs/app.js` e `DATA_CACHE`/`INDEX` em
`docs/sw.js`; ao mudar HTML/CSS/JS, troque `VERSION` em `docs/sw.js`.

## Como foram feitas as análises dos textos

Cada palavra é procurada nas ~350 mil formas analisadas pelo Morpheus, com tentativa de separar as
enclíticas *-que*, *-ne*, *-ve*. Não há desambiguação pelo contexto: quando há mais de um lema possível,
a ordem segue a frequência do lema nos três textos (ocorrências não ambíguas), com preferência para
palavras invariáveis cuja forma é a própria entrada (*sine*, *ita*) e alguns ajustes manuais
(*Gallia* antes de *Gallius*). O painel mostra todas as análises; a primeira é só a mais provável.
Ficaram sem análise cerca de 1% das palavras (sobretudo nomes próprios raros e numerais).

## A camada em português

As glosas inglesas de cada verbete foram extraídas automaticamente do L&S (itálicos em sequência no
início das acepções) ou, para o vocabulário mais comum, das glosas `<tr>` do *Elementary Latin
Dictionary* de Lewis. Os lotes `traducao/lotes/en-*.tsv` e `c-*.tsv` estão ordenados pela frequência
nos textos; os já traduzidos estão em `pt-*.tsv` (formato `id<TAB>glosa`). Para ampliar a camada,
traduza o próximo lote no mesmo formato e rode `scripts/build_pt.py`.

## Licenças

Código: MIT. Dados: CC BY-SA 4.0 (Perseus) e obras derivadas sob a mesma licença; ver `LICENSE-DATA.md`,
que também registra um ponto a verificar sobre os dados de morfologia antes de qualquer uso comercial.
