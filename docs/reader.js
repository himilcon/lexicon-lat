/* Lexicon — leitor de textos latinos com cada palavra ligada ao dicionário.
   Texto: Perseus Digital Library, canonical-latinLit (CC BY-SA 4.0). Lemas e morfologia: Morpheus (Perseus),
   por consulta de formas, sem desambiguação pelo contexto. Usa as variáveis e funções globais de app.js. */
"use strict";

const TEXTS_URL = "textos/index.json";
let textIndex = null;
const textCache = new Map();
let R = null;                  // estado do leitor aberto

/* ---------- morfologia (análises do Morpheus em inglês → português) ---------- */

const MT = {
  pres: "presente", imperf: "imperfeito", fut: "futuro", perf: "perfeito", plup: "mais-que-perfeito", futperf: "futuro perfeito",
  ind: "do indicativo", subj: "do subjuntivo", imperat: "do imperativo", inf: "infinitivo", part: "particípio",
  gerundive: "gerundivo", supine: "supino", act: "voz ativa", pass: "voz passiva",
  "1st": "1ª pessoa", "2nd": "2ª pessoa", "3rd": "3ª pessoa", sg: "singular", pl: "plural",
  comp: "comparativo", superl: "superlativo", adverbial: "advérbio",
};
const GEN = { masc: "masculino", fem: "feminino", neut: "neutro" };
const CAS = { nom: "nominativo", gen: "genitivo", dat: "dativo", acc: "acusativo", voc: "vocativo", abl: "ablativo" };
const INDECL = { adverb: "advérbio", conj: "conjunção", prep: "preposição", exclam: "interjeição", numeral: "numeral", indecl: "invariável", indef: "indefinido" };

function slash(s, map) {
  return s.split("/").map(x => map[x] || x).join(" ou ");
}

const readingsRaw = s => (s || "").split("|");

function morphPT(m) {
  if (!m) return "";
  if (m === "enclitic") return "partícula enclítica, unida à palavra";
  if (m === "roman") return "algarismo romano";
  if (m === "abbreviation") return "abreviatura de prenome";
  if (m === "citation") return "abreviatura numa citação";
  if (m.startsWith("compound")) return "parte de palavra composta" + (m.includes(":") ? " (" + m.split(":")[1] + ")" : "");
  if (m === "lsonly") return "forma de dicionário (sem análise morfológica do Morpheus)";
  if (m === "guess") return "forma não reconhecida pelo Morpheus; lema provável";
  const ind = /^indeclform \(([^)]+)\)/.exec(m);
  if (ind) return INDECL[ind[1]] || "invariável";
  const t = m.split(/\s+/);
  const out = [];
  const verbal = t.some(x => ["ind", "subj", "imperat", "inf", "part", "gerundive", "supine"].includes(x));
  if (verbal) {
    const tense = t.find(x => ["pres", "imperf", "fut", "perf", "plup", "futperf"].includes(x));
    const mood = t.find(x => ["ind", "subj", "imperat", "inf", "part", "gerundive", "supine"].includes(x));
    const voice = t.find(x => x === "act" || x === "pass");
    if (mood === "inf" || mood === "part") out.push([MT[mood], tense && MT[tense]].filter(Boolean).join(" "));
    else if (mood === "gerundive" || mood === "supine") out.push(MT[mood]);
    else out.push([tense && MT[tense], MT[mood]].filter(Boolean).join(" "));
    if (voice) out.push(MT[voice]);
    const pers = t.find(x => /^[123](st|nd|rd)$/.test(x));
    const num = t.find(x => x === "sg" || x === "pl");
    if (pers) out.push(MT[pers] + " do " + MT[num]);
    const g = t.find(x => /^(masc|fem|neut)/.test(x));
    const c = t.find(x => /^(nom|gen|dat|acc|voc|abl)/.test(x));
    if (g || c) out.push([g && slash(g, GEN), c && slash(c, CAS), !pers && num && MT[num]].filter(Boolean).join(" "));
  } else {
    const g = t.find(x => /^(masc|fem|neut)/.test(x));
    const c = t.find(x => /^(nom|gen|dat|acc|voc|abl)/.test(x));
    const num = t.find(x => x === "sg" || x === "pl");
    out.push([g && slash(g, GEN), c && slash(c, CAS), num && MT[num]].filter(Boolean).join(" "));
    for (const x of t) if (["comp", "superl", "adverbial"].includes(x)) out.push(MT[x]);
  }
  return out.filter(Boolean).join(" · ");
}

