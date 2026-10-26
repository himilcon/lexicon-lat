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
