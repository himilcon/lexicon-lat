/* Lexicon — dicionário latim · português.
   Verbetes: Lewis & Short, A Latin Dictionary (1879), digitalização da Perseus Digital Library, CC BY-SA 4.0.
   Camada PT: tradução das glosas gerada por IA (Claude), também CC BY-SA 4.0 (obra derivada). */
"use strict";

const DATA_VER = "ls-2026-10-1";
const INDEX_URL = `data/index.json?v=${DATA_VER}`;
const PT_URL = "data/pt.json";
const FORMS_URL = `data/formas.json?v=${DATA_VER}`;
const PAGE = 100;

const $ = (s, el = document) => el.querySelector(s);
const main = $("#main");
const qInput = $("#q");
const hint = $("#hint");

let E = [];            // [id, chave, cabeçalho, gramática, glosa EN, bloco, tamanho do verbete]
let BLOCK = 500;
let byId = new Map();  // id -> índice em E
let keys = [];         // chave normalizada (sem número de homônimo)
let PT = {};           // id -> glosa em português
let ptVer = "";
let ptIndex = null, enIndex = null;   // textos normalizados (busca reversa, criados sob demanda)
let FORMS = null;      // forma normalizada -> [índices], carregado sob demanda
let formsLoading = null;
const chunkCache = new Map();

/* ---------- normalização ---------- */

function normLa(s) {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
    .replace(/j/g, "i").replace(/v/g, "u").replace(/æ/g, "ae").replace(/œ/g, "oe").replace(/[^a-z]/g, "");
}
function normTxt(s) {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/* ---------- dados ---------- */

async function fetchWithProgress(url, onPct) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("HTTP " + res.status);
  if (!res.body || !res.body.getReader) return res.json();
  const total = +res.headers.get("content-length") || 0;
  const reader = res.body.getReader();
  const chunks = [];
  let got = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value); got += value.length;
    if (onPct) onPct(total ? `(${Math.min(100, Math.round(got / total * 100))}%)` : `(${(got / 1048576).toFixed(1)} MB)`);
  }
  const buf = new Uint8Array(got);
  let off = 0;
  for (const c of chunks) { buf.set(c, off); off += c.length; }
  return JSON.parse(new TextDecoder("utf-8").decode(buf));
}

function buildIndex(data) {
  E = data.entries;
  BLOCK = data.bloco || 500;
  E.forEach((e, i) => {
    byId.set(e[0], i);
    keys[i] = normLa(e[1].replace(/\d+$/, ""));
  });
}

async function loadPT() {
  try {
    const res = await fetch(PT_URL, { cache: "no-cache" }).catch(() => fetch(PT_URL));
    if (!res.ok) return;
    const d = await res.json();
    PT = d.pt || {};
    ptVer = d.versao || "";
  } catch { /* sem camada PT: mostra só o inglês */ }
}

function loadForms() {
  if (FORMS) return Promise.resolve(FORMS);
  if (!formsLoading) formsLoading = fetch(FORMS_URL).then(r => r.json()).then(d => {
    const m = new Map();
    for (const id in d) {
      const i = byId.get(id);
      if (i === undefined) continue;
      for (const f of d[id].split(" ")) {
        const l = m.get(f);
        if (l) { if (!l.includes(i)) l.push(i); } else m.set(f, [i]);
      }
    }
    FORMS = m;
    return m;
  }).catch(() => { formsLoading = null; return null; });
  return formsLoading;
}

/* corpo do verbete (HTML do L&S), em blocos de 500 verbetes carregados sob demanda */
async function entryHtml(i) {
  const b = E[i][5];
  if (!chunkCache.has(b)) {
    chunkCache.set(b, fetch(`data/ls/${String(b).padStart(3, "0")}.json?v=${DATA_VER}`).then(r => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }).catch(err => { chunkCache.delete(b); throw err; }));
  }
  const chunk = await chunkCache.get(b);
  return chunk[E[i][0]] || "";
}

const ptOf = i => PT[E[i][0]] || "";
const homNum = i => (/(\d+)$/.exec(E[i][1]) || [])[1] || "";

/* ---------- busca ---------- */