/* ---------- carregamento ---------- */

async function loadTextIndex() {
  if (textIndex) return textIndex;
  const res = await fetch(TEXTS_URL, { cache: "no-cache" }).catch(() => fetch(TEXTS_URL));
  if (!res.ok) throw new Error("HTTP " + res.status);
  textIndex = await res.json();
  return textIndex;
}

async function loadText(id) {
  if (textCache.has(id)) return textCache.get(id);
  const meta = (await loadTextIndex()).textos.find(t => t.id === id);
  if (!meta) throw new Error("texto não encontrado");
  const res = await fetch(`textos/${id}.json?v=${meta.versao}`);
  if (!res.ok) throw new Error("HTTP " + res.status);
  const doc = await res.json();
  doc.words = [];
  for (const b of doc.blocos) for (const it of b.x || []) if (Array.isArray(it)) doc.words.push(it);
  // ocorrências pelo lema mais provável de cada palavra
  doc.byLemma = new Map();
  doc.words.forEach((w, i) => {
    const a = w[1][0];
    if (!a) return;
    if (!doc.byLemma.has(a[0])) doc.byLemma.set(a[0], []);
    doc.byLemma.get(a[0]).push(i);
  });
  indexText(doc);
  textCache.set(id, doc);
  return doc;
}

/* Divide o texto em partes (livros, discursos) e indexa as referências → parte */
function indexText(doc) {
  doc.parts = [];
  doc.refPart = new Map(); doc.refs = [];
  let wi = 0, cur = null;
  const addRef = r => { if (r && !doc.refPart.has(r.toLowerCase())) { doc.refPart.set(r.toLowerCase(), doc.parts.length - 1); doc.refs.push(r); } };
  doc.blocos.forEach((b, bi) => {
    if (b.t === "c" && b.lv === 0) {
      if (cur) cur.b1 = bi;
      cur = { b0: bi, b1: doc.blocos.length, wStart: wi, c: b.c, rot: b.rot || b.c, chip: b.chip || b.c, chapters: [] };
      doc.parts.push(cur);
      addRef(b.c);
      return;
    }
    if (!cur) {
      cur = { b0: 0, b1: doc.blocos.length, wStart: 0, c: "", rot: "", chip: "", chapters: [] };
      doc.parts.push(cur);
    }
    if (b.t === "c") {
      cur.chapters.push({ c: b.c, chip: b.chip || b.c });
      addRef(b.c);
      return;
    }
    b.w0 = wi;
    for (const it of b.x || []) {
      if (Array.isArray(it)) wi++;
      else if (it && it.s) addRef(it.s);
    }
  });
}

/* ---------- biblioteca ---------- */

async function viewTexts() {
  setActiveLetter(null);
  document.body.classList.remove("reading");
  main.innerHTML = `<div class="loading"><div>Carregando a biblioteca…</div></div>`;
  let idx;
  try { idx = await loadTextIndex(); } catch (err) {
    main.innerHTML = `<div class="empty">Não foi possível carregar a lista de textos (${esc(String(err.message || err))}).</div>`;
    return;
  }
  let lastAuthor = null;
  const obras = new Map((idx.obras || []).map(o => [o.id, o]));
  const shown = new Set();
  const items = [];
  for (const t of idx.textos) {
    if (t.obra && obras.has(t.obra)) {
      if (!shown.has(t.obra)) { shown.add(t.obra); items.push({ ...obras.get(t.obra), isObra: true }); }
    } else items.push(t);
  }
  const cards = items.map(t => {
    if (t.isObra) {
      const head = t.autor !== lastAuthor ? `<li class="tauthor" lang="pt">${esc(t.autor)} <span lang="la">${esc(t.autorLa)}</span></li>` : "";
      lastAuthor = t.autor;
      return head + `<li class="tcard">
      <a href="#/obra/${t.id}">
        <span class="tcard-gr" lang="la">${esc(t.tituloLa)}</span>
        <span class="tcard-pt">${esc(t.autor)}, <i>${esc(t.titulo)}</i></span>
        <span class="tcard-desc">${esc(t.descricao)}</span>
        <span class="tcard-meta">${esc(t.edicaoCurta)} · ${t.palavras.toLocaleString("pt-BR")} palavras · ${esc(t.divisao || "em partes")} →</span>
      </a></li>`;
    }
    const head = t.autor !== lastAuthor ? `<li class="tauthor" lang="pt">${esc(t.autor)} <span lang="la">${esc(t.autorLa)}</span></li>` : "";
    lastAuthor = t.autor;
    const pos = store.get("lt.read." + t.id, null);
    return head + `<li class="tcard">
      <a href="#/t/${t.id}">
        <span class="tcard-gr" lang="la">${esc(t.tituloLa)}</span>
        <span class="tcard-pt">${esc(t.autor)}, <i>${esc(t.titulo)}</i></span>
        <span class="tcard-desc">${esc(t.descricao)}</span>
        <span class="tcard-meta">${t.edicaoCurta ? esc(t.edicaoCurta) + " · " : ""}${t.palavras.toLocaleString("pt-BR")} palavras${pos ? ` · parou em ${esc(pos)}` : ""}</span>
      </a></li>`;
  }).join("");
  main.innerHTML = `<div class="page">
    <h2>Textos</h2>
    <p class="home-intro">Toque numa palavra para ver os lemas possíveis, a análise morfológica e o verbete do dicionário.
      As análises vêm do <a href="https://github.com/perseids-tools/morpheus" target="_blank" rel="noopener">Morpheus</a> (Perseus)
      e são feitas palavra por palavra, sem olhar o contexto: a primeira é só a mais provável, e o painel mostra as outras.</p>
    <ul class="tlist">${cards}</ul>
  </div>`;
}

