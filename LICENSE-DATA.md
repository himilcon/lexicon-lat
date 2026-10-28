# Licenças dos dados

O **código** deste projeto (HTML, CSS, JavaScript e scripts Python) está sob a licença MIT (arquivo `LICENSE`).
Os **dados** têm as licenças abaixo, que valem para os arquivos de `docs/data/`, `docs/textos/` e `traducao/`.

## Lewis & Short — `docs/data/index.json`, `docs/data/ls/*.json`

Charlton T. Lewis e Charles Short, *A Latin Dictionary* (Oxford: Clarendon Press, 1879), domínio público.
Digitalização em TEI-XML da Perseus Digital Library (`lat.ls.perseus-eng2.xml`), sob
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

> Text provided under a CC BY-SA license by Perseus Digital Library, http://www.perseus.tufts.edu,
> with funding from The National Endowment for the Humanities.
> Data accessed from https://github.com/PerseusDL/lexica/ [outubro de 2026].

Modificações: conversão do TEI-XML para HTML simplificado; extração automática de glosas curtas em
inglês. O conteúdo lexicográfico dos verbetes não foi alterado. A Perseus pede que modificações lhe
sejam oferecidas.

As glosas curtas de parte dos verbetes vêm de Charlton T. Lewis, *An Elementary Latin Dictionary*
(1890), na digitalização da Perseus (`viaf2845558.viaf001.xml`), também CC BY-SA 4.0.

## Camada em português — `docs/data/pt.json`, `traducao/`

Tradução para o português das glosas inglesas acima, **gerada por IA** (Claude, da Anthropic) em
outubro de 2026. Como obra derivada de dados CC BY-SA 4.0, é distribuída sob a mesma licença,
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br). Não é uma tradução revisada
por especialista.

## Textos latinos — `docs/textos/*.json` (texto)

Perseus Digital Library, [canonical-latinLit](https://github.com/PerseusDL/canonical-latinLit),
CC BY-SA 4.0:

- César, *Commentarii de Bello Gallico*, ed. T. Rice Holmes (1914) — `phi0448.phi001.perseus-lat2.xml`
- Cícero, *In Catilinam*, ed. A. C. Clark (1905) — `phi0474.phi013.perseus-lat2.xml`
- Virgílio, *Aeneis*, ed. J. B. Greenough (1900) — `phi0690.phi003.perseus-lat2.xml`

Modificações: omissão das notas de aparato crítico; divisão em palavras; ligação a lemas e verbetes.

## Suma Teológica — `docs/textos/tomas-suma-*.json` (texto)

Tomás de Aquino, *Summa Theologiae*, partes I, I-II, II-II e III (até a q. 90; o *Supplementum* não está
incluído). Texto da edição leonina (Roma, 1888–1906), tomado da coluna latina das páginas bilíngues de
[Geremia/AquinasOperaOmnia](https://github.com/Geremia/AquinasOperaOmnia) (espelho do site de Joseph
Kenny, O.P.), pasta `summa/`, versão de abril de 2026. Nessa fonte faltam as colunas latinas de 17
questões (I-II q. 5; II-II qq. 6–9, 11, 12, 19–24, 103, 110, 115, 116); para elas o texto vem de
[AnthropologieBiblique/SummaTheologiae](https://github.com/AnthropologieBiblique/SummaTheologiae)
(Markdown por artigo, também com o texto leonino), com as referências bíblicas convertidas para a
forma abreviada usada no restante do texto (*Matth. XX*). Esse repositório também não declara licença.

**Ponto a verificar antes de uso comercial:** o texto de Tomás e o da edição leonina estão em domínio
público (inferência: a edição tem mais de 100 anos). A transcrição digital, porém, provavelmente vem do
Corpus Thomisticum (E. Alarcón, Universidad de Navarra), e o repositório de origem não declara licença
nem a procedência do latim (o mesmo vale para a fonte complementar). Para o uso atual, gratuito e com atribuição, não vemos impedimento; antes de
cobrar, convém confirmar os termos do Corpus Thomisticum ou trocar a fonte.

Modificações: divisão em arquivos por tratado; rótulos das partes do artigo (arg., s. c., co., ad);
divisão em palavras e ligação a lemas e verbetes. A análise morfológica usa, além do Morpheus, regras
próprias para o latim escolástico (abreviaturas de citação, compostos, grafias medievais), descritas em
`scripts/latim_medieval.py`.

## Suma contra os Gentios e De ente et essentia — `docs/textos/tomas-scg-*.json`, `docs/textos/tomas-de-ente.json`

Tomás de Aquino, *Summa contra Gentiles* (edição leonina, t. 13–15, 1918–1930) e *De ente et essentia*
(edição leonina, t. 43, 1976), tomados da coluna latina das páginas bilíngues de
[Geremia/AquinasOperaOmnia](https://github.com/Geremia/AquinasOperaOmnia) (`ContraGentiles1–4.htm`,
`DeEnte&Essentia.htm`). Valem as mesmas observações da Suma Teológica sobre a transcrição digital.
**Ponto a verificar antes de uso comercial (específico do De ente):** a edição leonina do *De ente* é de
1976 e pode ainda estar protegida como edição crítica em algumas jurisdições; isso é uma suposição a
verificar, não uma conclusão. Para a SCG, a edição tem mais de 90 anos (inferência: domínio público).

Modificações: divisão por livros e capítulos; numeração dos parágrafos tomada da coluna inglesa;
capítulos que a fonte funde ou deixa sem a linha “Caput N” (I 37 e 52; II 14, 19, 29 e 81) foram
separados pela numeração; alguns capítulos ficaram sem título latino porque a fonte não o traz.

## Léxico escolástico — `scripts/escolastico.py` e os campos de glosa nos textos de Tomás

Lista de cerca de 150 termos escolásticos ausentes do Lewis & Short ou do Morpheus (quidditas,
sensitivus, totaliter, causo…), com flexão gerada por regras e glosa em português **gerada por IA**
(Claude, da Anthropic), outubro de 2026. Distribuída sob CC BY-SA 4.0, como a camada em português.

## Morfologia — análises nos textos e `docs/data/formas.json`

Análises geradas pelo [Morpheus](https://github.com/perseids-tools/morpheus) (Perseus Digital Library;
software sob Mozilla Public License 2.0), obtidas do pacote de dados pré-compilados do
[Diogenes](https://github.com/pjheslin/diogenes-prebuilt-data) (P. J. Heslin), arquivo `latin-analyses.txt`.

**Ponto a verificar antes de uso comercial:** o repositório de dados do Diogenes não declara uma licença
própria, e a MPL 2.0 do Morpheus cobre o software, não explicitamente as análises que ele gera. Para o
uso atual, gratuito e com atribuição, não vemos impedimento; antes de cobrar pelo site ou por um app,
convém confirmar com os mantenedores (Perseus e P. J. Heslin) ou regenerar as análises com o próprio
Morpheus.

## Gaffiot

O dicionário de Félix Gaffiot **não** é reproduzido aqui. O botão “ver no Gaffiot” apenas abre a
palavra no site externo gaffiot.fr.