function searchLatin(qn) {
  if (!qn) return [];
  const out = [];
  for (let i = 0; i < E.length; i++) {
    const k = keys[i];
    let s = -1;
    if (k === qn) s = 0;
    else if (k.startsWith(qn)) s = 2;
    else if (qn.length >= 3 && k.includes(qn)) s = 4;
    if (s >= 0) out.push([s, i]);
  }
  if (FORMS) {
    const f = FORMS.get(qn);
    if (f) for (const i of f) if (keys[i] !== qn) out.push([1, i]);
  }
  // mesmo nível: verbetes mais longos (palavras mais comuns) primeiro, depois os mais curtos
  out.sort((a, b) => a[0] - b[0] || (a[0] <= 1 ? (E[b[1]][6] || 0) - (E[a[1]][6] || 0) : 0) ||
    keys[a[1]].length - keys[b[1]].length || a[1] - b[1]);
  const seen = new Set();
  return out.filter(x => !seen.has(x[1]) && seen.add(x[1])).map(x => x[1]);
}

function searchGloss(q, lang) {
  const words = normTxt(q).split(/[^a-z0-9À-ɏ]+/).filter(w => w.length >= 2);
  if (!words.length) return [];
  let idx;
  if (lang === "por") { if (!ptIndex) ptIndex = E.map((e, i) => normTxt(ptOf(i))); idx = ptIndex; }
  else { if (!enIndex) enIndex = E.map(e => normTxt(e[4])); idx = enIndex; }
  const res = words.map(w => new RegExp("(^|[^a-z0-9])" + reEsc(w), ""));
  const w0 = reEsc(words[0]);
  const r0 = new RegExp("^(to |a |an |the |o |a |os |as |um |uma )?" + w0 + "([;,.]|$)");
  const r1 = new RegExp("(^|; )(to |a |an |the |o |a |um |uma )?" + w0 + "([;,. ]|$)");
  const r2 = new RegExp("(^|[^a-z0-9])" + w0 + "([^a-z0-9]|$)");
  const out = [];
  for (let i = 0; i < E.length; i++) {
    const h = idx[i];
    if (!h) continue;
    let first = Infinity, ok = true;
    for (const re of res) {
      const m = re.exec(h);
      if (!m) { ok = false; break; }
      first = Math.min(first, m.index);
    }
    if (ok) {
      const rank = r0.test(h) ? 0 : r1.test(h) ? 1 : r2.test(h) ? 2 : 3;
      out.push([rank, first, i]);
    }
  }
  out.sort((a, b) => a[0] - b[0] || (E[b[2]][6] || 0) - (E[a[2]][6] || 0) || a[1] - b[1]);
  return out.map(x => x[2]);
}

/* ---------- renderização ---------- */

function headHtml(i) {
  const n = homNum(i);
  return esc(E[i][2]) + (n ? `<sup>${n}</sup>` : "");
}

function glossLine(i) {
  const pt = ptOf(i);
  if (pt) return esc(pt);
  return E[i][4] ? `<span class="en">${esc(E[i][4])}</span>` : "";
}

function resultList(idxs, opts = {}) {
  const shown = idxs.slice(0, opts.limit || PAGE);
  const mark = opts.mark ? new RegExp("(" + reEsc(opts.mark) + ")", "i") : null;
  const items = shown.map(i => {
    let gl = opts.lang === "eng" ? `<span class="en">${esc(E[i][4])}</span>` : glossLine(i);
    if (mark) gl = gl.replace(mark, "<mark>$1</mark>");
    const form = opts.forms && opts.forms.has(i) ? `<span class="fm">forma de</span> ` : "";
    return `<li><a href="#/v/${E[i][0]}"><span class="hw">${form}${headHtml(i)}<span class="gm">${esc(E[i][3])}</span></span><span class="gl">${gl}</span></a></li>`;
  }).join("");
  return `<ul class="results">${items}</ul>` +
    (idxs.length > shown.length ? `<button class="more" data-more="${shown.length + PAGE}">Mostrar mais (${idxs.length - shown.length} restantes)</button>` : "");
}

/* ---------- estado local (favoritos, histórico) ---------- */

const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* sem armazenamento */ } },
};
const favs = () => store.get("lt.favs", []);
function toggleFav(id) {
  const f = favs(); const p = f.indexOf(id);
  if (p >= 0) f.splice(p, 1); else f.unshift(id);
  store.set("lt.favs", f); return p < 0;
}
function pushHistory(id) {
  const h = store.get("lt.hist", []).filter(x => x !== id);
  h.unshift(id); store.set("lt.hist", h.slice(0, 30));
}

/* ---------- páginas ---------- */