/* ---------- página de uma obra dividida em vários arquivos (as Sumas) ---------- */

async function viewObra(id) {
  setActiveLetter(null);
  document.body.classList.remove("reading");
  let idx;
  try { idx = await loadTextIndex(); } catch (err) {
    main.innerHTML = `<div class="empty">Não foi possível carregar a lista de textos (${esc(String(err.message || err))}).</div>`;
    return;
  }
  const o = (idx.obras || []).find(x => x.id === id);
  if (!o) { main.innerHTML = `<div class="empty">Obra não encontrada.</div>`; return; }
  const parts = idx.textos.filter(t => t.obra === id);
  const ex = o.refExemplos || ["I q. 2 a. 3", "I-II 90.4"];
  let html = "", lastPars = null;
  for (const t of parts) {
    if (t.pars !== lastPars) {
      if (lastPars !== null) html += "</ul>";
      html += `<h3 class="obra-pars"><span lang="la">${esc(t.parsLa)}</span> · ${esc(t.parsPt)} (${esc(t.pars)})</h3><ul class="obra-list">`;
      lastPars = t.pars;
    }
    const pos = store.get("lt.read." + t.id, null);
    const [u1, u2] = o.unidade || ["q.", "qq."];
    const a = t.qmin === 0 ? "pr." : t.qmin;
    const rng = t.qmin === t.qmax ? `${u1} ${a}` : `${t.qmin === 0 ? "pr., " + u2 + " 1" : u2 + " " + a}–${t.qmax}`;
    html += `<li><a href="#/t/${t.id}"><span class="oq">${rng}</span><span class="ot">${esc(t.tratado)}</span>
      <span class="om">${t.palavras.toLocaleString("pt-BR")} palavras${pos ? ` · parou em ${esc(pos)}` : ""}</span></a></li>`;
  }
  if (lastPars !== null) html += "</ul>";
  main.innerHTML = `<div class="page">
    <a class="rback" href="#/textos">← Textos</a>
    <h2><span lang="la">${esc(o.tituloLa)}</span></h2>
    <p class="home-intro">${esc(o.autor)}, <i>${esc(o.titulo)}</i>. ${esc(o.descricao)}
      Cada parte abre separadamente. Para ir direto a um ponto, digite a referência abaixo (por exemplo ${ex.map(x => `<i>${esc(x)}</i>`).join(", ")}).</p>
    <form class="rgo" id="ogo"><input id="ogo-in" placeholder="${esc(ex[0])}" aria-label="Referência" autocomplete="off" spellcheck="false"><button>ir</button></form>
    ${html}
    ${o.notaFinal ? `<p class="rsrc">${esc(o.notaFinal)}</p>` : ""}
  </div>`;
  $("#ogo").addEventListener("submit", ev => {
    ev.preventDefault();
    const go = obraTarget($("#ogo-in").value, parts, null, id);
    if (go) location.hash = go; else toast(`Referência não encontrada. Use, por exemplo, ${ex.join(" ou ")}.`);
  });
}

