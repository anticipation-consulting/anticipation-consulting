/* ============================================================
   Anticipation Consulting — shared site behavior
   - mobile nav
   - palette persistence + vanilla Tweaks panel (host protocol)
   - interactive site-wide network background (#net-bg)
   - static node-link motif inside dark .ink-section bands
   - scroll reveal
   ============================================================ */
(function () {
  "use strict";

  /* ---------- palette ---------- */
  var PALETTES = [
    { id: "signal", name: "Signal", sub: "Charcoal \u00b7 blue",  sw: ["#1a1d22", "#f6f7f9", "#2f6fe0"] },
    { id: "ink",    name: "Ink",    sub: "Navy \u00b7 copper",    sw: ["#1c2333", "#fbfaf7", "#a8693f"] },
    { id: "field",  name: "Field",  sub: "Forest \u00b7 ochre",   sw: ["#23382e", "#f4f1e9", "#b58a3e"] }
  ];
  var DEFAULT_PAL = "signal";
  var LS_PAL = "ac_palette";
  var LS_MOTIF = "ac_motif";

  function getPalette() {
    try { return localStorage.getItem(LS_PAL) || DEFAULT_PAL; } catch (e) { return DEFAULT_PAL; }
  }
  function setPalette(id) {
    document.documentElement.setAttribute("data-palette", id);
    try { localStorage.setItem(LS_PAL, id); } catch (e) {}
    refreshColors();
    drawAllMotifs();
    syncTweaksUI();
  }
  function motifOn() {
    try { return localStorage.getItem(LS_MOTIF) !== "off"; } catch (e) { return true; }
  }
  function setMotif(on) {
    try { localStorage.setItem(LS_MOTIF, on ? "on" : "off"); } catch (e) {}
    document.querySelectorAll(".hero-motif").forEach(function (c) { c.style.display = on ? "" : "none"; });
    if (bgCanvas) {
      bgCanvas.style.display = on ? "" : "none";
      if (on) startBg(); else stopBg();
    }
    drawAllMotifs();
    syncTweaksUI();
  }

  document.documentElement.setAttribute("data-palette", getPalette());
  var REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- color helpers ---------- */
  var _resolveEl, _lineRGB = "30,34,42", _nodeRGB = "30,34,42", _accentRGB = "47,111,224";
  // logo triad (blue / copper / green) — fixed, palette-independent
  var LOGO_TRI = ["47,111,224", "181,120,63", "47,125,84"];
  function triPath(ctx, x, y, r, flip) {
    var k = flip ? -1 : 1;
    ctx.beginPath();
    ctx.moveTo(x, y - r * k);
    ctx.lineTo(x - r * 0.866, y + r * 0.5 * k);
    ctx.lineTo(x + r * 0.866, y + r * 0.5 * k);
    ctx.closePath();
  }
  function rgbOf(color) {
    if (!_resolveEl) { _resolveEl = document.createElement("span"); _resolveEl.style.cssText = "position:absolute;display:none"; document.body.appendChild(_resolveEl); }
    _resolveEl.style.color = color;
    var m = getComputedStyle(_resolveEl).color.match(/\d+(\.\d+)?/g);
    return m ? (m[0] + "," + m[1] + "," + m[2]) : "30,34,42";
  }
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function refreshColors() {
    _lineRGB = rgbOf(cssVar("--motif") || "#1a1d22");
    _nodeRGB = _lineRGB;
    _accentRGB = rgbOf(cssVar("--accent") || "#2f6fe0");
  }

  /* ---------- mobile nav ---------- */
  function initNav() {
    var burger = document.querySelector(".hamburger");
    var links = document.querySelector(".nav-links");
    if (!burger || !links) return;
    burger.addEventListener("click", function () { links.classList.toggle("open"); });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); });
    });
  }

  /* ============================================================
     INTERACTIVE NETWORK BACKGROUND (#net-bg, fixed, full-viewport)
     ============================================================ */
  var bgCanvas, bgCtx, bgNodes = [], bgW = 0, bgH = 0, bgRAF = 0, bgDpr = 1;
  var mouse = { x: -9999, y: -9999, on: false };

  function buildBg() {
    bgCanvas = document.createElement("canvas");
    bgCanvas.id = "net-bg";
    bgCanvas.setAttribute("aria-hidden", "true");
    document.body.insertBefore(bgCanvas, document.body.firstChild);
    bgCtx = bgCanvas.getContext("2d");
    sizeBg();
    seedNodes();
    window.addEventListener("pointermove", function (e) {
      mouse.x = e.clientX; mouse.y = e.clientY; mouse.on = true;
    }, { passive: true });
    window.addEventListener("pointerleave", function () { mouse.on = false; });
    window.addEventListener("blur", function () { mouse.on = false; });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) stopBg(); else if (motifOn()) startBg();
    });
    if (!motifOn()) { bgCanvas.style.display = "none"; return; }
    if (REDUCED) { renderBg(); } else { startBg(); }
  }
  function sizeBg() {
    bgDpr = Math.min(window.devicePixelRatio || 1, 2);
    bgW = window.innerWidth; bgH = window.innerHeight;
    bgCanvas.width = bgW * bgDpr; bgCanvas.height = bgH * bgDpr;
    bgCanvas.style.width = bgW + "px"; bgCanvas.style.height = bgH + "px";
    bgCtx.setTransform(bgDpr, 0, 0, bgDpr, 0, 0);
  }
  function seedNodes() {
    var n = Math.round((bgW * bgH) / 12500);
    n = Math.max(44, Math.min(n, 170));
    bgNodes = [];
    for (var i = 0; i < n; i++) {
      bgNodes.push({
        x: Math.random() * bgW,
        y: Math.random() * bgH,
        vx: (Math.random() - 0.5) * 0.22,
        vy: (Math.random() - 0.5) * 0.22,
        r: 1.1 + Math.random() * 1.9,
        big: Math.random() > 0.9,
        col: LOGO_TRI[(Math.random() * 3) | 0],
        flip: Math.random() > 0.5
      });
    }
  }
  var LINK = 124, CURSOR_R = 196;
  function renderBg() {
    if (!bgCtx) return;
    bgCtx.clearRect(0, 0, bgW, bgH);
    var i, j, a, b, dx, dy, d;
    // update positions
    for (i = 0; i < bgNodes.length; i++) {
      a = bgNodes[i];
      if (!REDUCED) {
        if (mouse.on) {
          dx = mouse.x - a.x; dy = mouse.y - a.y; d = Math.sqrt(dx * dx + dy * dy);
          if (d < CURSOR_R && d > 0.1) {
            var f = (1 - d / CURSOR_R) * 0.012;
            a.vx += (dx / d) * f; a.vy += (dy / d) * f;
          }
        }
        a.x += a.vx; a.y += a.vy;
        a.vx *= 0.992; a.vy *= 0.992;
        // gentle minimum drift
        if (Math.abs(a.vx) < 0.04) a.vx += (Math.random() - 0.5) * 0.03;
        if (Math.abs(a.vy) < 0.04) a.vy += (Math.random() - 0.5) * 0.03;
        // clamp speed
        var sp = Math.hypot(a.vx, a.vy); if (sp > 0.55) { a.vx *= 0.55 / sp; a.vy *= 0.55 / sp; }
        if (a.x < -20) a.x = bgW + 20; else if (a.x > bgW + 20) a.x = -20;
        if (a.y < -20) a.y = bgH + 20; else if (a.y > bgH + 20) a.y = -20;
      }
    }
    // links between nodes
    bgCtx.lineWidth = 1;
    for (i = 0; i < bgNodes.length; i++) {
      a = bgNodes[i];
      for (j = i + 1; j < bgNodes.length; j++) {
        b = bgNodes[j];
        dx = a.x - b.x; dy = a.y - b.y; d = Math.sqrt(dx * dx + dy * dy);
        if (d < LINK) {
          var op = (1 - d / LINK) * 0.42;
          var grd = bgCtx.createLinearGradient(a.x, a.y, b.x, b.y);
          grd.addColorStop(0, "rgba(" + a.col + "," + op.toFixed(3) + ")");
          grd.addColorStop(1, "rgba(" + b.col + "," + op.toFixed(3) + ")");
          bgCtx.strokeStyle = grd;
          bgCtx.beginPath(); bgCtx.moveTo(a.x, a.y); bgCtx.lineTo(b.x, b.y); bgCtx.stroke();
        }
      }
    }
    // links to cursor
    if (mouse.on) {
      for (i = 0; i < bgNodes.length; i++) {
        a = bgNodes[i];
        dx = mouse.x - a.x; dy = mouse.y - a.y; d = Math.sqrt(dx * dx + dy * dy);
        if (d < CURSOR_R) {
          var cop = (1 - d / CURSOR_R) * 0.42;
          var cg = bgCtx.createLinearGradient(a.x, a.y, mouse.x, mouse.y);
          cg.addColorStop(0, "rgba(" + a.col + "," + cop.toFixed(3) + ")");
          cg.addColorStop(1, "rgba(" + a.col + ",0)");
          bgCtx.strokeStyle = cg;
          bgCtx.lineWidth = 1;
          bgCtx.beginPath(); bgCtx.moveTo(a.x, a.y); bgCtx.lineTo(mouse.x, mouse.y); bgCtx.stroke();
        }
      }
      bgCtx.beginPath();
      bgCtx.fillStyle = "rgba(" + _accentRGB + ",0.5)";
      bgCtx.arc(mouse.x, mouse.y, 2.6, 0, 6.2832); bgCtx.fill();
    }
    // nodes — small triangles in the logo triad
    for (i = 0; i < bgNodes.length; i++) {
      a = bgNodes[i];
      var rr = (a.big ? a.r + 1.5 : a.r) * 1.75;
      triPath(bgCtx, a.x, a.y, rr, a.flip);
      bgCtx.fillStyle = "rgba(" + a.col + "," + (a.big ? 0.72 : 0.5) + ")";
      bgCtx.fill();
    }
  }
  function loop() { renderBg(); bgRAF = requestAnimationFrame(loop); }
  function startBg() { if (REDUCED) { renderBg(); return; } if (bgRAF) return; bgRAF = requestAnimationFrame(loop); }
  function stopBg() { if (bgRAF) { cancelAnimationFrame(bgRAF); bgRAF = 0; } }

  /* ---------- static motif inside dark ink sections ---------- */
  function drawMotif(canvas) {
    if (canvas.style.display === "none") return;
    var rect = canvas.getBoundingClientRect();
    var w = rect.width, h = rect.height;
    if (w < 4 || h < 4) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = w * dpr; canvas.height = h * dpr;
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    var seed = (canvas.dataset.seed ? parseInt(canvas.dataset.seed, 10) : 7) || 7;
    function rnd() { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; }
    var density = parseFloat(canvas.dataset.density || "1");
    var n = Math.min(Math.max(14, Math.round((w * h) / 26000 * density)), 60);
    var nodes = [];
    for (var i = 0; i < n; i++) nodes.push({ x: rnd() * w, y: rnd() * h, r: 1.3 + rnd() * 2.6, big: rnd() > 0.85, col: LOGO_TRI[(rnd() * 3) | 0], flip: rnd() > 0.5 });
    var maxD = Math.min(w, h) * 0.32 + 90;
    ctx.lineWidth = 1;
    for (var a = 0; a < nodes.length; a++) for (var b = a + 1; b < nodes.length; b++) {
      var dx = nodes[a].x - nodes[b].x, dy = nodes[a].y - nodes[b].y, d = Math.sqrt(dx * dx + dy * dy);
      if (d < maxD) {
        var lop = (1 - d / maxD) * 0.5;
        var mg = ctx.createLinearGradient(nodes[a].x, nodes[a].y, nodes[b].x, nodes[b].y);
        mg.addColorStop(0, "rgba(" + nodes[a].col + "," + lop.toFixed(3) + ")");
        mg.addColorStop(1, "rgba(" + nodes[b].col + "," + lop.toFixed(3) + ")");
        ctx.strokeStyle = mg;
        ctx.beginPath(); ctx.moveTo(nodes[a].x, nodes[a].y); ctx.lineTo(nodes[b].x, nodes[b].y); ctx.stroke();
      }
    }
    for (var k = 0; k < nodes.length; k++) {
      var nd = nodes[k];
      var rr = (nd.big ? nd.r + 1.4 : nd.r) * 1.75;
      triPath(ctx, nd.x, nd.y, rr, nd.flip);
      ctx.fillStyle = "rgba(" + nd.col + "," + (nd.big ? 0.85 : 0.55) + ")";
      ctx.fill();
    }
  }
  var _onInkRGB = "230,235,242";
  function drawAllMotifs() {
    _onInkRGB = rgbOf(cssVar("--on-ink") || "#e6ebf2");
    document.querySelectorAll(".ink-section .hero-motif").forEach(drawMotif);
  }

  /* ---------- scroll reveal ---------- */
  function initReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!els.length || !("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ---------- tweaks panel ---------- */
  var panelEl;
  function buildTweaks() {
    panelEl = document.createElement("div");
    panelEl.id = "tweaks";
    var opts = PALETTES.map(function (p) {
      var sw = p.sw.map(function (c) { return '<i style="background:' + c + '"></i>'; }).join("");
      return '<button class="pal-opt" data-pal="' + p.id + '">' +
        '<span class="pal-sw">' + sw + '</span>' +
        '<span><span class="pal-name">' + p.name + '</span><br><span class="pal-sub">' + p.sub + '</span></span>' +
        '</button>';
    }).join("");
    panelEl.innerHTML =
      '<div class="tweaks-head"><h4>Tweaks</h4><button id="tw-close" aria-label="Close">&times;</button></div>' +
      '<div class="tweaks-body">' +
        '<div class="tw-label">Palette direction</div>' +
        '<div class="pal-opts">' + opts + '</div>' +
        '<div class="tw-toggle"><span>Network background</span><button class="tw-switch" id="tw-motif" aria-label="Toggle network background"></button></div>' +
      '</div>';
    document.body.appendChild(panelEl);
    panelEl.querySelectorAll(".pal-opt").forEach(function (btn) {
      btn.addEventListener("click", function () { setPalette(btn.dataset.pal); });
    });
    panelEl.querySelector("#tw-close").addEventListener("click", function () {
      panelEl.classList.remove("open");
      try { window.parent.postMessage({ type: "__edit_mode_dismissed" }, "*"); } catch (e) {}
    });
    panelEl.querySelector("#tw-motif").addEventListener("click", function () { setMotif(!motifOn()); });
    syncTweaksUI();
  }
  function syncTweaksUI() {
    if (!panelEl) return;
    var cur = getPalette();
    panelEl.querySelectorAll(".pal-opt").forEach(function (b) { b.classList.toggle("sel", b.dataset.pal === cur); });
    var sw = panelEl.querySelector("#tw-motif"); if (sw) sw.classList.toggle("on", motifOn());
  }
  function initTweaksHost() {
    buildTweaks();
    window.addEventListener("message", function (e) {
      var t = e && e.data && e.data.type;
      if (t === "__activate_edit_mode") panelEl.classList.add("open");
      else if (t === "__deactivate_edit_mode") panelEl.classList.remove("open");
    });
    try { window.parent.postMessage({ type: "__edit_mode_available" }, "*"); } catch (e) {}
  }

  /* ---------- header shadow ---------- */
  function initHeader() {
    var h = document.querySelector(".site-header"); if (!h) return;
    var onScroll = function () { h.classList.toggle("scrolled", window.scrollY > 8); };
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- init ---------- */
  function init() {
    refreshColors();
    initNav();
    initHeader();
    buildBg();
    if (!motifOn()) document.querySelectorAll(".hero-motif").forEach(function (c) { c.style.display = "none"; });
    drawAllMotifs();
    initReveal();
    initTweaksHost();
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        if (bgCanvas) { sizeBg(); seedNodes(); if (REDUCED) renderBg(); }
        drawAllMotifs();
      }, 160);
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawAllMotifs);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