const ALPHA = "ABCDEFGHIJKLMNOPQRSTUVXYZ";

function viewHome() {
  setActiveLetter(null);
  const hist = store.get("lt.hist", []).map(id => byId.get(id)).filter(i => i !== undefined);
  const chip = i => `<a href="#/v/${E[i][0]}">${headHtml(i)}</a>`;
  const examples = ["amo", "virtus", "animus", "res", "fortuna", "pietas", "lupus", "amabant", "arma", "cano"]
    .map(w => `<a href="#/lat/${encodeURIComponent(w)}">${w}</a>`).join("");
  const nPT = Object.keys(PT).length;
  main.innerHTML = `
    <p class="home-intro">${E.length.toLocaleString("pt-BR")} verbetes do <i>Latin Dictionary</i> de Lewis &amp; Short (1879), em inglês,
      com a tradução das acepções principais para o português em ${nPT.toLocaleString("pt-BR")} deles.
      Digite a palavra latina, com ou sem quantidades (<i>amo</i>, <i>ămo</i>), ou uma forma flexionada (<i>amabant</i>, <i>virum</i>).
      Para buscar pelo significado, escolha <b>Português</b> ou <b>Inglês</b>.</p>
    ${hist.length ? `<h3 class="count">Consultados recentemente</h3><div class="chips">${hist.slice(0, 15).map(chip).join("")}</div>` : ""}
    <h3 class="count">Experimente</h3><div class="chips">${examples}<a href="#/acaso">ao acaso ↻</a></div>
    <h3 class="count">Ler textos</h3>
    <a class="home-texts" href="#/textos"><span lang="la">Caesar · Cicero · Vergilius · Thomas de Aquino</span>
      <span>César (<i>A Guerra da Gália</i>), Cícero (<i>Catilinárias</i>), Virgílio (<i>Eneida</i>) e Tomás de Aquino (<i>Suma Teológica</i>, <i>Suma contra os Gentios</i>, <i>O ente e a essência</i>):
        toque em cada palavra para ver lema, análise e verbete →</span></a>`;
}

function viewSearch(mode, q) {
  setActiveLetter(null);
  if (qInput.value !== q && document.activeElement !== qInput) qInput.value = q;
  setMode(mode);
  hint.innerHTML = "";
  if (!q.trim()) { viewHome(); return; }
  if (mode === "por" || mode === "eng") {
    const idxs = searchGloss(q, mode);
    const w = normTxt(q).split(/[^a-z0-9À-ɏ]+/).filter(x => x.length >= 2)[0];
    if (mode === "por" && Object.keys(PT).length) hint.innerHTML = `A busca em português cobre só os verbetes já traduzidos · <a href="#/eng/${encodeURIComponent(q)}">buscar “${esc(q)}” em inglês</a>`;
    renderResults(idxs, { mark: null, lang: mode }, "verbetes");
    return;
  }
  const qn = normLa(q);
  const run = () => {
    const idxs = searchLatin(qn);
    const forms = new Set();
    if (FORMS && FORMS.get(qn)) for (const i of FORMS.get(qn)) if (keys[i] !== qn) forms.add(i);
    renderResults(idxs, { forms }, "verbetes");
  };
  run();
  if (!FORMS && qn.length >= 2) loadForms().then(f => { if (f && location.hash.startsWith("#/lat/") && normLa(qInput.value) === qn) run(); });
}

function renderResults(idxs, opts, what) {
  if (!idxs.length) { main.innerHTML = `<div class="empty">Nenhum resultado.</div>`; return; }
  const draw = (limit) => {
    main.innerHTML = `<div class="count">${idxs.length.toLocaleString("pt-BR")} ${what}</div>` + resultList(idxs, { ...opts, limit });
    const more = $(".more", main);
    if (more) more.onclick = () => { const y = scrollY; draw(+more.dataset.more); scrollTo(0, y); };
  };
  draw(PAGE);
}

const gaffiotUrl = i => "https://gaffiot.fr/#" + encodeURIComponent(E[i][1].replace(/\d+$/, ""));
const logeionUrl = i => "https://logeion.uchicago.edu/" + encodeURIComponent(E[i][1].replace(/\d+$/, ""));