/* "I-II q. 90 a. 4", "II-II 23.1", "q2a3", "2.3" → {pars, q, a} */
function parseSummaRef(t) {
  t = t.trim().replace(/[“”"]/g, "");
  let pars = null;
  const pm = /^(I-II|II-II|1-2|2-2|III|I)(?=[\s,.q\d]|$)\s*[,.]?\s*/i.exec(t);
  if (pm) {
    pars = { "1-2": "I-II", "2-2": "II-II" }[pm[1]] || pm[1].toUpperCase();
    t = t.slice(pm[0].length);
  }
  const m = /^(?:q(?:uaestio|u)?\.?\s*)?(\d+)(?:\s*[,.]?\s*(?:a(?:rt(?:iculus)?)?\.?\s*)?(\d+))?/i.exec(t.replace(/\s+/g, " "));
  if (!m) return null;
  return { pars, q: +m[1], a: m[2] ? +m[2] : null };
}

/* Suma contra os Gentios: "III, 65", "3.65", "l. 3 c. 65", "65" (no livro atual) → {pars, q} */
const SCG = "tomas-scg";
const ROM = { 1: "I", 2: "II", 3: "III", 4: "IV" }, ARAB = { I: 1, II: 2, III: 3, IV: 4 };
function parseScgRef(t) {
  t = t.trim().replace(/[“”"]/g, "").replace(/^(?:S\.?\s*)?C\.?\s*G\.?\s*/i, "");
  let pars = null;
  let m = /^(?:l(?:ib(?:er)?)?\.?\s*)?(IV|III|II|I)(?=[\s,.]|$)\s*[,.]?\s*/i.exec(t);
  if (m) pars = m[1].toUpperCase();
  else if ((m = /^(?:l(?:ib(?:er)?)?\.?\s*)?([1-4])(?:\s*[,.]\s*|\s+)(?=c|\d|p)/i.exec(t))) pars = ROM[m[1]];
  if (m) t = t.slice(m[0].length);
  const c = /^(?:c(?:ap(?:ut)?)?\.?\s*)?(\d+|pr(?:ol|ooemium)?\.?)/i.exec(t.trim());
  if (!c) return null;
  return { pars, q: /^\d/.test(c[1]) ? +c[1] : 0, a: null };
}

function obraRef(t, obra) { return obra === SCG ? parseScgRef(t) : parseSummaRef(t); }

function obraRefStr(obra, pars, r) {
  return obra === SCG ? `${ARAB[pars]}.${r.q === 0 ? "prol" : r.q}` : `${r.q}${r.a ? "." + r.a : ""}`;
}

function obraTarget(text, parts, curPars, obra) {
  const r = obraRef(text, obra);
  if (!r) return null;
  const pars = r.pars || curPars || "I";
  const t = parts.find(p => p.pars === pars && r.q >= p.qmin && r.q <= p.qmax);
  if (!t) return null;
  return `#/t/${t.id}/${obraRefStr(obra, pars, r)}`;
}

function summaTarget(text, parts, curPars) { return obraTarget(text, parts, curPars, "tomas-suma"); }

/* ---------- leitor ---------- */

async function viewReader(id, target) {
  setActiveLetter(null);
  document.body.classList.add("reading");
  if (!R || R.id !== id || !$("#rtext", main)) {
    // arquivos da Suma renomeados quando a divisão muda: leva o link antigo à questão certa
    const old = id.match(/^tomas-suma-(i|i-ii|ii-ii|iii)-q(\d+)$/);
    if (old) {
      const parts = (await loadTextIndex()).textos.filter(t => t.obra === "tomas-suma");
      if (!parts.some(t => t.id === id)) {
        const go = summaTarget(target || String(+old[2]), parts, old[1].toUpperCase());
        if (go) { location.replace(go); return; }
      }
    }
    main.innerHTML = `<div class="loading"><div class="loading-gr">legitur…</div><div>Carregando o texto</div></div>`;
    let doc;
    try { doc = await loadText(id); } catch (err) {
      main.innerHTML = `<div class="empty">Não foi possível carregar o texto (${esc(String(err.message || err))}).</div>`;
      return;
    }
    if (location.hash.split("/")[2] !== id) return;
    R = { id, doc, sel: -1, entry: null, part: -1, full: false, siblings: {} };
    if (doc.meta.obra) {
      const parts = (await loadTextIndex()).textos.filter(t => t.obra === doc.meta.obra);
      const k = parts.findIndex(t => t.id === id);
      R.siblings = { prev: parts[k - 1], next: parts[k + 1] };
    }
    renderReader();
  }
  const ref = target ? resolveRef(target) : null;
  if (target && !ref) {
    if (R.doc.meta.obra) {
      const parts = (await loadTextIndex()).textos.filter(t => t.obra === R.doc.meta.obra);
      const go = obraTarget(target, parts, R.doc.meta.pars, R.doc.meta.obra);
      if (go && !go.startsWith(`#/t/${R.id}/`)) { location.replace(go); return; }
    }
    showPart(R.part >= 0 ? R.part : 0);
    toast(`Referência “${target}” não encontrada neste texto.`);
    return;
  }
  if (ref) {
    showPart(R.doc.refPart.get(ref.toLowerCase()));
    const el = main.querySelector(`#rtext [data-s="${CSS.escape(ref)}"]`);
    if (el) { el.scrollIntoView({ block: "start" }); scrollBy(0, -scrollOffset()); flash(el.classList.contains("lnm") ? el.parentElement : el); }
  } else if (R.part < 0) {
    showPart(0);
    scrollTo(0, 0);
  }
}

function resolveRef(t) {
  const mo = R.doc.meta;
  if (mo.obra) {
    const r = obraRef(t, mo.obra);
    if (r && (!r.pars || r.pars === mo.pars)) t = obraRefStr(mo.obra, mo.pars, r);
    else if (r) return null;
  }
  t = t.trim().toLowerCase().replace(/\s+/g, "").replace(/,/g, ".");
  const { refPart, refs } = R.doc;
  if (refPart.has(t)) return t;
  return refs.find(r => r.toLowerCase().startsWith(t + ".")) || null;
}

function scrollOffset() {
  const s = $(".search-wrap");
  return (s ? s.offsetHeight : 0) + 12;
}

function flash(el) {
  el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash");
}

function toast(msg) {
  const t = document.createElement("div");
  t.className = "toast"; t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

function renderReader() {
  const { doc } = R;
  const m = doc.meta;
  const last = store.get("lt.read." + R.id, null);
  const partLabel = m.rotPartes || (m.obra ? "Questões" : R.id.startsWith("cicero") ? "Discursos" : "Livros");
  const chapLabel = m.obra === "tomas-suma" ? "Artigos" : "Capítulos";
  main.innerHTML = `
    <div class="reader">
      <div class="rcol">
        <header class="rhead">
          ${m.obra ? `<a class="rback" href="#/obra/${esc(m.obra)}">← ${esc(m.obraTitulo || "Suma Teológica")}</a>` : `<a class="rback" href="#/textos">← Textos</a>`}
          <div class="rmeta"><span lang="la">${esc(m.autorLa)}</span> · ${esc(m.autor)}, <i>${esc(m.titulo)}</i>${m.tratado ? ` · ${esc(m.tratado)}` : ""}${m.edicaoCurta ? ` <span class="rmeta-ed">(${esc(m.edicaoCurta)})</span>` : ""}</div>
          <nav class="rcaps" id="rparts" data-label="${partLabel}" aria-label="${partLabel}">${doc.parts.length > 1
            ? doc.parts.map((p, i) => `<a href="#/t/${R.id}/${esc(p.c)}" data-p="${i}" title="${esc(p.rot)}">${esc(p.chip)}</a>`).join("") : ""}</nav>
          <nav class="rcaps rsub" id="rchaps" data-label="${chapLabel}" aria-label="${chapLabel}"></nav>
          <div class="rtools">
            <form class="rgo" id="rgo"><input id="rgo-in" placeholder="${esc(m.referencia)}: ${esc(m.exemploRef || "")}" aria-label="Ir para a referência (${esc(m.referencia)})" autocomplete="off" spellcheck="false" inputmode="decimal"><button>ir</button></form>
            ${last ? `<a class="rcont" href="#/t/${R.id}/${esc(last)}">continuar em ${esc(last)} →</a>` : ""}
          </div>
        </header>
        <article class="rtext" id="rtext" lang="la"></article>
        <nav class="rpager" id="rpager"></nav>
        <footer class="rsrc">
          <p><b>Texto:</b> ${esc(m.edicao)} Transcrição digital: <a href="${esc(m.fonteTexto.url)}" target="_blank" rel="noopener">${esc(m.fonteTexto.nome)}</a>, ${esc(m.fonteTexto.licenca)}.</p>
          <p><b>Lemas e morfologia:</b> <a href="${esc(m.fonteAnotacao.url)}" target="_blank" rel="noopener">${esc(m.fonteAnotacao.nome)}</a>. ${esc(m.fonteAnotacao.nota)}
            ${doc.estat.sem_analise.toLocaleString("pt-BR")} das ${doc.estat.palavras.toLocaleString("pt-BR")} palavras (sobretudo nomes próprios e numerais) ficaram sem análise e aparecem em cinza.</p>
          <p>${esc(m.notaEdicao)}</p>
        </footer>
      </div>
      <aside class="rpanel" id="rpanel" aria-live="polite" hidden></aside>
    </div>`;
  $("#rtext").addEventListener("click", onWordClick);
  $("#rpanel").addEventListener("click", onPanelClick);
  $("#rgo").addEventListener("submit", ev => {
    ev.preventDefault();
    const v = $("#rgo-in").value.trim();
    if (v) location.hash = `#/t/${R.id}/${encodeURIComponent(v.replace(/\s+/g, ""))}`;
  });
}

function showPart(p) {
  if (p === undefined || p === R.part) return;
  const { doc } = R;
  const part = doc.parts[p];
  closePanel();
  R.part = p;
  let html = "";
  for (let bi = part.b0; bi < part.b1; bi++) {
    const b = doc.blocos[bi];
    if (b.t === "c") {
      html += b.lv === 0 ? `<h2 class="book" data-s="${esc(b.c)}">${esc(b.rot)}</h2>`
        : `<h3 class="cap" data-s="${esc(b.c)}">${esc(b.rot)}</h3>`;
      continue;
    }
    if (b.t === "h") { html += `<h1 class="rtitle">${esc(b.x[0])}</h1>`; continue; }
    let wi = b.w0, inner = "";
    for (const it of b.x) {
      if (typeof it === "string") inner += esc(it);
      else if (Array.isArray(it)) inner += `<span class="w${it[1].length ? "" : " nx"}" data-i="${wi++}">${esc(it[0])}</span>`;
      else if (it.br) inner += "<br>";
      else if (it.lab) inner += `<span class="lab">${esc(it.lab)}</span> `;
      else if (it.s) {
        if (it.k === "ln") inner += `<a class="sec ln${it.d ? "" : " lnm"}" href="#/t/${R.id}/${esc(it.s)}" data-s="${esc(it.s)}" title="${esc(it.s)}">${esc(it.d || "")}</a>`;
        else inner += `<a class="sec" href="#/t/${R.id}/${esc(it.s)}" data-s="${esc(it.s)}" title="${esc(it.s)}">${esc(it.d || it.s)}</a>`;
      }
    }
    html += `<p class="${b.x.some(it => it && it.k === "ln") ? "verse" : ""}">${inner}</p>`;
  }
  $("#rtext").innerHTML = html;
  main.querySelectorAll("#rparts a[data-p]").forEach(a => a.classList.toggle("on", +a.dataset.p === p));
  $("#rchaps").innerHTML = part.chapters.map(c => `<a href="#/t/${R.id}/${esc(c.c)}">${esc(c.chip)}</a>`).join("");
  const prev = doc.parts[p - 1], next = doc.parts[p + 1];
  const sib = R.siblings || {};
  const prevL = prev ? `<a href="#/t/${R.id}/${esc(prev.c)}">← ${esc(prev.rot)}</a>`
    : sib.prev ? `<a href="#/t/${sib.prev.id}">← ${esc(sib.prev.pars)}, ${esc(sib.prev.tratado)}</a>` : "<span></span>";
  const nextL = next ? `<a href="#/t/${R.id}/${esc(next.c)}">${esc(next.rot)} →</a>`
    : sib.next ? `<a href="#/t/${sib.next.id}">${esc(sib.next.pars)}, ${esc(sib.next.tratado)} →</a>` : "<span></span>";
  $("#rpager").innerHTML = doc.parts.length > 1 || sib.prev || sib.next ? prevL + nextL : "";
}

function partOfWord(i) {
  const ps = R.doc.parts;
  for (let p = ps.length - 1; p >= 0; p--) if (i >= ps[p].wStart) return p;
  return 0;
}

function onWordClick(ev) {
  const w = ev.target.closest(".w");
  if (!w) return;
  selectWord(+w.dataset.i);
}

function wordEl(i) { return main.querySelector(`#rtext .w[data-i="${i}"]`); }

function clearMarks() {
  main.querySelectorAll(".w.sel, .w.same").forEach(el => el.classList.remove("sel", "same"));
}

function selectWord(i) {
  if (!R) return;
  const w = R.doc.words[i];
  if (!w) return;
  const p = partOfWord(i);
  if (p !== R.part) showPart(p);
  clearMarks();
  R.sel = i;
  R.full = false;
  const el = wordEl(i);
  if (el) el.classList.add("sel");
  const an = w[1];
  const main0 = an.find(a => R.doc.lemas[a[0]][1]) || an[0];
  R.entry = main0 ? { lem: main0[0] } : null;
  if (main0) markSame(main0[0]);
  renderPanel();
  saveSection(el);
  if (el) keepVisible(el);
}

function keepVisible(el) {
  const r = el.getBoundingClientRect();
  const p = $("#rpanel");
  const top = scrollOffset();
  const sheet = p && getComputedStyle(p).position === "fixed" ? p.getBoundingClientRect().top : innerHeight;
  if (r.bottom > sheet - 16) scrollBy({ top: r.bottom - sheet + Math.min(120, (sheet - top) / 3), behavior: "smooth" });
  else if (r.top < top) scrollBy({ top: r.top - top - 16, behavior: "smooth" });
}

function markSame(li) {
  for (const j of R.doc.byLemma.get(li) || []) if (j !== R.sel) { const e = wordEl(j); if (e) e.classList.add("same"); }
}

function saveSection(el) {
  if (!el) return;
  let s = null;
  for (const m of main.querySelectorAll("#rtext [data-s]")) {
    if (m.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) s = m.dataset.s; else break;
  }
  if (s) store.set("lt.read." + R.id, s);
}

/* ---------- painel ---------- */

function renderPanel() {
  const p = $("#rpanel");
  if (!p) return;
  const w = R.doc.words[R.sel];
  const L = R.doc.lemas, M = R.doc.morfs;
  const an = w[1];
  const occ = li => (R.doc.byLemma.get(li) || []).length;
  const rows = an.map((a, k) => {
    const [li, mi] = a;
    const [lemma, id, escGram, escGl] = L[li];
    const ix = id ? byId.get(id) : undefined;
    const on = R.entry && R.entry.lem === li;
    const readings = (M[mi] || "").split("|").map(morphPT).filter(Boolean);
    const n = occ(li);
    const gram = ix !== undefined ? E[ix][3] : (escGram || "");
    const gl = ix !== undefined ? (ptOf(ix) || E[ix][4]) : (escGl || "");
    return `<div class="an${on ? " on" : ""}">
      <div class="an-top">
        ${ix !== undefined ? `<button class="lem" data-lem="${li}" lang="la">${esc(lemma)}${homNum(ix) ? `<sup>${homNum(ix)}</sup>` : ""}</button>` : `<span class="lem nolem" lang="la">${esc(lemma)}</span>`}
        ${gram ? `<span class="gm" lang="la">${esc(gram)}</span>` : ""}
        ${k === 0 && an.length > 1 ? `<span class="prob" title="Escolhida pela frequência do lema, sem olhar o contexto">mais provável</span>` : ""}
      </div>
      ${readings.length ? `<ul class="morphs">${readings.map(r => `<li>${esc(r)}</li>`).join("")}</ul>` : ""}
      ${gl ? `<div class="angl${ix === undefined || ptOf(ix) ? "" : " en"}">${esc(gl.length > 160 ? gl.slice(0, 157) + "…" : gl)}</div>` : ""}
      ${k === 0 && n > 1 ? `<div class="occ"><button class="btn-link" data-occ="${li}">${n} ocorrências no texto</button></div>` : ""}
      ${ix === undefined && !/^\d+$/.test(lemma) && !readingsRaw(M[mi]).includes("citation") ? `<div class="miss">${escGl ? "Termo escolástico ausente do Lewis &amp; Short; glosa do léxico escolástico deste site (gerada por IA)." : "Lema sem verbete no Lewis &amp; Short."} <a href="https://logeion.uchicago.edu/${encodeURIComponent(lemma)}" target="_blank" rel="noopener">Logeion ↗</a></div>` : ""}
    </div>`;
  }).join("");

  let entryHtmlStr = "";
  const li = R.entry ? R.entry.lem : undefined;
  const id = li !== undefined ? L[li][1] : "";
  const ix = id ? byId.get(id) : undefined;
  if (ix !== undefined) {
    entryHtmlStr = `<div class="rentry">
      <h3 lang="la">${headHtml(ix)} <span class="gm">${esc(E[ix][3])}</span></h3>
      <div lang="pt">${ptBox(ix, true)}</div>
      <div class="rlinks">
        <a href="#/v/${E[ix][0]}">abrir no dicionário →</a>
        <button class="btn-link" data-full>${R.full ? "ocultar" : "ver"} verbete completo (L&amp;S)</button>
        <a href="${gaffiotUrl(ix)}" target="_blank" rel="noopener">Gaffiot ↗</a>
      </div>
      ${R.full ? `<div class="lsdef small" id="rfull" lang="en"><p class="muted">carregando…</p></div>` : ""}
    </div>`;
  } else if (!an.length) {
    entryHtmlStr = `<div class="miss">Sem análise para esta palavra (nome próprio raro, numeral ou forma ausente do Morpheus).
      <a href="#/lat/${encodeURIComponent(w[0])}">procurar “${esc(w[0])}” no dicionário</a></div>`;
  }

  p.innerHTML = `
    <div class="rp-head">
      <span class="rp-form" lang="la">${esc(w[0])}</span>
      <span class="rp-nav">
        <button data-step="-1" title="palavra anterior (←)">‹</button>
        <button data-step="1" title="palavra seguinte (→)">›</button>
        <button data-close title="fechar (Esc)">✕</button>
      </span>
    </div>
    ${rows ? `<div class="ans">${rows}</div>` : ""}
    ${entryHtmlStr}
    <div class="rp-note">Análise automática${R.doc.meta.obra ? " (Morpheus, com regras próprias para o latim escolástico)" : " do Morpheus"}, palavra por palavra, sem desambiguação pelo contexto.
      Traduções em português geradas por IA: confira no verbete.</div>`;
  p.hidden = false;
  p.scrollTop = 0;
  document.body.classList.add("panel-open");
  if (R.full && ix !== undefined) {
    entryHtml(ix).then(h => { const b = $("#rfull"); if (b) b.innerHTML = h; })
      .catch(() => { const b = $("#rfull"); if (b) b.innerHTML = `<p class="muted">Não foi possível carregar o verbete.</p>`; });
  }
}

function closePanel() {
  const p = $("#rpanel");
  if (p) p.hidden = true;
  document.body.classList.remove("panel-open");
  clearMarks();
  if (R) R.sel = -1;
}

function onPanelClick(ev) {
  const btn = ev.target.closest("button");
  if (!btn) return;
  if (btn.dataset.close !== undefined) { closePanel(); return; }
  if (btn.dataset.step) { step(+btn.dataset.step); return; }
  if (btn.dataset.full !== undefined) { R.full = !R.full; const y = $("#rpanel").scrollTop; renderPanel(); $("#rpanel").scrollTop = y; return; }
  if (btn.dataset.lem) {
    const li = +btn.dataset.lem;
    R.entry = { lem: li };
    R.full = false;
    clearMarks();
    const el = wordEl(R.sel); if (el) el.classList.add("sel");
    markSame(li);
    renderPanel();
    return;
  }
  if (btn.dataset.occ) { nextOccurrence(+btn.dataset.occ); return; }
}

function step(d) {
  if (!R || R.sel < 0) return;
  const j = R.sel + d;
  if (j >= 0 && j < R.doc.words.length) selectWord(j);
}

function nextOccurrence(li) {
  const list = R.doc.byLemma.get(li) || [];
  if (!list.length) return;
  const next = list.find(j => j > R.sel) ?? list[0];
  selectWord(next);
}

document.addEventListener("keydown", ev => {
  if (!document.body.classList.contains("reading") || !R) return;
  if (ev.target.closest && ev.target.closest("input, textarea")) return;
  if (ev.key === "Escape") closePanel();
  else if (ev.key === "ArrowRight" && R.sel >= 0) { ev.preventDefault(); step(1); }
  else if (ev.key === "ArrowLeft" && R.sel >= 0) { ev.preventDefault(); step(-1); }
});

function leaveReader() {
  document.body.classList.remove("reading", "panel-open");
}
