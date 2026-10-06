/* Redshift-Dependent Expansion — public illustrative simulation.
 *
 * What this page shows: one set of synthetic galaxy tracers, each projected
 * through two fitted expansion histories (distance-sector endpoint R in blue,
 * Planck-compatible reference C1 in red, optional sensitivity reference C2
 * as an amber halo). The spoke between each pair exaggerates the inferred
 * radial difference for visibility; graph data are never exaggerated.
 *
 * Rendering follows a p5.js 2-D canvas approach: tracer directions live in
 * 3-D, are rotated with yaw/pitch matrices, perspective-projected, and
 * depth-sorted before drawing. No observed galaxies are plotted anywhere.
 */
'use strict';

(function () {
  var GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
  var PERSP = 3.0;
  var C_LIGHT = 299792.458;

  var state = {
    data: null,
    loadError: null,
    tracers: [],
    stars: [],
    proj: [], // projected screen positions for hover inspection
    animationProgress: 0.55,
    playing: true,
    yaw: 0.7,
    pitch: 0.42,
    zoom: 1.0,
    exaggerationFactor: 8,
    exaggerationOptions: [1, 4, 8, 12],
    showC2: false,
    showPairLines: true,
    showGraphs: true,
    mouseDown: false,
    lastPX: 0,
    lastPY: 0,
    hoverIndex: -1,
    sphereSketch: null,
    zScan: 1.0,
    aVisual: 1.0,
    peakBoost: 1.0,
    graphCtx: {}
  };

  /* ---------------- deterministic utilities ---------------- */

  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function clamp(v, lo, hi) {
    return v < lo ? lo : v > hi ? hi : v;
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function linInterp(xp, fp, x) {
    if (x <= xp[0]) return fp[0];
    if (x >= xp[xp.length - 1]) return fp[xp.length - 1];
    var lo = 0;
    var hi = xp.length - 1;
    while (hi - lo > 1) {
      var mid = (lo + hi) >> 1;
      if (xp[mid] <= x) lo = mid;
      else hi = mid;
    }
    var t = (x - xp[lo]) / (xp[hi] - xp[lo]);
    return fp[lo] + t * (fp[hi] - fp[lo]);
  }

  // Invert a monotone increasing table yp(xp) at value y.
  function invertMonotone(xp, yp, y) {
    if (y <= yp[0]) return xp[0];
    if (y >= yp[yp.length - 1]) return xp[xp.length - 1];
    var lo = 0;
    var hi = yp.length - 1;
    while (hi - lo > 1) {
      var mid = (lo + hi) >> 1;
      if (yp[mid] <= y) lo = mid;
      else hi = mid;
    }
    var t = (y - yp[lo]) / (yp[hi] - yp[lo]);
    return xp[lo] + t * (xp[hi] - xp[lo]);
  }

  /* ---------------- animation kinematics ---------------- */

  // Redshift scan: decreases from an early illustrative state toward 0.
  // Scientific overlays become active at z = 2.33 (Ly-alpha anchor) and the
  // validated domain covers z <= 1.8.
  function zScanOf(p) {
    if (p < 0.22) {
      var t = p / 0.22;
      t = t * t * (3 - 2 * t);
      return lerp(3.4, 2.33, t);
    }
    if (p < 0.38) return lerp(2.33, 1.8, (p - 0.22) / 0.16);
    return 1.8 * (1 - (p - 0.38) / 0.62);
  }

  // Presentation-only growth factor for the sphere visual. Named aVisual
  // (not scale factor): it is a cinematic device, not a cosmological a(t).
  function aVisualOf(p) {
    return 0.06 + 0.94 * easeOutCubic(clamp(p, 0, 1));
  }

  function regimeOf(z) {
    if (z > 2.33) return 'early';
    if (z > 1.8) return 'continuation';
    return 'constrained';
  }

  /* ---------------- tracer construction ---------------- */

  function buildTracers(data) {
    var n = data.tracers.count;
    var seed = data.tracers.seed;
    var rng = mulberry32(seed);
    var z = data.curves.z;
    var dmC1 = data.curves.DM_C1;
    var dmR = data.curves.DM_R;
    var dmC2 = data.curves.DM_C2;
    var dmMax = dmC1[dmC1.length - 1];
    var out = [];
    for (var i = 0; i < n; i++) {
      // Quasi-uniform direction on the sphere (Fibonacci lattice).
      var y = 1 - (2 * (i + 0.5)) / n;
      var rr = Math.sqrt(Math.max(0, 1 - y * y));
      var phi = i * GOLDEN_ANGLE;
      var dir = { x: rr * Math.cos(phi), y: y, z: rr * Math.sin(phi) };
      // Radial location uniform in comoving volume, then mapped to a
      // nominal redshift through the C1 distance table.
      var u = rng();
      var dmTarget = Math.cbrt(u) * dmMax;
      var zi = invertMonotone(z, dmC1, dmTarget);
      var trueRadiusR = linInterp(z, dmR, zi) / dmMax;
      var trueRadiusC1 = linInterp(z, dmC1, zi) / dmMax;
      var trueRadiusC2 = linInterp(z, dmC2, zi) / dmMax;
      out.push({
        id: i,
        dir: dir,
        z: zi,
        trueRadiusR: trueRadiusR,
        trueRadiusC1: trueRadiusC1,
        trueRadiusC2: trueRadiusC2
      });
    }
    return out;
  }

  function buildStars(seed) {
    var rng = mulberry32(seed ^ 0x51ab);
    var stars = [];
    for (var i = 0; i < 240; i++) {
      stars.push({
        x: rng(),
        y: rng(),
        r: 0.4 + rng() * 0.9,
        a: 16 + rng() * 44
      });
    }
    return stars;
  }

  // Midpoint-preserving display exaggeration. E = 1 reproduces the true
  // normalized radii exactly; larger E widens only the displayed gap.
  function displayRadii(tr, exaggerationFactor) {
    var mid = (tr.trueRadiusR + tr.trueRadiusC1) / 2;
    var gap = tr.trueRadiusR - tr.trueRadiusC1;
    return {
      displayRadiusR: mid + (exaggerationFactor / 2) * gap,
      displayRadiusC1: mid - (exaggerationFactor / 2) * gap
    };
  }

  /* ---------------- data loading ---------------- */

  function loadData() {
    // Standalone single-file builds embed the JSON payload directly.
    if (window.__RDE_DATA) {
      initFromData(window.__RDE_DATA);
      return;
    }
    fetch('data/publication_simulation_data.json')
      .then(function (resp) {
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        return resp.json();
      })
      .then(function (data) {
        initFromData(data);
      })
      .catch(function (err) {
        state.loadError = String(err);
      });
  }

  function initFromData(data) {
    state.data = data;
    state.exaggerationFactor = data.display_defaults.exaggeration;
    state.exaggerationOptions = data.display_defaults.exaggeration_options;
    state.tracers = buildTracers(data);
    state.stars = buildStars(data.tracers.seed);
    updateBadge();
  }

  /* ---------------- HUD ---------------- */

  function $(id) {
    return document.getElementById(id);
  }

  function updateBadge() {
    $('badge-exaggeration').textContent =
      'difference display ×' + state.exaggerationFactor;
  }

  function fmt(n, digits) {
    return Number(n).toFixed(digits);
  }

  function updateHud() {
    var z = state.zScan;
    var regime = regimeOf(z);
    var scanEl = $('scan-readout');
    var regEl = $('regime-readout');
    var badge = $('badge-domain');
    var interp = $('interp-line');
    if (regime === 'early') {
      scanEl.textContent = 'z = ' + fmt(z, 2) + ' · illustrative early era';
      regEl.textContent = 'no paper inference';
      regEl.style.color = '#93a5c4';
      badge.textContent = 'z > 2.33 · illustration only';
      interp.textContent =
        'Illustrative early era: the sphere is still growing and no paper ' +
        'inference is shown here. Scientific overlays activate at z = 2.33.';
    } else if (regime === 'continuation') {
      scanEl.textContent = 'z = ' + fmt(z, 2) + ' · continuation-test region';
      regEl.textContent = 'Lyα continuation test';
      regEl.style.color = '#ffb020';
      badge.textContent = '1.8 < z ≤ 2.33 · continuation test';
      interp.textContent =
        'The compact order-3 continuation fails here; this point is not ' +
        'part of the validated reconstruction domain.';
    } else {
      scanEl.textContent = 'z = ' + fmt(z, 2) + ' · constrained domain';
      regEl.textContent = 'validated paper domain';
      regEl.style.color = '#4da3ff';
      badge.textContent = 'z ≤ 1.8 constrained';
      interp.textContent =
        'At this redshift, the distance-sector history and Planck reference ' +
        'assign slightly different expansion/distance relationships; the ' +
        'connecting spokes exaggerate that difference.';
      if (Math.abs(z - 0.65) < 0.15) {
        interp.textContent +=
          ' Largest endpoint separation occurs in this broad ' +
          'low/intermediate-redshift region.';
      }
    }
  }

  /* ---------------- sphere rendering (p5) ---------------- */

  function shellWeight(zi, zScan, width) {
    var d = (zi - zScan) / width;
    return Math.exp(-0.5 * d * d);
  }

  function rotatePoint(p, cosY, sinY, cosP, sinP) {
    var x1 = p.x * cosY + p.z * sinY;
    var z1 = -p.x * sinY + p.z * cosY;
    var y2 = p.y * cosP - z1 * sinP;
    var z2 = p.y * sinP + z1 * cosP;
    return { x: x1, y: y2, z: z2 };
  }

  function startSphere() {
    var holder = $('sphere-holder');
    var sketch = function (pp) {
      var canvas = null;
      pp.setup = function () {
        var w = Math.max(320, holder.clientWidth);
        var h = Math.max(320, holder.clientHeight);
        canvas = pp.createCanvas(w, h);
        canvas.parent(holder);
        pp.textFont('system-ui, sans-serif');
      };
      pp.windowResized = function () {
        var w = Math.max(320, holder.clientWidth);
        var h = Math.max(320, holder.clientHeight);
        pp.resizeCanvas(w, h);
      };
      pp.draw = function () {
        var dt = Math.min(0.05, (pp.deltaTime || 16.7) / 1000);
        step(dt);
        renderSphere(pp);
        drawGraphs();
        updateHud();
      };
    };
    state.sphereSketch = new p5(sketch, holder);
  }

  function step(dt) {
    if (state.playing && state.data) {
      state.animationProgress += dt * 0.045;
      if (state.animationProgress > 1) state.animationProgress -= 1;
      state.yaw += dt * 0.12;
    }
    state.zScan = zScanOf(state.animationProgress);
    state.aVisual = aVisualOf(state.animationProgress);
    var peakDist = (state.zScan - 0.65) / 0.25;
    state.peakBoost = 1 + 1.5 * Math.exp(-peakDist * peakDist);
  }

  function renderSphere(pp) {
    var w = pp.width;
    var h = pp.height;
    pp.background(5, 8, 14);
    var cx = w / 2;
    var cy = h / 2;

    // Seeded, flicker-free background stars (much dimmer than tracers).
    pp.noStroke();
    for (var s = 0; s < state.stars.length; s++) {
      var st = state.stars[s];
      pp.fill(150, 170, 210, st.a);
      pp.circle(st.x * w, st.y * h, st.r * 2);
    }

    if (!state.data) {
      pp.fill(211, 229, 255);
      pp.textAlign(pp.CENTER, pp.CENTER);
      pp.textSize(15);
      pp.text(
        state.loadError
          ? 'Could not load publication data (' + state.loadError + ').'
          : 'Loading frozen publication numbers…',
        cx,
        cy
      );
      return;
    }

    var regime = regimeOf(state.zScan);
    var worldR = Math.min(w, h) * 0.3 * state.zoom;
    var cosY = Math.cos(state.yaw);
    var sinY = Math.sin(state.yaw);
    var cosP = Math.cos(state.pitch);
    var sinP = Math.sin(state.pitch);
    var width = state.data.display_defaults.shell_width;
    var dim = regime === 'early' ? 0.35 : 1.0;

    // Faint reference outline of the present-day visual sphere.
    pp.noFill();
    pp.stroke(60, 80, 115, 90);
    pp.strokeWeight(1);
    pp.circle(cx, cy, 2 * worldR * state.aVisual);

    // Scan shell ring at the C1 radius of the cursor redshift.
    if (state.zScan <= 2.33) {
      var dmMax =
        state.data.curves.DM_C1[state.data.curves.DM_C1.length - 1];
      var shellR =
        (linInterp(
          state.data.curves.z,
          state.data.curves.DM_C1,
          clamp(state.zScan, 0, 2.33)
        ) /
          dmMax) *
        worldR *
        state.aVisual;
      pp.stroke(220, 230, 245, 40);
      pp.circle(cx, cy, 2 * shellR);
    }

    // Project every tracer pair, then depth-sort (far first).
    var items = [];
    for (var i = 0; i < state.tracers.length; i++) {
      var tr = state.tracers[i];
      var disp = displayRadii(tr, state.exaggerationFactor);
      var pR = {
        x: tr.dir.x * disp.displayRadiusR * state.aVisual,
        y: tr.dir.y * disp.displayRadiusR * state.aVisual,
        z: tr.dir.z * disp.displayRadiusR * state.aVisual
      };
      var pC = {
        x: tr.dir.x * disp.displayRadiusC1 * state.aVisual,
        y: tr.dir.y * disp.displayRadiusC1 * state.aVisual,
        z: tr.dir.z * disp.displayRadiusC1 * state.aVisual
      };
      var rR = rotatePoint(pR, cosY, sinY, cosP, sinP);
      var rC = rotatePoint(pC, cosY, sinY, cosP, sinP);
      var weight = shellWeight(tr.z, state.zScan, width);
      items.push({ tr: tr, rR: rR, rC: rC, weight: weight });
    }
    items.sort(function (a, b) {
      return (
        Math.min(a.rR.z, a.rC.z) - Math.min(b.rR.z, b.rC.z)
      );
    });

    state.proj = [];
    for (var k = 0; k < items.length; k++) {
      var it = items[k];
      var wgt = it.weight;
      var sR = PERSP / (PERSP - it.rR.z);
      var sC = PERSP / (PERSP - it.rC.z);
      var sxR = cx + it.rR.x * worldR * sR;
      var syR = cy - it.rR.y * worldR * sR;
      var sxC = cx + it.rC.x * worldR * sC;
      var syC = cy - it.rC.y * worldR * sC;
      state.proj.push({ sx: (sxR + sxC) / 2, sy: (syR + syC) / 2, tr: it.tr });

      var bright = 0.06 + 0.94 * wgt;
      var alpha = dim * bright * state.peakBoost;
      if (alpha > 1) alpha = 1;

      if (state.showPairLines) {
        pp.stroke(200, 212, 232, 14 + 150 * alpha);
        pp.strokeWeight(1);
        pp.line(sxR, syR, sxC, syC);
      }
      var pr = 1.1 + 2.2 * wgt;
      pp.noStroke();
      // C1 Planck-compatible reference (red).
      pp.fill(255, 90, 90, 30 + 225 * alpha);
      pp.circle(sxC, syC, pr * 2);
      // R distance-sector endpoint (blue).
      pp.fill(77, 163, 255, 30 + 225 * alpha);
      pp.circle(sxR, syR, pr * 2);

      if (state.showC2) {
        // C2 hugs the displayed C1 position: its small unexaggerated true
        // offset is rotated into the current frame and added to the
        // rotated C1 point, then drawn as an amber halo.
        var gapC = it.tr.trueRadiusC2 - it.tr.trueRadiusC1;
        var oVec = rotatePoint(
          {
            x: it.tr.dir.x * gapC * state.aVisual,
            y: it.tr.dir.y * gapC * state.aVisual,
            z: it.tr.dir.z * gapC * state.aVisual
          },
          cosY,
          sinY,
          cosP,
          sinP
        );
        var so = PERSP / (PERSP - (it.rC.z + oVec.z));
        var sxO = cx + (it.rC.x + oVec.x) * worldR * so;
        var syO = cy - (it.rC.y + oVec.y) * worldR * so;
        pp.noFill();
        pp.stroke(255, 176, 32, 40 + 200 * alpha);
        pp.strokeWeight(1.2);
        pp.circle(sxO, syO, pr * 2 + 5);
      }
    }

    // Hovered tracer gets a marker ring.
    if (state.hoverIndex >= 0 && state.hoverIndex < state.proj.length) {
      var hp = state.proj[state.hoverIndex];
      pp.noFill();
      pp.stroke(255, 255, 255, 220);
      pp.strokeWeight(1.4);
      pp.circle(hp.sx, hp.sy, 16);
    }

    // Regime caption inside the canvas.
    pp.noStroke();
    pp.textAlign(pp.LEFT, pp.TOP);
    pp.textSize(12);
    if (regime === 'early') {
      pp.fill(147, 165, 196);
      pp.text('illustrative early era — no paper inference', 12, 10);
    } else if (regime === 'continuation') {
      pp.fill(255, 176, 32);
      pp.text('continuation-test region 1.8 < z ≤ 2.33', 12, 10);
    } else {
      pp.fill(77, 163, 255);
      pp.text('constrained paper domain z ≤ 1.8', 12, 10);
    }
    updateTooltip();
  }

  /* ---------------- hover inspection ---------------- */

  function setupHover() {
    var holder = $('sphere-holder');
    var tip = $('tooltip');
    holder.addEventListener('mousemove', function (ev) {
      var rect = holder.getBoundingClientRect();
      var mx = ev.clientX - rect.left;
      var my = ev.clientY - rect.top;
      var best = -1;
      var bestD2 = 16 * 16;
      for (var i = 0; i < state.proj.length; i++) {
        var dx = state.proj[i].sx - mx;
        var dy = state.proj[i].sy - my;
        var d2 = dx * dx + dy * dy;
        if (d2 < bestD2) {
          bestD2 = d2;
          best = i;
        }
      }
      state.hoverIndex = best;
      if (best < 0 || !state.data) {
        tip.hidden = true;
        return;
      }
      var tr = state.proj[best].tr;
      var dmMax =
        state.data.curves.DM_C1[state.data.curves.DM_C1.length - 1];
      var dmR = tr.trueRadiusR * dmMax;
      var dmC1 = tr.trueRadiusC1 * dmMax;
      var frac = (dmR - dmC1) / dmC1;
      tip.innerHTML =
        'synthetic tracer #' +
        tr.id +
        '<br>nominal z = ' +
        fmt(tr.z, 3) +
        '<br>D_M(R) = ' +
        fmt(dmR, 1) +
        ' Mpc<br>D_M(C1) = ' +
        fmt(dmC1, 1) +
        ' Mpc<br>displayed exaggeration ×' +
        state.exaggerationFactor +
        '<br>true fractional distance difference = ' +
        (frac >= 0 ? '+' : '') +
        fmt(100 * frac, 2) +
        '%';
      tip.hidden = false;
      var stage = $('stage-card').getBoundingClientRect();
      tip.style.left = ev.clientX - stage.left + 14 + 'px';
      tip.style.top = ev.clientY - stage.top + 10 + 'px';
    });
    holder.addEventListener('mouseleave', function () {
      state.hoverIndex = -1;
      tip.hidden = true;
    });
  }

  function updateTooltip() {
    // Hide the tooltip if its tracer scrolled out of range.
    var tip = $('tooltip');
    if (state.hoverIndex < 0) tip.hidden = true;
  }

  /* ---------------- interaction ---------------- */

  function cycleExaggeration() {
    var opts = state.exaggerationOptions;
    var i = opts.indexOf(state.exaggerationFactor);
    state.exaggerationFactor = opts[(i + 1) % opts.length];
    updateBadge();
  }

  function toggleHelp() {
    var panel = $('help-panel');
    var btn = $('help-btn');
    var show = panel.hidden;
    panel.hidden = !show;
    btn.setAttribute('aria-expanded', show ? 'true' : 'false');
  }

  function toggleGraphs() {
    state.showGraphs = !state.showGraphs;
    $('dashboard').style.display = state.showGraphs ? '' : 'none';
  }

  function setupInteraction() {
    var holder = $('sphere-holder');
    holder.addEventListener('mousedown', function (ev) {
      state.mouseDown = true;
      state.lastPX = ev.clientX;
      state.lastPY = ev.clientY;
    });
    window.addEventListener('mouseup', function () {
      state.mouseDown = false;
    });
    holder.addEventListener('mousemove', function (ev) {
      if (!state.mouseDown) return;
      state.yaw += (ev.clientX - state.lastPX) * 0.005;
      state.pitch = clamp(
        state.pitch + (ev.clientY - state.lastPY) * 0.005,
        -1.2,
        1.2
      );
      state.lastPX = ev.clientX;
      state.lastPY = ev.clientY;
    });
    holder.addEventListener(
      'wheel',
      function (ev) {
        ev.preventDefault();
        state.zoom = clamp(state.zoom * Math.exp(-ev.deltaY * 0.001), 0.55, 2.6);
      },
      { passive: false }
    );
    document.addEventListener('keydown', function (ev) {
      if (ev.target && (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA')) return;
      switch (ev.key) {
        case ' ':
          ev.preventDefault();
          state.playing = !state.playing;
          break;
        case 'ArrowRight':
          ev.preventDefault();
          state.playing = false;
          state.animationProgress = clamp(state.animationProgress + 0.02, 0, 1);
          break;
        case 'ArrowLeft':
          ev.preventDefault();
          state.playing = false;
          state.animationProgress = clamp(state.animationProgress - 0.02, 0, 1);
          break;
        case 'r':
        case 'R':
          state.animationProgress = 0;
          state.playing = true;
          break;
        case 's':
        case 'S':
          if (state.sphereSketch) state.sphereSketch.saveCanvas('rde_sphere', 'png');
          break;
        case 'c':
        case 'C':
          state.showC2 = !state.showC2;
          break;
        case 'l':
        case 'L':
          state.showPairLines = !state.showPairLines;
          break;
        case 'g':
        case 'G':
          toggleGraphs();
          break;
        case 'e':
        case 'E':
          cycleExaggeration();
          break;
        case 'h':
        case 'H':
          toggleHelp();
          break;
      }
    });
    $('help-btn').addEventListener('click', toggleHelp);
  }

  /* ---------------- dashboard graphs (plain 2-D canvas) ---------------- */

  function fitCanvas(id) {
    var cv = $(id);
    var dpr = window.devicePixelRatio || 1;
    var w = cv.clientWidth || 300;
    var h = parseInt(cv.getAttribute('height'), 10) || 220;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
      cv.width = Math.round(w * dpr);
      cv.height = Math.round(h * dpr);
    }
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx: ctx, w: w, h: h };
  }

  var ML = 46;
  var MR = 10;
  var MT = 10;
  var MB = 22;

  function xPix(z, w) {
    return ML + (z / 2.33) * (w - ML - MR);
  }

  function yPix(v, vmin, vmax, h) {
    return MT + (1 - (v - vmin) / (vmax - vmin)) * (h - MT - MB);
  }

  function drawFrame(g, title, vmin, vmax, yticks) {
    var ctx = g.ctx;
    var w = g.w;
    var h = g.h;
    ctx.clearRect(0, 0, w, h);
    // Constrained domain shading (z <= 1.8) and continuation band.
    ctx.fillStyle = 'rgba(77,163,255,0.07)';
    ctx.fillRect(xPix(0, w), MT, xPix(1.8, w) - xPix(0, w), h - MT - MB);
    ctx.fillStyle = 'rgba(255,176,32,0.08)';
    ctx.fillRect(xPix(1.8, w), MT, xPix(2.33, w) - xPix(1.8, w), h - MT - MB);
    // Gridlines.
    ctx.strokeStyle = '#1c2942';
    ctx.fillStyle = '#93a5c4';
    ctx.font = '10px ui-monospace, monospace';
    ctx.textAlign = 'right';
    ctx.lineWidth = 1;
    for (var i = 0; i < yticks.length; i++) {
      var yy = yPix(yticks[i], vmin, vmax, h);
      ctx.beginPath();
      ctx.moveTo(ML, yy);
      ctx.lineTo(w - MR, yy);
      ctx.stroke();
      ctx.fillText(String(yticks[i]), ML - 4, yy + 3);
    }
    // x ticks.
    ctx.textAlign = 'center';
    var xticks = [0, 0.5, 1.0, 1.5, 2.0, 2.33];
    for (var j = 0; j < xticks.length; j++) {
      var xx = xPix(xticks[j], w);
      if (xticks[j] === 2.33) {
        ctx.textAlign = 'right';
        ctx.fillText('2.33 Lyα', w - MR - 2, h - 6);
        ctx.textAlign = 'center';
      } else {
        ctx.fillText(String(xticks[j]), xx, h - 6);
      }
    }
    // Ly-alpha marker.
    ctx.strokeStyle = 'rgba(255,176,32,0.55)';
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.moveTo(xPix(2.33, w), MT);
    ctx.lineTo(xPix(2.33, w), h - MB);
    ctx.stroke();
    ctx.setLineDash([]);
    // Moving cursor at the scan redshift.
    if (state.zScan <= 2.34) {
      var zc = clamp(state.zScan, 0, 2.33);
      ctx.strokeStyle = 'rgba(230,238,250,0.75)';
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.moveTo(xPix(zc, w), MT);
      ctx.lineTo(xPix(zc, w), h - MB);
      ctx.stroke();
      ctx.lineWidth = 1;
    }
    void title;
  }

  function polyline(g, xs, ys, vmin, vmax, color, dash, width) {
    var ctx = g.ctx;
    ctx.strokeStyle = color;
    ctx.lineWidth = width || 1.6;
    ctx.setLineDash(dash || []);
    ctx.beginPath();
    for (var i = 0; i < xs.length; i++) {
      var xx = xPix(xs[i], g.w);
      var yy = yPix(ys[i], vmin, vmax, g.h);
      if (i === 0) ctx.moveTo(xx, yy);
      else ctx.lineTo(xx, yy);
    }
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.lineWidth = 1;
  }

  function legend(g, entries, pos) {
    var ctx = g.ctx;
    var w = g.w;
    var h = g.h;
    var x = ML + 6;
    var y = MT + 6;
    if (pos === 'bl') y = h - MB - entries.length * 14 - 2;
    if (pos === 'tr') x = w - MR - 172;
    ctx.font = '10px system-ui, sans-serif';
    ctx.textAlign = 'left';
    for (var i = 0; i < entries.length; i++) {
      ctx.strokeStyle = entries[i][1];
      ctx.lineWidth = 2;
      ctx.setLineDash(entries[i][2] || []);
      ctx.beginPath();
      ctx.moveTo(x, y - 3);
      ctx.lineTo(x + 16, y - 3);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = '#d7e5ff';
      ctx.fillText(entries[i][0], x + 20, y);
      y += 14;
    }
    ctx.lineWidth = 1;
  }

  function drawGraphH() {
    var g = fitCanvas('graph-h');
    var d = state.data;
    if (!d) return;
    var c = d.curves;
    drawFrame(g, '', 60, 270, [80, 140, 200, 260]);
    polyline(g, c.z, c.H_C2, 60, 270, '#ffb020', [], 1.2);
    polyline(g, c.z, c.H_C1, 60, 270, '#ff5a5a', [], 1.6);
    polyline(g, c.z, c.H_R, 60, 270, '#4da3ff', [], 1.6);
    legend(g, [
      ['R distance sector', '#4da3ff'],
      ['C1 Planck reference', '#ff5a5a'],
      ['C2 sensitivity ref', '#ffb020']
    ], 'bl');
  }

  function drawGraphD() {
    var g = fitCanvas('graph-d');
    var d = state.data;
    if (!d) return;
    var c = d.curves;
    drawFrame(g, '', -0.01, 0.135, [0, 0.05, 0.1]);
    polyline(g, c.z, c.deltaC, -0.01, 0.135, '#ffb020', [], 1.2);
    polyline(g, c.z, c.m3, -0.01, 0.135, '#9aa7bd', [5, 3], 1.3);
    polyline(g, c.z, c.delta2, -0.01, 0.135, '#8fc6ff', [], 1.4);
    polyline(g, c.z, c.delta1, -0.01, 0.135, '#4da3ff', [], 1.6);
    legend(g, [
      ['Δ1 = ln HR − ln HC1', '#4da3ff'],
      ['Δ2 = ln HR − ln HC2', '#8fc6ff'],
      ['ΔC = ln HC1 − ln HC2', '#ffb020'],
      ['five-coordinate approx (order 3)', '#9aa7bd', [5, 3]]
    ], 'tr');
  }

  function drawGraphCV() {
    var cv = $('graph-cv');
    var held = document.getElementById('dashboard').style.display === 'none';
    var g = fitCanvas('graph-cv');
    var ctx = g.ctx;
    var d = state.data;
    if (!d || held) {
      if (held) return;
      if (!d) return;
    }
    var v = d.validation;
    var min = Math.min.apply(null, v.cv_combined_constrained);
    var vals = v.cv_combined_constrained.map(function (x) {
      return x - min;
    });
    var vmax = Math.max.apply(null, vals.concat([3])) * 1.15;
    // Frame without the redshift cursor semantics (categorical x axis).
    ctx.clearRect(0, 0, g.w, g.h);
    var n = v.cv_orders.length;
    var slot = (g.w - ML - MR) / n;
    var bw = Math.min(46, slot * 0.55);
    ctx.font = '10px ui-monospace, monospace';
    // y grid.
    var ticks = [0, 10, 20, 30, 40, 50];
    ctx.textAlign = 'right';
    for (var t = 0; t < ticks.length; t++) {
      if (ticks[t] > vmax) continue;
      var yy = yPix(ticks[t], 0, vmax, g.h);
      ctx.strokeStyle = '#1c2942';
      ctx.beginPath();
      ctx.moveTo(ML, yy);
      ctx.lineTo(g.w - MR, yy);
      ctx.stroke();
      ctx.fillStyle = '#93a5c4';
      ctx.fillText(String(ticks[t]), ML - 4, yy + 3);
    }
    // Threshold line at minimum + 2.
    var y2 = yPix(2.0, 0, vmax, g.h);
    ctx.strokeStyle = 'rgba(255,255,255,0.6)';
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    ctx.moveTo(ML, y2);
    ctx.lineTo(g.w - MR, y2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#d7e5ff';
    ctx.textAlign = 'left';
    ctx.fillText('min + 2', ML + 4, y2 - 4);
    // Bars.
    ctx.textAlign = 'center';
    for (var i = 0; i < n; i++) {
      var xx = ML + slot * (i + 0.5);
      var yTop = yPix(vals[i], 0, vmax, g.h);
      var yBase = yPix(0, 0, vmax, g.h);
      var order = v.cv_orders[i];
      var isSel = order === v.selected_order;
      var isMin = order === v.raw_min_order;
      ctx.fillStyle = isSel ? '#4da3ff' : '#5a6c8f';
      ctx.fillRect(xx - bw / 2, yTop, bw, yBase - yTop);
      if (isMin && !isSel) {
        ctx.strokeStyle = '#ffb020';
        ctx.lineWidth = 2;
        ctx.strokeRect(xx - bw / 2, Math.min(yTop, yBase - 2), bw, Math.max(2, yBase - yTop));
        ctx.lineWidth = 1;
      }
      ctx.fillStyle = '#d7e5ff';
      ctx.fillText('m' + order, xx, g.h - 6);
      // Tall bars get their above-minimum value; near-zero bars are
      // annotated once at the top of the panel instead of per-bar.
      if (yBase - yTop > 26) {
        ctx.fillText('+' + vals[i].toFixed(1), xx, yTop - 5);
      }
    }
    // Selection annotations, top-right where the short bars leave space.
    ctx.textAlign = 'right';
    ctx.fillStyle = '#4da3ff';
    ctx.fillText('selected → m' + v.selected_order, g.w - MR - 4, MT + 12);
    ctx.fillStyle = '#ffb020';
    ctx.fillText('raw min → m' + v.raw_min_order, g.w - MR - 4, MT + 26);
  }

  function drawGraphs() {
    if (!state.showGraphs) return;
    drawGraphH();
    drawGraphD();
    drawGraphCV();
  }

  /* ---------------- boot ---------------- */

  document.addEventListener('DOMContentLoaded', function () {
    loadData();
    startSphere();
    setupHover();
    setupInteraction();
    updateBadge();
  });

  // Exposed for tests and debugging (read-only snapshot).
  window.__rdeState = state;
  window.__rdePure = {
    mulberry32: mulberry32,
    linInterp: linInterp,
    invertMonotone: invertMonotone,
    zScanOf: zScanOf,
    aVisualOf: aVisualOf,
    displayRadii: displayRadii,
    easeOutCubic: easeOutCubic
  };
})();
