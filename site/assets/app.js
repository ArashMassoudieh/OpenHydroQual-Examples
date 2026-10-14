(() => {
  "use strict";

  // Line icons (24x24) per track.
  const ICONS = {
    start: '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
    wq: '<path d="M9 3h6"/><path d="M10 3v6L5 19a1.5 1.5 0 0 0 1.3 2h11.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/><path d="M7.5 15h9"/>',
    storm: '<path d="M7 15a4 4 0 1 1 .9-7.9A5 5 0 0 1 17.6 8 3.5 3.5 0 1 1 17 15H7Z"/><path d="M8 18l-1 3M12 18l-1 3M16 18l-1 3"/>',
    hydro: '<path d="m2 20 7-11 4 6 3-4 6 9Z"/><path d="M2 20c3-1.5 5 1.5 8 0s5 1.5 8 0 3 0 4 0"/>',
    soil: '<path d="M12 21v-8"/><path d="M12 13c0-4 3-6 7-6 0 4-3 6-7 6Z"/><path d="M12 15c0-3-2-5-6-5 0 3 2 5 6 5Z"/><path d="M3 21h18"/>',
    hyd: '<path d="M2 18h20"/><path d="M4 18v-5a8 8 0 0 1 16 0v5"/><path d="M8 18v-4a4 4 0 0 1 8 0v4"/>',
    mgmt: '<path d="M3 21V10l5-3v14"/><path d="M8 21V4l7 3v14"/><path d="M15 21v-9l6 2v7"/><path d="M2 21h20"/>',
    calib: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r=".8"/>',
    auto: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3M12 15h5"/>'
  };
  const LEVELS = ["", "Beginner", "Intermediate", "Advanced"];
  const SUGGESTIONS = ["bioretention", "Monod", "MCMC", "culvert", "snowmelt", "Richards equation", "sorption", "dissolved oxygen", "curve number", "real-time control", "python"];
  const DOCS = {
    "culvert_model.pdf": "Culvert Hydraulics",
    "curve_number_method.pdf": "SCS Curve Number Method",
    "hydrologic_response_units.pdf": "Hydrologic Response Units",
    "lm_calibration.pdf": "Levenberg-Marquardt Calibration",
    "plant_water_uptake.pdf": "Plant Water Uptake",
    "sedimentation_basin_tutorial.pdf": "Sedimentation Basin Tutorial",
    "composite_blocks.pdf": "Composite Blocks",
    "emc_calibration.pdf": "EMC Calibration",
    "ohq_settings_manual.pdf": "Solver & Settings Manual"
  };
  // Field weights for ranking.
  const W = { title: 10, keywords: 6, plugins: 5, features: 4, track: 3, summary: 2 };

  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = (s) => String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[_\-/(),.:+]/g, " ");

  let DATA, trackById = {};
  const state = { q: "", tracks: new Set(), level: 0, plugin: "", readyOnly: false };

  function index(ex) {
    const t = trackById[ex.track];
    ex._f = {
      title: norm(ex.title),
      keywords: norm(ex.keywords.join(" | ")),
      plugins: norm(ex.plugins.join(" | ")),
      features: norm(ex.features.join(" | ")),
      track: norm(t.name),
      summary: norm(ex.summary)
    };
  }

  // Every query term must hit at least one field, by word prefix (or substring for 4+ chars).
  function score(ex, terms) {
    let total = 0;
    const hits = new Set();
    for (const term of terms) {
      let best = 0;
      const re = new RegExp("(^|\\s)" + term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
      for (const k in W) {
        const f = ex._f[k];
        if (re.test(f)) { best = Math.max(best, W[k] * 2); if (k === "keywords") hits.add(term); }
        else if (term.length >= 4 && f.includes(term)) best = Math.max(best, W[k]);
      }
      if (!best) return 0;
      total += best;
    }
    const phrase = terms.join(" ");
    if (terms.length > 1 && (ex._f.title.includes(phrase) || ex._f.keywords.includes(phrase))) total += 15;
    ex._hits = hits;
    return total;
  }

  function highlight(text, terms) {
    let out = esc(text);
    if (!terms.length) return out;
    const pat = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
    return out.replace(new RegExp("(^|[^\\w&])(" + pat + ")", "gi"), "$1<mark>$2</mark>");
  }

  function matchedKeywords(ex, terms) {
    if (!terms.length) return "";
    const kws = ex.keywords.filter((k) => terms.some((t) => new RegExp("(^|\\s)" + t).test(norm(k))));
    if (!kws.length) return "";
    return '<div class="matched">Matches: ' + kws.slice(0, 4).map((k) => highlight(k, terms)).join(", ") + "</div>";
  }

  function card(ex, terms) {
    const t = trackById[ex.track];
    const planned = ex.status !== "ready";
    const dots = [1, 2, 3].map((i) => `<b class="${i <= ex.level ? "f" : ""}"></b>`).join("");
    const doc = ex.doc ? `<a class="btn ghost" href="docs/${esc(ex.doc)}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6"/></svg>Guide</a>` : "";
    const main = planned
      ? `<span class="btn disabled">Coming soon</span>`
      : `<a class="btn primary" href="downloads/${ex.id}.zip" download><svg viewBox="0 0 24 24"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>Download</a>
         <a class="btn ghost" href="examples/${ex.id}/">Details</a>`;
    return `<article class="card" style="--c:${t.color}">
      ${ex.thumb ? `<a class="thumb diagram-thumb" href="examples/${ex.id}/" aria-label="${esc(ex.title)} details">
        <img src="${esc(ex.thumb)}" alt="" loading="lazy">
        <span class="track">${esc(t.name)}</span>
      </a>` : `<div class="thumb">
        <svg class="waves" viewBox="0 0 300 104" preserveAspectRatio="none"><path d="M0 70 Q40 50 80 70 T160 70 T240 70 T320 70 V104 H0Z" fill="#fff"/><path d="M0 84 Q40 66 80 84 T160 84 T240 84 T320 84 V104 H0Z" fill="#fff"/></svg>
        ${planned ? '<span class="badge">Planned</span>' : ""}
        <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${ICONS[ex.track]}</svg>
        <span class="track">${esc(t.name)}</span>
      </div>`}
      <div class="body">
        <h3>${planned ? highlight(ex.title, terms) : `<a href="examples/${ex.id}/">${highlight(ex.title, terms)}</a>`}</h3>
        <div class="level" title="${LEVELS[ex.level]}">${dots}<span>${LEVELS[ex.level]}</span></div>
        <p>${highlight(ex.summary, terms)}</p>
        ${matchedKeywords(ex, terms)}
        <div class="tags">${ex.features.map((f) => `<span class="tag">${highlight(f, terms)}</span>`).join("")}</div>
        <div class="tags">${ex.plugins.map((p) => `<button class="plug" data-plugin="${esc(p)}" title="Filter by this plugin">${highlight(p, terms)}</button>`).join("")}</div>
      </div>
      <div class="actions">${main}${doc}</div>
    </article>`;
  }

  function render() {
    const terms = norm(state.q).split(/\s+/).filter(Boolean);
    let list = DATA.examples.filter((ex) =>
      (!state.tracks.size || state.tracks.has(ex.track)) &&
      (!state.level || ex.level === state.level) &&
      (!state.plugin || ex.plugins.includes(state.plugin)) &&
      (!state.readyOnly || ex.status === "ready"));
    if (terms.length) {
      list = list.map((ex) => [ex, score(ex, terms)]).filter((p) => p[1] > 0).sort((a, b) => b[1] - a[1]).map((p) => p[0]);
    }
    $("#grid").innerHTML = list.map((ex) => card(ex, terms)).join("");
    $("#empty").hidden = list.length > 0;
    const n = DATA.examples.length;
    $("#count").textContent = list.length === n ? `${n} examples` : `${list.length} of ${n} examples`;
    $("#reset").hidden = !(state.q || state.tracks.size || state.level || state.plugin || state.readyOnly);
    document.querySelectorAll(".chip").forEach((c) => c.classList.toggle("on", state.tracks.has(c.dataset.track)));
    document.querySelectorAll("#levels button").forEach((b) => b.classList.toggle("on", +b.dataset.level === state.level));
    $("#plugin").value = state.plugin;
    $("#readyOnly").checked = state.readyOnly;
    syncURL();
  }

  function syncURL() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.tracks.size) p.set("track", [...state.tracks].join(","));
    if (state.level) p.set("level", state.level);
    if (state.plugin) p.set("plugin", state.plugin);
    if (state.readyOnly) p.set("ready", "1");
    const s = p.toString();
    history.replaceState(null, "", s ? "?" + s : location.pathname);
  }

  function readURL() {
    const p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    state.tracks = new Set((p.get("track") || "").split(",").filter((t) => trackById[t]));
    state.level = +p.get("level") || 0;
    state.plugin = p.get("plugin") || "";
    state.readyOnly = p.get("ready") === "1";
    $("#q").value = state.q;
  }

  function suggestButtons(el) {
    el.innerHTML = SUGGESTIONS.map((s) => `<button data-q="${esc(s)}">${esc(s)}</button>`).join("");
  }

  function setup(data) {
    DATA = data;
    data.tracks.forEach((t) => (trackById[t.id] = t));
    data.examples.forEach(index);

    $("#tracks").innerHTML = data.tracks.map((t) => {
      const n = data.examples.filter((e) => e.track === t.id).length;
      return `<button class="chip" data-track="${t.id}" style="--c:${t.color}"><i></i>${esc(t.name)} <small>${n}</small></button>`;
    }).join("");

    const plugins = [...new Set(data.examples.flatMap((e) => e.plugins))].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));
    $("#plugin").insertAdjacentHTML("beforeend", plugins.map((p) => `<option value="${esc(p)}">${esc(p)}</option>`).join(""));

    suggestButtons($("#suggest"));
    suggestButtons($("#emptySuggest"));
    $("#doclist").innerHTML = Object.entries(DOCS).map(([f, name]) =>
      `<a class="doc" href="docs/${f}" target="_blank" rel="noopener"><span class="pdf">PDF</span><span>${esc(name)}<small>${f}</small></span></a>`).join("");

    let timer;
    $("#q").addEventListener("input", (e) => { clearTimeout(timer); timer = setTimeout(() => { state.q = e.target.value.trim(); render(); }, 80); });
    $("#q").addEventListener("keydown", (e) => { if (e.key === "Escape") { e.target.value = ""; state.q = ""; render(); } });
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && document.activeElement !== $("#q") && !/input|select|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); $("#q").focus(); }
    });
    document.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (chip) { const t = chip.dataset.track; state.tracks.has(t) ? state.tracks.delete(t) : state.tracks.add(t); render(); return; }
      const lvl = e.target.closest("#levels button");
      if (lvl) { state.level = +lvl.dataset.level; render(); return; }
      const plug = e.target.closest(".plug");
      if (plug) { state.plugin = plug.dataset.plugin; render(); window.scrollTo({ top: $(".filters").offsetTop, behavior: "smooth" }); return; }
      const sug = e.target.closest("[data-q]");
      if (sug) { state.q = sug.dataset.q; $("#q").value = state.q; render(); return; }
    });
    $("#plugin").addEventListener("change", (e) => { state.plugin = e.target.value; render(); });
    $("#readyOnly").addEventListener("change", (e) => { state.readyOnly = e.target.checked; render(); });
    $("#reset").addEventListener("click", () => {
      Object.assign(state, { q: "", tracks: new Set(), level: 0, plugin: "", readyOnly: false });
      $("#q").value = ""; render();
    });

    readURL();
    render();
  }

  fetch("data/catalog.json")
    .then((r) => r.json())
    .then(setup)
    .catch((err) => { $("#grid").innerHTML = `<p>Could not load the catalog (${esc(err.message)}).</p>`; });
})();
