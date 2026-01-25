/*
  Grafana-style customer dashboard (frontend-only placeholder).
  - Generates smooth-ish live looking data.
  - Draws simple line charts on <canvas>.
  - Updates headline KPIs and status.
  - Safe to run even if no machines are rendered.
*/

(() => {
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const nowTs = () => Date.now();

  class Series {
    constructor({ points = 120, min = 0, max = 100, start = null, volatility = 0.06, drift = 0.0 } = {}) {
      this.points = points;
      this.min = min;
      this.max = max;
      this.volatility = volatility;
      this.drift = drift;
      const mid = (min + max) / 2;
      const first = start == null ? mid : start;
      this.data = Array.from({ length: points }, () => first);
      this.target = first;
    }

    step() {
      // Gently wander target
      const span = (this.max - this.min);
      const noise = (Math.random() - 0.5) * span * this.volatility;
      this.target = clamp(this.target + noise + (this.drift * span), this.min, this.max);

      // Smooth towards target
      const last = this.data[this.data.length - 1];
      const next = lerp(last, this.target, 0.35);

      this.data.push(next);
      if (this.data.length > this.points) this.data.shift();
      return next;
    }

    latest() {
      return this.data[this.data.length - 1];
    }
  }

  function formatNumber(v, digits = 0) {
    const n = Number(v);
    if (!Number.isFinite(n)) return "—";
    return n.toFixed(digits);
  }

  function niceTime(date = new Date()) {
    const hh = String(date.getHours()).padStart(2, '0');
    const mm = String(date.getMinutes()).padStart(2, '0');
    const ss = String(date.getSeconds()).padStart(2, '0');
    return `${hh}:${mm}:${ss}`;
  }

  function drawLineChart(canvas, series, opts = {}) {
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(1, Math.floor(rect.width * dpr));
    const h = Math.max(1, Math.floor(rect.height * dpr));

    if (canvas.width !== w) canvas.width = w;
    if (canvas.height !== h) canvas.height = h;

    const pad = (opts.padding ?? 18) * dpr;
    const bg = opts.background ?? 'transparent';

    // Background
    if (bg !== 'transparent') {
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, w, h);
    } else {
      ctx.clearRect(0, 0, w, h);
    }

    // Grid
    ctx.save();
    ctx.globalAlpha = 0.5;
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.lineWidth = 1 * dpr;
    const gridY = 4;
    for (let i = 1; i <= gridY; i++) {
      const y = pad + ((h - pad * 2) * i / (gridY + 1));
      ctx.beginPath();
      ctx.moveTo(pad, y);
      ctx.lineTo(w - pad, y);
      ctx.stroke();
    }
    ctx.restore();

    const data = series.data;
    const min = opts.min ?? series.min;
    const max = opts.max ?? series.max;
    const range = Math.max(1e-9, max - min);

    const x0 = pad;
    const x1 = w - pad;
    const y0 = h - pad;
    const y1 = pad;

    // Path
    ctx.save();
    ctx.lineWidth = (opts.lineWidth ?? 2.25) * dpr;
    ctx.strokeStyle = opts.stroke ?? 'rgba(90,169,255,0.95)';
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    ctx.beginPath();
    for (let i = 0; i < data.length; i++) {
      const t = i / (data.length - 1);
      const x = x0 + (x1 - x0) * t;
      const v = data[i];
      const yn = (v - min) / range;
      const y = y0 - (y0 - y1) * yn;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Soft fill
    if (opts.fill) {
      ctx.globalAlpha = 0.20;
      ctx.fillStyle = opts.stroke ?? 'rgba(90,169,255,0.95)';
      ctx.lineTo(x1, y0);
      ctx.lineTo(x0, y0);
      ctx.closePath();
      ctx.fill();
    }

    ctx.restore();
  }

  function chooseStatus(packs) {
    // If packs very low -> Stopped; otherwise Running; occasionally Fault
    const r = Math.random();
    if (r < 0.02) return 'FAULT';
    if (packs < 2.0) return 'STOPPED';
    return 'RUNNING';
  }

  function statusToClass(s) {
    const st = String(s || '').toUpperCase();
    if (st === 'RUNNING') return 'is-running';
    if (st === 'STOPPED') return 'is-stopped';
    if (st === 'FAULT' || st === 'ERROR') return 'is-fault';
    return 'is-stopped';
  }

  function renderMachine(machineEl) {
    const id = machineEl.dataset.machineId || '';
    const points = 140;

    // Baselines per machine, so they don't all look identical
    const seed = Array.from(id).reduce((a, c) => a + c.charCodeAt(0), 0) || 42;
    const rand = () => {
      // tiny deterministic-ish jitter using seed plus Math.random
      return ((seed % 97) / 97) * 0.4 + Math.random() * 0.6;
    };

    const packs = new Series({ points, min: 0, max: 45, start: 18 + rand() * 8, volatility: 0.10, drift: 0.0 });
    const eff = new Series({ points, min: 40, max: 98, start: 78 + rand() * 6, volatility: 0.05, drift: 0.0 });
    const power = new Series({ points, min: 1.2, max: 6.5, start: 3.2 + rand() * 1.4, volatility: 0.08, drift: 0.0 });
    const heater = new Series({ points, min: 120, max: 220, start: 165 + rand() * 12, volatility: 0.03, drift: 0.0 });

    let batchCount = Math.floor(4000 + rand() * 5000);
    let lastPulseTs = nowTs();

    const elPacks = machineEl.querySelector('[data-kpi="packs"]');
    const elBatch = machineEl.querySelector('[data-kpi="batch"]');
    const elPower = machineEl.querySelector('[data-kpi="power"]');
    const elStatus = machineEl.querySelector('[data-kpi="status"]');
    const pill = machineEl.querySelector('[data-status-pill]');
    const lastUpdate = machineEl.querySelector('[data-last-update]');

    const canvPacks = machineEl.querySelector('[data-chart="packs"]');
    const canvEff = machineEl.querySelector('[data-chart="eff"]');
    const canvPower = machineEl.querySelector('[data-chart="power"]');
    const canvHeater = machineEl.querySelector('[data-chart="heater"]');

    // Seed list items with placeholder timestamps
    const errList = machineEl.querySelector('[data-errors]');
    const logList = machineEl.querySelector('[data-logs]');

    const pushListItem = (listEl, { title, meta, badgeText, badgeClass } = {}) => {
      if (!listEl) return;
      const item = document.createElement('div');
      item.className = 'list-item';
      item.innerHTML = `
        <div class="badge ${badgeClass || 'is-info'}">${badgeText || ''}</div>
        <div class="list-item__body">
          <p class="list-item__title">${title || ''}</p>
          <p class="list-item__meta">${meta || ''}</p>
        </div>
      `;
      listEl.prepend(item);
      // keep list short
      while (listEl.children.length > 6) listEl.removeChild(listEl.lastChild);
    };

    // Initial content
    if (logList && logList.children.length === 0) {
      pushListItem(logList, { title: 'Dashboard connected', meta: `Live UI simulation started at ${niceTime()}`, badgeText: 'INFO', badgeClass: 'is-info' });
    }

    function tick() {
      const p = packs.step();
      const e = eff.step();
      const pw = power.step();
      heater.step();

      // Batch count rises with production
      const dt = (nowTs() - lastPulseTs) / 1000;
      if (dt > 0.8) {
        const inc = Math.max(0, Math.round((p / 60) * dt * 60 * 0.6)); // pseudo
        batchCount += inc;
        lastPulseTs = nowTs();
      }

      // Status logic (simple)
      const st = chooseStatus(p);
      if (elStatus) elStatus.textContent = st;
      if (pill) {
        pill.textContent = st;
        pill.classList.remove('is-running', 'is-stopped', 'is-fault');
        pill.classList.add(statusToClass(st));
      }

      if (elPacks) elPacks.textContent = `${formatNumber(p, 1)}`;
      if (elBatch) elBatch.textContent = `${batchCount.toLocaleString()}`;
      if (elPower) elPower.textContent = `${formatNumber(pw, 2)}`;
      if (lastUpdate) lastUpdate.textContent = niceTime();

      // Draw charts
      if (canvPacks) drawLineChart(canvPacks, packs, { min: 0, max: 45, stroke: 'rgba(90,169,255,0.95)', fill: true });
      if (canvEff) drawLineChart(canvEff, eff, { min: 40, max: 100, stroke: 'rgba(53,208,127,0.95)', fill: true });
      if (canvPower) drawLineChart(canvPower, power, { min: 1.0, max: 7.0, stroke: 'rgba(200,120,255,0.95)', fill: true });
      if (canvHeater) drawLineChart(canvHeater, heater, { min: 120, max: 220, stroke: 'rgba(255,176,32,0.95)', fill: true });

      // Occasionally create a "fault" message
      if (st === 'FAULT' && errList && Math.random() < 0.6) {
        const codes = ['E-26 Servo Not Ready', 'E-83 Overcurrent', 'Film Low', 'Heater Out of Range', 'E-07 Guard Open'];
        const code = codes[Math.floor(Math.random() * codes.length)];
        pushListItem(errList, {
          title: code,
          meta: `Detected ${niceTime()} • Please contact support if persistent`,
          badgeText: 'FAULT',
          badgeClass: 'is-fault'
        });
        pushListItem(logList, {
          title: `Alarm logged: ${code}`,
          meta: `Auto-generated event at ${niceTime()}`,
          badgeText: 'ALARM',
          badgeClass: 'is-warn'
        });
      }
    }

    // Render at 1 Hz
    tick();
    const timer = window.setInterval(tick, 1000);

    // Redraw charts on resize
    const onResize = () => {
      if (canvPacks) drawLineChart(canvPacks, packs, { min: 0, max: 45, stroke: 'rgba(90,169,255,0.95)', fill: true });
      if (canvEff) drawLineChart(canvEff, eff, { min: 40, max: 100, stroke: 'rgba(53,208,127,0.95)', fill: true });
      if (canvPower) drawLineChart(canvPower, power, { min: 1.0, max: 7.0, stroke: 'rgba(200,120,255,0.95)', fill: true });
      if (canvHeater) drawLineChart(canvHeater, heater, { min: 120, max: 220, stroke: 'rgba(255,176,32,0.95)', fill: true });
    };
    window.addEventListener('resize', onResize);

    // Cleanup hook if you ever hot-swap
    machineEl._dashDispose = () => {
      window.clearInterval(timer);
      window.removeEventListener('resize', onResize);
    };
  }

  function boot() {
    const machines = Array.from(document.querySelectorAll('[data-machine]'));
    machines.forEach(renderMachine);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
