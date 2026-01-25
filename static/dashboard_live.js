/* 
  Grafana-style Dashboard Simulator for Tray Sealer 
  Simulates WebSocket data streams and Canvas rendering
*/

// --- CONFIGURATION ---
const MAX_DATA_POINTS = 50;
const REFRESH_RATE = 1000; // 1 second updates for numbers
const ANIM_SPEED = 60; // Chart scrolling speed

// --- MOCK DATA GENERATOR ---
class MachineSimulator {
    constructor(id, name, targetPPM, targetTemp) {
        this.id = id;
        this.name = name;
        this.status = "RUNNING"; // RUNNING, STOPPED, ERROR
        this.targetPPM = targetPPM;
        this.targetTemp = targetTemp;
        
        // State
        this.currentPPM = 0;
        this.currentTemp = 0;
        this.batchCount = Math.floor(Math.random() * 1000);
        this.dwellTime = 0.8;
        
        // History for Charts
        this.historyPPM = new Array(MAX_DATA_POINTS).fill(0);
        this.historyTemp = new Array(MAX_DATA_POINTS).fill(0);
    }

    tick() {
        if (this.status === "RUNNING") {
            // Simulate random fluctuation
            const ppmNoise = (Math.random() - 0.5) * 5; 
            this.currentPPM = Math.floor(this.targetPPM + ppmNoise);
            if(this.currentPPM < 0) this.currentPPM = 0;

            const tempNoise = (Math.random() - 0.5) * 2;
            this.currentTemp = parseFloat((this.targetTemp + tempNoise).toFixed(1));

            // Increment batch
            this.batchCount += Math.floor(this.currentPPM / 60 * (REFRESH_RATE/1000) * 2); // rough approx
            
            // Randomly stop machine rarely
            if (Math.random() > 0.98) this.triggerEvent("STOPPED");
        } else if (this.status === "STOPPED") {
            this.currentPPM = 0;
            this.currentTemp = parseFloat((this.currentTemp * 0.99).toFixed(1)); // Cool down
            
            // Auto restart
            if (Math.random() > 0.8) this.triggerEvent("RUNNING");
        }

        // Shift history
        this.historyPPM.shift();
        this.historyPPM.push(this.currentPPM);
        
        this.historyTemp.shift();
        this.historyTemp.push(this.currentTemp);
    }

    triggerEvent(newStatus) {
        this.status = newStatus;
        const uiLog = document.getElementById("eventLog");
        const time = new Date().toLocaleTimeString();
        const div = document.createElement("div");
        div.className = "log-entry";
        
        let msg = "";
        let style = "log-info";
        
        if(newStatus === "STOPPED") {
            msg = "Operator Pause / Idle";
            style = "log-info";
        } else if (newStatus === "RUNNING") {
            msg = "Production Resumed";
            style = "log-info";
        } else {
            msg = "CRITICAL: Seal Integrity Check Failed";
            style = "log-err";
        }

        div.innerHTML = `<span class="log-time">${time}</span> <span class="${style}">${newStatus}: ${msg}</span>`;
        uiLog.prepend(div);
        
        // Clean old logs
        if(uiLog.children.length > 20) uiLog.lastChild.remove();
        
        updateStatusBadge(newStatus);
    }
}

// --- INSTANCES ---
const machines = {
    "ts-01": new MachineSimulator("ts-01", "TS-01: ProSeal GTR", 65, 180),
    "ts-02": new MachineSimulator("ts-02", "TS-02: Ishida QX", 45, 165),
    "ts-03": new MachineSimulator("ts-03", "TS-03: Multivac T800", 80, 190),
};

let activeMachine = machines["ts-01"];

// --- UI UPDATERS ---
const els = {
    name: document.getElementById("machineName"),
    status: document.getElementById("machineStatus"),
    ppm: document.getElementById("val-ppm"),
    temp: document.getElementById("val-temp"),
    batch: document.getElementById("val-batch"),
    dwell: document.getElementById("val-dwell"),
    bar: document.getElementById("batch-progress")
};

function updateStatusBadge(status) {
    els.status.className = "badge";
    els.status.innerText = status;
    if(status === "RUNNING") els.status.classList.add("running");
    else if(status === "STOPPED") els.status.classList.add("idle");
    else els.status.classList.add("stopped"); // red
}

function updateUI() {
    activeMachine.tick();

    els.ppm.innerText = activeMachine.currentPPM;
    els.temp.innerText = activeMachine.currentTemp;
    els.batch.innerText = activeMachine.batchCount.toLocaleString();
    els.dwell.innerText = activeMachine.status === "RUNNING" ? (0.8 + (Math.random()*0.1)).toFixed(2) : "0.0";
    
    // Fake Progress Bar (Reset at 5000)
    let progress = (activeMachine.batchCount % 5000) / 5000 * 100;
    els.bar.style.width = `${progress}%`;
}

// --- CHART RENDERER (Canvas) ---
function drawChart(canvasId, data, color, isFilled) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    // Resize logic
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = canvasId === 'chart-ppm' ? 60 : 120; // Explicit height logic

    const w = canvas.width;
    const h = canvas.height;
    const maxVal = Math.max(...data, 100); 
    const step = w / (data.length - 1);

    ctx.clearRect(0, 0, w, h);
    ctx.beginPath();
    
    data.forEach((val, i) => {
        const x = i * step;
        // Normalize to height (leave 10px padding top)
        const y = h - ((val / maxVal) * (h - 10)); 
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });

    ctx.lineWidth = 2;
    ctx.strokeStyle = color;
    ctx.stroke();

    if (isFilled) {
        ctx.lineTo(w, h);
        ctx.lineTo(0, h);
        ctx.fillStyle = color + "33"; // 20% opacity hex
        ctx.fill();
    }
}

function renderLoop() {
    // Draw PPM Small Chart
    drawChart("chart-ppm", activeMachine.historyPPM, "#3b82f6", false);
    
    // Draw Main Chart (PPM vs Time)
    drawChart("chart-main", activeMachine.historyPPM, "#22c55e", true);
    
    requestAnimationFrame(renderLoop);
}

// --- EVENTS ---
document.getElementById("machineSelect").addEventListener("change", (e) => {
    activeMachine = machines[e.target.value];
    els.name.innerText = activeMachine.name;
    updateStatusBadge(activeMachine.status);
    
    // Inject a "Switched" log
    const uiLog = document.getElementById("eventLog");
    uiLog.innerHTML += `<div class="log-entry"><span class="log-time">${new Date().toLocaleTimeString()}</span> <span class="log-info" style="color:yellow">System: View switched to ${activeMachine.id}</span></div>`;
});

// --- INIT ---
setInterval(updateUI, REFRESH_RATE);
renderLoop();