function ptBox(i, compact) {
  const pt = ptOf(i), en = E[i][4];
  if (pt) return `<div class="ptbox"><div class="pt-txt">${esc(pt)}</div>
    ${compact ? "" : `<div class="pt-note">Tradução das acepções principais gerada por IA a partir do inglês; confira no verbete original abaixo.</div>`}</div>`;
  if (en) return `<div class="ptbox none"><div class="pt-en">${esc(en)}</div>
    <div class="pt-note">Resumo em inglês. A tradução para o português deste verbete ainda não foi gerada.</div></div>`;
  return "";
}

function viewEntry(id, fromLink) {
  const i = byId.get(String(id));
  if (i === undefined) { main.innerHTML = `<div class="empty">Verbete não encontrado.</div>`; return; }
  const e = E[i];
  pushHistory(e[0]);
  const prev = i > 0 ? i - 1 : null;
  const next = i < E.length - 1 ? i + 1 : null;
  const isFav = favs().includes(e[0]);
  setActiveLetter(letterOf(i));
  main.innerHTML = `
    <article class="entry" lang="en">
      <div class="entry-head">
        <h1 lang="la">${headHtml(i)}</h1>
        <button class="star ${isFav ? "on" : ""}" id="star" aria-pressed="${isFav}" title="Favorito">★</button>
      </div>
      ${e[3] ? `<div class="gram" lang="la">${esc(e[3])}</div>` : ""}
      <div lang="pt">${ptBox(i)}</div>
      <div class="ext"><a href="${gaffiotUrl(i)}" target="_blank" rel="noopener">ver no Gaffiot ↗</a>
        <a href="${logeionUrl(i)}" target="_blank" rel="noopener">Logeion ↗</a></div>
      <h2 class="ls-title">Lewis &amp; Short</h2>
      <div class="lsdef" id="lsdef"><p class="muted">carregando o verbete…</p></div>
      <nav class="entry-nav">
        ${prev !== null ? `<a href="#/v/${E[prev][0]}">← ${headHtml(prev)}</a>` : "<span></span>"}
        ${next !== null ? `<a href="#/v/${E[next][0]}">${headHtml(next)} →</a>` : "<span></span>"}
      </nav>
      <div class="entry-meta">Lewis &amp; Short, verbete n${esc(e[0])} · <button class="btn-link" id="share">copiar link</button></div>
    </article>`;
  entryHtml(i).then(h => {
    const box = $("#lsdef");
    if (box && location.hash.replace(/^#\/v\//, "") === String(e[0])) box.innerHTML = h || `<p class="muted">(verbete vazio)</p>`;
  }).catch(() => { const box = $("#lsdef"); if (box) box.innerHTML = `<p class="muted">Não foi possível carregar o verbete. Verifique a conexão.</p>`; });
  $("#star").onclick = ev => {
    const on = toggleFav(e[0]);
    ev.currentTarget.classList.toggle("on", on);
    ev.currentTarget.setAttribute("aria-pressed", on);
  };
  $("#share").onclick = async ev => {
    const url = location.href;
    try {
      if (navigator.share && matchMedia("(pointer: coarse)").matches) await navigator.share({ title: e[2], url });
      else { await navigator.clipboard.writeText(url); ev.target.textContent = "link copiado"; }
    } catch { /* cancelado */ }
  };
  if (!fromLink) scrollTo(0, 0);
}

function letterOf(i) {
  const c = E[i][1].normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/^[^A-Za-z]+/, "")[0];
  return c ? c.toUpperCase() : null;
}

function viewLetter(L) {
  setActiveLetter(L);
  const idxs = [];
  for (let i = 0; i < E.length; i++) if (letterOf(i) === L) idxs.push(i);
  renderResults(idxs, {}, `verbetes em ${L}`);
}

function viewFavs() {
  setActiveLetter(null);
  const f = favs().map(id => byId.get(id)).filter(i => i !== undefined);
  main.innerHTML = `<div class="page"><h2>Favoritos</h2>` +
    (f.length ? resultList(f, { limit: 1000 }) : `<p class="empty">Toque em ★ num verbete para guardá-lo aqui. Os favoritos ficam salvos neste aparelho.</p>`) + `</div>`;
}

function viewAbout() {
  setActiveLetter(null);
  const nPT = Object.keys(PT).length;
  main.innerHTML = `<div class="page">
    <h2>Sobre</h2>
    <p>Este site é uma interface de consulta ao <i>A Latin Dictionary</i> de Charlton T. Lewis e Charles Short
      (Oxford: Clarendon Press, 1879), o “Lewis &amp; Short”, na digitalização da
      <a href="https://github.com/PerseusDL/lexica" target="_blank" rel="noopener">Perseus Digital Library</a> (Tufts University).
      Os verbetes são mostrados em inglês, como no original; a conversão do TEI-XML para HTML não altera o conteúdo.</p>
    <p class="attr">Text provided under a CC BY-SA license by Perseus Digital Library, http://www.perseus.tufts.edu,
      with funding from The National Endowment for the Humanities. Data accessed from https://github.com/PerseusDL/lexica/ [outubro de 2026].</p>

    <h3>A camada em português</h3>
    <p>No alto de cada verbete aparece um resumo das acepções principais em português. Ele foi gerado por inteligência artificial
      (Claude, da Anthropic) a partir das glosas inglesas do próprio Lewis &amp; Short ou, para o vocabulário mais comum, do
      <i>Elementary Latin Dictionary</i> de Lewis (1890), também digitalizado pela Perseus. É um auxílio de leitura, não uma
      tradução revisada: confira sempre no verbete original. ${nPT.toLocaleString("pt-BR")} verbetes já têm a tradução${ptVer ? ` (versão ${esc(ptVer)})` : ""};
      a prioridade foi o vocabulário dos textos do leitor. Nos demais aparece o resumo em inglês.</p>
    <p>Por ser obra derivada, a camada em português segue a mesma licença dos dados:
      <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br" target="_blank" rel="noopener">CC BY-SA 4.0</a>.</p>

    <h3>Como buscar</h3>
    <p><b>Latim</b>: digite a palavra com ou sem quantidades (<i>ămo</i> ou <i>amo</i>); <i>j</i> e <i>i</i>, <i>v</i> e <i>u</i> são equivalentes.
      Formas flexionadas também funcionam (<i>amabant</i> → <i>amo</i>, <i>virum</i> → <i>vir</i>), graças às análises do Morpheus.</p>
    <p><b>Português</b> procura nas traduções; <b>Inglês</b>, nos resumos ingleses (todas as palavras digitadas precisam aparecer).</p>
    <p>O botão <b>ver no Gaffiot</b> abre a palavra no <i>Dictionnaire latin-français</i> de Félix Gaffiot, no site externo gaffiot.fr;
      o Gaffiot não é reproduzido aqui. <b>Logeion</b> (Universidade de Chicago) reúne vários dicionários.</p>

    <h3>Textos</h3>
    <p>Em <a href="#/textos">Textos</a>, cada palavra é clicável: o painel mostra os lemas possíveis, a análise morfológica e a tradução.
      Texto latino da Perseus (<a href="https://github.com/PerseusDL/canonical-latinLit" target="_blank" rel="noopener">canonical-latinLit</a>, CC BY-SA 4.0).
      As análises vêm do <a href="https://github.com/perseids-tools/morpheus" target="_blank" rel="noopener">Morpheus</a> (Perseus) e são feitas palavra
      por palavra, sem levar em conta o contexto: a primeira análise é só a mais provável. No teclado: <code>←</code> <code>→</code> mudam de palavra,
      <code>Esc</code> fecha o painel. O campo de referência leva a uma passagem: <code>1.1.1</code> em César, <code>1.1</code> nas
      Catilinárias, <code>6.851</code> na Eneida; links como <code>…/#/t/virgilio-eneida/6.851</code> também funcionam.</p>
    <p>A <i>Suma Teológica</i> de Tomás de Aquino (edição leonina) está dividida por tratados, em
      <a href="#/obra/tomas-suma">página própria</a>. Cada parágrafo traz a parte do artigo: <i>arg.</i> (objeção), <i>s. c.</i>
      (sed contra), <i>co.</i> (corpo, “Respondeo”) e <i>ad</i> (resposta às objeções). As referências aceitam a forma usual:
      <code>I q. 2 a. 3</code>, <code>I-II 90.4</code>, <code>III q. 75</code>. Para o latim escolástico, a análise acrescenta ao Morpheus
      regras próprias: abreviaturas de citação (<i>Ethic.</i>, <i>Matth.</i>), compostos (<i>inquantum</i>, <i>huiusmodi</i>),
      grafias medievais (<i>poenitentia</i>) e formas registradas no Lewis &amp; Short mas ausentes do Morpheus.</p>
    <p>A <i>Suma contra os Gentios</i> está dividida por livros, também em <a href="#/obra/tomas-scg">página própria</a>; cite como
      <code>III, 65</code> ou <code>3.65</code>. <i>O ente e a essência</i> é um texto único, por capítulos (<code>4</code>).
      Os termos escolásticos que não estão no Lewis &amp; Short (<i>quidditas</i>, <i>sensitivus</i>, <i>totaliter</i>, <i>causo</i>…)
      vêm de um pequeno léxico próprio, com glosa em português gerada por IA.</p>

    <h3>Instalar no iPhone / iPad</h3>
    <p>No Safari, toque em <b>Compartilhar</b> → <b>Adicionar à Tela de Início</b>. Os verbetes abertos e os textos lidos ficam guardados para uso sem internet.</p>

    <h3>Tema</h3>
    <p><button class="btn-link" data-theme-set="">automático</button> · <button class="btn-link" data-theme-set="light">claro</button> · <button class="btn-link" data-theme-set="dark">escuro</button></p>
  </div>`;
  main.querySelectorAll("[data-theme-set]").forEach(b => b.onclick = () => setTheme(b.dataset.themeSet));
}

function viewRandom() {
  // ao acaso entre os verbetes com tradução, se houver
  const ids = Object.keys(PT);
  const id = ids.length ? ids[Math.floor(Math.random() * ids.length)] : E[Math.floor(Math.random() * E.length)][0];
  location.replace("#/v/" + id);
}

/* ---------- roteamento ---------- */

function route() {
  const h = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  const [r, ...rest] = h.split("/");
  const arg = rest.join("/");
  if (!["lat", "por", "eng"].includes(r)) hint.innerHTML = "";
  if (r !== "t" && typeof leaveReader === "function") leaveReader();
  switch (r) {
    case "textos": viewTexts(); break;
    case "obra": viewObra(arg); break;
    case "t": viewReader(rest[0], rest.slice(1).join("/")); break;
    case "v": viewEntry(arg); break;
    case "lat": case "por": case "eng": viewSearch(r, arg); break;
    case "l": viewLetter(arg); break;
    case "favoritos": viewFavs(); break;
    case "sobre": viewAbout(); break;
    case "acaso": viewRandom(); break;
    default: qInput.value = ""; viewHome();
  }
}

function currentMode() { return $('input[name="mode"]:checked').value; }
function setMode(m) { const r = $(`input[name="mode"][value="${m}"]`); if (r) r.checked = true; }
function setActiveLetter(L) {
  document.querySelectorAll(".alphabet a").forEach(a => a.classList.toggle("on", a.dataset.l === L));
}
function setTheme(t) {
  if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme;
  store.set("lt.theme", t || "");
}

let tmr;
function onType() {
  clearTimeout(tmr);
  tmr = setTimeout(() => {
    const q = qInput.value;
    const target = q.trim() ? `#/${currentMode()}/${encodeURIComponent(q)}` : "#/";
    const fromSearch = /^#\/(lat|por|eng)\//.test(location.hash);
    if (fromSearch || !q.trim()) history.replaceState(null, "", target); else history.pushState(null, "", target);
    route();
  }, 140);
}

/* ---------- início ---------- */

async function start() {
  const t = store.get("lt.theme", "");
  if (t) document.documentElement.dataset.theme = t;

  $("#alphabet").innerHTML = [...ALPHA].map(L => `<a href="#/l/${L}" data-l="${L}">${L}</a>`).join("");

  qInput.addEventListener("input", onType);
  document.querySelectorAll('input[name="mode"]').forEach(r => r.addEventListener("change", () => {
    if (qInput.value.trim()) onType();
    qInput.focus();
  }));
  $("#search-form").addEventListener("submit", ev => {
    ev.preventDefault();
    const first = $(".results a", main);
    if (first) { qInput.blur(); location.hash = first.getAttribute("href"); }
  });
  document.addEventListener("keydown", ev => {
    if (ev.key === "/" && document.activeElement !== qInput && !(ev.target.closest && ev.target.closest("input"))) {
      ev.preventDefault(); qInput.focus(); qInput.select();
    }
  });

  try {
    const [idx] = await Promise.all([fetchWithProgress(INDEX_URL, p => { $("#load-pct").textContent = p; }), loadPT()]);
    buildIndex(idx);
  } catch (err) {
    main.innerHTML = `<div class="empty">Não foi possível carregar o dicionário (${esc(String(err.message || err))}).<br>Verifique a conexão e recarregue a página.</div>`;
    return;
  }
  addEventListener("hashchange", route);
  route();

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
}

start();
