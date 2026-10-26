/**
 * LearnSphere AI - Interactive Visual Lab
 * 1. Linear Equation Graph Plotter (y = mx + c)
 * 2. Newton's Laws & Force Balance Physics Simulation
 * 3. Photosynthesis Interactive Cellular Simulation
 */

class VisualLab {
  constructor() {
    this.graphCanvas = null;
    this.graphCtx = null;
    this.slope = 2;
    this.intercept = -1;

    this.forceCanvas = null;
    this.forceCtx = null;
    this.appliedForce = 20; // Newtons
    this.frictionForce = 20; // Newtons (balanced initially)
    this.mass = 5; // kg
    this.boxPos = 120;
    this.boxVel = 0;
    this.animId = null;
  }

  init() {
    this.initGraphPlotter();
    this.initForceSimulation();
  }

  // ==========================================
  // 1. LINEAR EQUATION GRAPH PLOTTER
  // ==========================================
  initGraphPlotter() {
    this.graphCanvas = document.getElementById("graph-canvas");
    if (!this.graphCanvas) return;
    this.graphCtx = this.graphCanvas.getContext("2d");

    const slopeSlider = document.getElementById("slope-slider");
    const interceptSlider = document.getElementById("intercept-slider");
    const slopeVal = document.getElementById("slope-val");
    const interceptVal = document.getElementById("intercept-val");

    if (slopeSlider) {
      slopeSlider.addEventListener("input", (e) => {
        this.slope = parseFloat(e.target.value);
        if (slopeVal) slopeVal.textContent = this.slope;
        this.drawGraph();
      });
    }

    if (interceptSlider) {
      interceptSlider.addEventListener("input", (e) => {
        this.intercept = parseFloat(e.target.value);
        if (interceptVal) interceptVal.textContent = this.intercept;
        this.drawGraph();
      });
    }

    this.drawGraph();
  }

  drawGraph() {
    if (!this.graphCtx) return;
    const ctx = this.graphCtx;
    const w = this.graphCanvas.width;
    const h = this.graphCanvas.height;
    const originX = w / 2;
    const originY = h / 2;
    const scale = 22; // pixels per unit

    // Clear
    ctx.clearRect(0, 0, w, h);

    // Background Grid
    ctx.strokeStyle = "rgba(255, 255, 255, 0.06)";
    ctx.lineWidth = 1;
    for (let x = originX % scale; x < w; x += scale) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = originY % scale; y < h; y += scale) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Axes
    ctx.strokeStyle = "rgba(255, 255, 255, 0.35)";
    ctx.lineWidth = 2;
    // X Axis
    ctx.beginPath();
    ctx.moveTo(0, originY);
    ctx.lineTo(w, originY);
    ctx.stroke();
    // Y Axis
    ctx.beginPath();
    ctx.moveTo(originX, 0);
    ctx.lineTo(originX, h);
    ctx.stroke();

    // Axis Labels
    ctx.fillStyle = "#94a3b8";
    ctx.font = "12px JetBrains Mono";
    ctx.fillText("X", w - 16, originY - 8);
    ctx.fillText("Y", originX + 8, 16);
    ctx.fillText("(0,0)", originX + 6, originY + 16);

    // Plot Line y = mx + c
    // Canvas y is inverted: canvasY = originY - (y * scale)
    ctx.strokeStyle = "#6366f1";
    ctx.lineWidth = 3;
    ctx.beginPath();

    const minX = -(originX / scale);
    const maxX = (w - originX) / scale;

    const startY = this.slope * minX + this.intercept;
    const endY = this.slope * maxX + this.intercept;

    const canvasStartX = 0;
    const canvasStartY = originY - startY * scale;
    const canvasEndX = w;
    const canvasEndY = originY - endY * scale;

    ctx.moveTo(canvasStartX, canvasStartY);
    ctx.lineTo(canvasEndX, canvasEndY);
    ctx.stroke();

    // Mark Y-intercept: (0, c)
    const yIntX = originX;
    const yIntY = originY - this.intercept * scale;
    ctx.fillStyle = "#f59e0b";
    ctx.beginPath();
    ctx.arc(yIntX, yIntY, 5, 0, Math.PI * 2);
    ctx.fill();

    // Mark X-intercept (Root): (-c/m, 0) if m != 0
    let rootText = "None (Horizontal Line)";
    if (this.slope !== 0) {
      const rootXVal = -this.intercept / this.slope;
      const rootCanvasX = originX + rootXVal * scale;
      const rootCanvasY = originY;

      ctx.fillStyle = "#10b981";
      ctx.beginPath();
      ctx.arc(rootCanvasX, rootCanvasY, 5, 0, Math.PI * 2);
      ctx.fill();

      rootText = `x = ${rootXVal.toFixed(2)}`;
    }

    // Update Equation Readout
    const eqReadout = document.getElementById("equation-readout");
    if (eqReadout) {
      const sign = this.intercept >= 0 ? "+" : "-";
      eqReadout.innerHTML = `Equation: <strong style="color:#6366f1;">y = ${this.slope}x ${sign} ${Math.abs(this.intercept)}</strong> | Root: <strong style="color:#10b981;">${rootText}</strong> | Y-Int: <strong style="color:#f59e0b;">(0, ${this.intercept})</strong>`;
    }
  }

  // ==========================================
  // 2. NEWTON'S 3RD LAW & BALANCED FORCE SIMULATION
  // ==========================================
  initForceSimulation() {
    this.forceCanvas = document.getElementById("force-canvas");
    if (!this.forceCanvas) return;
    this.forceCtx = this.forceCanvas.getContext("2d");

    const forceSlider = document.getElementById("force-slider");
    const forceVal = document.getElementById("force-val");
    const toggleBalanceBtn = document.getElementById("toggle-balance-btn");
    const resetForceBtn = document.getElementById("reset-force-btn");

    if (forceSlider) {
      forceSlider.addEventListener("input", (e) => {
        this.appliedForce = parseFloat(e.target.value);
        if (forceVal) forceVal.textContent = this.appliedForce;
      });
    }

    if (toggleBalanceBtn) {
      toggleBalanceBtn.addEventListener("click", () => {
        if (this.frictionForce === this.appliedForce) {
          // Make unbalanced
          this.frictionForce = Math.max(0, this.appliedForce - 15);
          toggleBalanceBtn.textContent = "Switch to Balanced Force (Net = 0)";
          toggleBalanceBtn.classList.add("btn-outline-danger");
        } else {
          // Make balanced
          this.frictionForce = this.appliedForce;
          toggleBalanceBtn.textContent = "Switch to Unbalanced Force";
          toggleBalanceBtn.classList.remove("btn-outline-danger");
        }
      });
    }

    if (resetForceBtn) {
      resetForceBtn.addEventListener("click", () => {
        this.boxPos = 120;
        this.boxVel = 0;
      });
    }

    this.startForceLoop();
  }

  startForceLoop() {
    const render = () => {
      this.updateAndDrawForce();
      this.animId = requestAnimationFrame(render);
    };
    render();
  }

  updateAndDrawForce() {
    if (!this.forceCtx) return;
    const ctx = this.forceCtx;
    const w = this.forceCanvas.width;
    const h = this.forceCanvas.height;

    // Physics calculations
    const netForce = this.appliedForce - this.frictionForce; // Horizontal
    const acceleration = netForce / this.mass;

    this.boxVel += acceleration * 0.05;
    this.boxPos += this.boxVel;

    // Boundary bounce/wrap
    const boxW = 80;
    const boxH = 50;
    const groundY = h - 60;

    if (this.boxPos > w - boxW - 20) {
      this.boxPos = w - boxW - 20;
      this.boxVel = 0;
    } else if (this.boxPos < 20) {
      this.boxPos = 20;
      this.boxVel = 0;
    }

    // Clear
    ctx.clearRect(0, 0, w, h);

    // Ground
    ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, groundY);
    ctx.lineTo(w, groundY);
    ctx.stroke();

    // Ground hatches
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.lineWidth = 1;
    for (let x = 10; x < w; x += 15) {
      ctx.beginPath();
      ctx.moveTo(x, groundY);
      ctx.lineTo(x - 10, groundY + 15);
      ctx.stroke();
    }

    // Box
    const boxY = groundY - boxH;
    ctx.fillStyle = "#3b82f6";
    ctx.strokeStyle = "#60a5fa";
    ctx.lineWidth = 2;
    ctx.fillRect(this.boxPos, boxY, boxW, boxH);
    ctx.strokeRect(this.boxPos, boxY, boxW, boxH);

    // Box Label
    ctx.fillStyle = "#fff";
    ctx.font = "bold 13px Plus Jakarta Sans";
    ctx.textAlign = "center";
    ctx.fillText(`Mass: ${this.mass}kg`, this.boxPos + boxW / 2, boxY + boxH / 2 + 5);

    // Force Vectors
    const centerX = this.boxPos + boxW / 2;
    const centerY = boxY + boxH / 2;

    // 1. Applied Push Force (Green arrow right)
    this.drawArrow(ctx, centerX + boxW / 2, centerY, centerX + boxW / 2 + this.appliedForce * 2.2, centerY, "#10b981", `Push: ${this.appliedForce}N`);

    // 2. Friction Force (Red arrow left)
    if (this.frictionForce > 0) {
      this.drawArrow(ctx, centerX - boxW / 2, centerY, centerX - boxW / 2 - this.frictionForce * 2.2, centerY, "#ef4444", `Friction: ${this.frictionForce}N`);
    }

    // 3. Normal Force (Up) & Gravity Force (Down)
    const gravityForce = this.mass * 9.8;
    this.drawArrow(ctx, centerX, boxY, centerX, boxY - 35, "#38bdf8", "Normal (Up)");
    this.drawArrow(ctx, centerX, boxY + boxH, centerX, boxY + boxH + 35, "#a855f7", "Gravity (Down)");

    // Status readout
    const statusBox = document.getElementById("force-status-readout");
    if (statusBox) {
      if (Math.abs(netForce) < 0.1) {
        statusBox.innerHTML = `<span style="color:#10b981; font-weight:700;">✅ BALANCED FORCES:</span> Net Force = 0 N. Acceleration = 0 m/s². The book/box remains at rest!`;
      } else {
        statusBox.innerHTML = `<span style="color:#ef4444; font-weight:700;">⚡ UNBALANCED FORCES:</span> Net Force = ${netForce.toFixed(1)} N. Acceleration = ${acceleration.toFixed(2)} m/s²! Object accelerates!`;
      }
    }
  }

  drawArrow(ctx, fromX, fromY, toX, toY, color, label) {
    const headlen = 8;
    const angle = Math.atan2(toY - fromY, toX - fromX);

    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headlen * Math.cos(angle - Math.PI / 6), toY - headlen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(toX - headlen * Math.cos(angle + Math.PI / 6), toY - headlen * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();

    // Label
    ctx.font = "11px JetBrains Mono";
    ctx.fillText(label, toX, toY - 8);
  }
}

window.visualLab = new VisualLab();
