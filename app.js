const storageKey = "meterx-working-model";

const seed = {
  currentUserId: null,
  route: "login",
  theme: "dark",
  selectedConsumerId: "C10239",
  users: [
    { id: "C10239", name: "Anjali Nair", email: "consumer@meterx.com", password: "1234", role: "consumer" },
    { id: "A1001", name: "KSEB Admin", email: "admin@meterx.com", password: "admin", role: "admin" },
  ],
  readings: [
    { consumerId: "C10239", type: "first", value: 12840, timestamp: "2026-05-01 06:30 AM", confidence: 96.8, image: "filebase/may-first.jpg" },
    { consumerId: "C10239", type: "last", value: 13116, timestamp: "2026-05-31 08:15 AM", confidence: 98.4, image: "filebase/may-last.jpg" },
  ],
  bill: {
    consumerId: "C10239",
    month: "May 2026",
    gst: 42,
    fixedCharge: 120,
    additionalCharge: 35,
    status: "Pending",
    paymentReceipt: "",
    paymentStatus: "Pending",
    approved: false,
  },
  captures: [
    ["06:30 AM", "13112.5 kWh", "Sharp image", "ok"],
    ["08:15 AM", "13116.0 kWh", "Best OCR confidence", "ok"],
    ["11:45 AM", "13116.1 kWh", "Slight glare", "warn"],
    ["04:20 PM", "13116.0 kWh", "Accepted backup", "info"],
    ["09:10 PM", "Pending", "Waiting for upload", "warn"],
  ],
  usageHistory: [95, 182, 216, 168, 246, 276],
};

let state = null;
const tariffRate = 6.85;
const app = document.getElementById("app");
let chartInstances = [];

async function loadState() {
  // Try to load from backend first, fall back to localStorage
  try {
    const res = await fetch((window.__API_BASE__ || "") + '/api/state');
    if (res.ok) {
      const data = await res.json();
      return normalizeState(data);
    }
  } catch (e) {
    // ignore network errors and fall back
  }
  const saved = localStorage.getItem(storageKey);
  return normalizeState(saved ? JSON.parse(saved) : structuredClone(seed));
}

function normalizeState(data) {
  return {
    ...structuredClone(seed),
    ...data,
    bill: { ...structuredClone(seed).bill, ...(data.bill || {}) },
    captures: data.captures || structuredClone(seed).captures,
    readings: data.readings || structuredClone(seed).readings,
    users: data.users || structuredClone(seed).users,
    usageHistory: data.usageHistory || structuredClone(seed).usageHistory,
    theme: data.theme || "dark",
  };
}

function saveState() {
  // persist locally
  localStorage.setItem(storageKey, JSON.stringify(state));
  // try to persist to backend (best-effort)
  try {
    fetch((window.__API_BASE__ || "") + '/api/state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state),
    }).catch(() => {});
  } catch (e) {}
}

function resetDemo() {
  state = structuredClone(seed);
  saveState();
  render();
}

function currentUser() {
  return state.users.find((user) => user.id === state.currentUserId);
}

function selectedConsumer() {
  return state.users.find((user) => user.id === state.selectedConsumerId) || state.users.find((user) => user.role === "consumer");
}

function readingsFor(consumerId = selectedConsumer().id) {
  const first = state.readings.find((reading) => reading.consumerId === consumerId && reading.type === "first");
  const last = state.readings.find((reading) => reading.consumerId === consumerId && reading.type === "last");
  return { first, last };
}

function units(consumerId = selectedConsumer().id) {
  const { first, last } = readingsFor(consumerId);
  return Math.max(0, Number(last?.value || 0) - Number(first?.value || 0));
}

function billAmount() {
  return Math.round(units() * tariffRate + Number(state.bill.gst) + Number(state.bill.fixedCharge) + Number(state.bill.additionalCharge));
}

function currency(value) {
  return `Rs ${Number(value).toLocaleString("en-IN")}`;
}

function refreshIcons() {
  if (window.lucide) window.lucide.createIcons();
}

function navigate(route) {
  showLoading("Loading page...");
  setTimeout(() => {
    state.route = route;
    saveState();
    render();
  }, 280);
}

function toggleTheme() {
  state.theme = state.theme === "dark" ? "light" : "dark";
  saveState();
  render();
}

function login(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    email: form.get("email"),
    password: form.get("password"),
    role: form.get("role"),
  };

  const doLocalLogin = () => {
    const user = state.users.find(
      (item) => item.email === payload.email && item.password === payload.password && item.role === payload.role
    );
    if (!user) {
      showToast("Invalid login. Try consumer@meterx.com / 1234 or admin@meterx.com / admin.");
      return;
    }
    state.currentUserId = user.id;
    state.route = user.role === "admin" ? "admin-dashboard" : "consumer-dashboard";
    if (user.role === "consumer") state.selectedConsumerId = user.id;
    saveState();
    showLoading("Signing in...");
    setTimeout(render, 400);
  };

  fetch((window.__API_BASE__ || "") + "/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then(async (res) => {
      if (!res.ok) {
        throw new Error("Login failed");
      }
      const data = await res.json();
      window.localStorage.setItem("meterx_auth_token", data.access_token);
      return fetch((window.__API_BASE__ || "") + "/auth/me", {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
    })
    .then(async (res) => {
      if (!res.ok) {
        throw new Error("Unable to fetch user profile");
      }
      const user = await res.json();
      if (!state.users.find((item) => item.id === user.id)) {
        state.users.push({ id: user.id, name: user.name, email: user.email, role: user.role });
      }
      state.currentUserId = user.id;
      state.route = user.role === "admin" ? "admin-dashboard" : "consumer-dashboard";
      if (user.role === "consumer") state.selectedConsumerId = user.id;
      saveState();
      showLoading("Signing in...");
      setTimeout(render, 400);
    })
    .catch(() => {
      doLocalLogin();
    });
}

function register(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    name: form.get("name").trim(),
    email: form.get("email").trim(),
    password: form.get("password"),
    role: form.get("role"),
  };

  if (!payload.name || !payload.email || !payload.password) {
    showToast("Please fill all registration fields.");
    return;
  }

  fetch((window.__API_BASE__ || "") + "/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then(async (res) => {
      if (!res.ok) {
        throw new Error("Registration failed");
      }
      return res.json();
    })
    .then((user) => {
      if (!state.users.find((item) => item.id === user.id)) {
        state.users.push({ id: user.id, name: user.name, email: user.email, role: user.role });
      }
      state.currentUserId = user.id;
      state.route = user.role === "admin" ? "admin-dashboard" : "consumer-dashboard";
      if (user.role === "consumer") {
        state.selectedConsumerId = user.id;
      }
      saveState();
      showLoading("Creating account...");
      setTimeout(render, 450);
    })
    .catch(() => {
      const role = payload.role;
      const id = role === "admin" ? `A${Date.now().toString().slice(-4)}` : `C${Date.now().toString().slice(-5)}`;
      const user = {
        id,
        name: payload.name,
        email: payload.email,
        password: payload.password,
        role,
      };
      state.users.push(user);
      if (role === "consumer") {
        state.selectedConsumerId = id;
        state.readings.push(
          { consumerId: id, type: "first", value: 10000, timestamp: "2026-05-01 06:30 AM", confidence: 95.2, image: "filebase/first.jpg" },
          { consumerId: id, type: "last", value: 10145, timestamp: "2026-05-31 08:15 AM", confidence: 97.1, image: "filebase/last.jpg" }
        );
      }
      state.currentUserId = id;
      state.route = role === "admin" ? "admin-dashboard" : "consumer-dashboard";
      saveState();
      showLoading("Creating account...");
      setTimeout(render, 450);
    });
}

function logout() {
  state.currentUserId = null;
  state.route = "login";
  saveState();
  render();
}

function shell(title, content) {
  const user = currentUser();
  const isAdmin = user?.role === "admin";
  const nav = isAdmin
    ? [
        ["admin-dashboard", "Consumers", "users"],
        ["verify", "Verify OCR", "badge-check"],
        ["billing", "Bills", "receipt-text"],
        ["analytics", "Analytics", "bar-chart-3"],
      ]
    : [
        ["consumer-dashboard", "Dashboard", "layout-dashboard"],
        ["bills", "Bills", "receipt-text"],
        ["payment", "Payment", "upload"],
        ["prediction", "Prediction", "brain-circuit"],
      ];

  return `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark"><i data-lucide="gauge"></i></div>
          <div><h1>MeterX</h1><p>Smart KSEB Meter Billing</p></div>
        </div>
        <nav class="nav-list">
          ${nav.map(([route, label, icon]) => `<button class="nav-item ${state.route === route ? "active" : ""}" data-route="${route}"><i data-lucide="${icon}"></i>${label}</button>`).join("")}
        </nav>
        <div class="system-card">
          <div class="pulse"></div>
          <div><strong>ESP32-CAM Online</strong><span>5 captures daily via Wi-Fi</span></div>
        </div>
      </aside>
      <main class="main">
        <header class="topbar">
          <div><p class="eyebrow">${isAdmin ? "KSEB Admin Panel" : "Consumer Portal"}</p><h2>${title}</h2></div>
          <div class="top-actions">
            <button class="icon-btn" title="Notifications"><i data-lucide="bell"></i><span class="dot"></span></button>
            <button class="icon-btn" title="Theme" data-action="toggle-theme"><i data-lucide="${state.theme === "dark" ? "sun" : "moon"}"></i></button>
            <div class="profile"><span>${user.name}</span><small>${user.role}</small></div>
            <button class="secondary small" data-action="logout"><i data-lucide="log-out"></i> Logout</button>
          </div>
        </header>
        ${content}
      </main>
    </div>
  `;
}

function authView(mode = "login") {
  const isLogin = mode === "login";
  return `
    <main class="auth-page">
      <section class="phone-auth">
        <div class="brand center">
          <div class="brand-mark"><i data-lucide="gauge"></i></div>
          <div><h1>MeterX</h1><p>Smart Meter Billing</p></div>
        </div>
        <h2>${isLogin ? "Welcome Back" : "Create Account"}</h2>
        <form class="auth-form" id="${isLogin ? "loginForm" : "registerForm"}">
          ${isLogin ? "" : `<input name="name" placeholder="Full Name" autocomplete="name" />`}
          <input name="email" type="email" placeholder="Consumer ID / Email" autocomplete="email" />
          <input name="password" type="password" placeholder="Password" autocomplete="${isLogin ? "current-password" : "new-password"}" />
          <select name="role">
            <option value="consumer">Consumer</option>
            <option value="admin">KSEB Admin</option>
          </select>
          <button class="primary" type="submit"><i data-lucide="${isLogin ? "lock-keyhole" : "user-plus"}"></i>${isLogin ? "Log In" : "Register"}</button>
        </form>
        <button class="link-btn" data-route="${isLogin ? "register" : "login"}">${isLogin ? "New user? Register here" : "Already registered? Login"}</button>
        <button class="icon-btn auth-theme" title="Theme" data-action="toggle-theme"><i data-lucide="${state.theme === "dark" ? "sun" : "moon"}"></i></button>
      </section>
    </main>
  `;
}

function consumerDashboard() {
  const user = currentUser();
  const { last } = readingsFor(user.id);
  const alert = highUsageAlert();
  return shell(
    "Consumer Dashboard",
    `
      <div class="grid stats-grid">
        ${stat("Current Usage", `${units(user.id)} units`, "Current month consumption")}
        ${stat("Last Reading", `${Number(last.value).toLocaleString("en-IN")} kWh`, last.timestamp)}
        ${stat("Last Bill", currency(billAmount()), state.bill.paymentStatus)}
        ${stat("Next Month", "294 units", "Random Forest prediction")}
      </div>
      ${alert ? `<div class="usage-alert page-alert"><i data-lucide="triangle-alert"></i>${alert}</div>` : ""}
      <div class="grid two-col" style="margin-top:18px">
        <section class="panel">
          <div class="panel-header"><div><h3>Usage Overview</h3><p>Reading extracted from OCR and verified by KSEB.</p></div><span class="status ok">Bill generated</span></div>
          ${meterVisual(last.value)}
        </section>
        <section class="panel">
          <div class="panel-header">
            <div><h3>Scan KSEB Meter</h3><p>Take or upload a meter photo. The demo simulates OCR extraction and stores the reading.</p></div>
            <span class="status info">Camera ready</span>
          </div>
          <label class="scan-box" for="meterPhoto">
            <input id="meterPhoto" type="file" accept="image/*" capture="environment" />
            <div class="scan-preview" id="scanPreview"><i data-lucide="camera"></i><strong>Tap to scan meter</strong><span>Use phone camera or upload image</span></div>
          </label>
          <div class="form-grid" style="margin-top:14px">
            <div class="field"><label>Extracted Reading</label><input id="scanReading" type="number" value="${last.value}" /></div>
            <div class="field"><label>OCR Confidence</label><input id="scanConfidence" readonly value="98.4%" /></div>
            <div class="field"><label>Timestamp</label><input readonly value="${new Date().toLocaleString("en-IN")}" /></div>
          </div>
          <div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap">
            <button class="primary" data-action="simulate-ocr"><i data-lucide="scan-text"></i> Extract Reading</button>
            <button class="secondary" data-action="save-scan"><i data-lucide="save"></i> Save Reading</button>
          </div>
        </section>
      </div>
      <div class="grid two-col" style="margin-top:18px">
        <section class="panel">
          <div class="panel-header"><div><h3>Notifications</h3><p>Bill generated, payment reminders, and high usage alerts.</p></div></div>
          ${timeline("Verification completed", "Admin approved monthly meter readings.")}
          ${timeline("Bill generated", `${state.bill.month} bill is ready to download.`)}
          ${timeline("High usage alert", "Usage is up by 12% compared to last month.")}
        </section>
        <section class="panel">
          <div class="panel-header"><div><h3>Monthly Consumption Graph</h3><p>Live Chart.js view of recent consumption trend.</p></div></div>
          <div class="chart-card"><canvas id="dashboardChart" height="130"></canvas></div>
        </section>
      </div>
    `
  );
}

function billsView() {
  return shell(
    "Bills",
    `
      <section class="panel">
        <div class="panel-header"><div><h3>Monthly Bill PDF Preview</h3><p>PDF structure for your KSEB bill output.</p></div><button class="primary" data-action="download-bill"><i data-lucide="download"></i> Download PDF</button></div>
        ${billRows()}
        <div class="bill-total"><span>Total Amount</span><strong>${currency(billAmount())}</strong></div>
      </section>
    `
  );
}

function paymentView() {
  return shell(
    "Payment & Receipt Upload",
    `
      <section class="panel">
        <div class="panel-header"><div><h3>Manual Payment Status</h3><p>Upload receipt after paying the electricity bill.</p></div><span class="status ${state.bill.paymentStatus === "Verified" ? "ok" : "warn"}">${state.bill.paymentStatus}</span></div>
        <div class="form-grid">
          <div class="field"><label>Receipt Image/PDF</label><input id="receiptInput" type="file" /></div>
          <div class="field"><label>Uploaded Receipt</label><input readonly value="${state.bill.paymentReceipt || "No receipt uploaded"}" /></div>
          <div class="field"><label>Bill Amount</label><input readonly value="${currency(billAmount())}" /></div>
        </div>
        <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
          <button class="primary" data-action="upload-receipt"><i data-lucide="upload"></i> Save Receipt</button>
          <button class="secondary" data-action="mark-paid"><i data-lucide="check-circle-2"></i> Mark Paid</button>
        </div>
      </section>
    `
  );
}

function predictionView() {
  const alert = highUsageAlert();
  return shell(
    "Prediction",
    `
      <div class="grid three-col">
        ${stat("Predicted Usage", "294 units", "Random Forest Regression")}
        ${stat("Estimated Bill", currency(2211), "Based on projected usage")}
        ${stat("Confidence", "91%", "Historical + seasonal data")}
      </div>
      ${alert ? `<div class="usage-alert page-alert"><i data-lucide="triangle-alert"></i>${alert}</div>` : ""}
      ${analyticsPanel()}
    `
  );
}

function adminDashboard() {
  const consumers = state.users.filter((user) => user.role === "consumer");
  return shell(
    "All Consumers",
    `
      <div class="grid stats-grid">
        ${stat("Consumers", consumers.length, "Registered consumer accounts")}
        ${stat("Pending Verification", state.bill.approved ? 0 : 1, "Monthly readings")}
        ${stat("Bills Generated", state.bill.status === "Generated" ? 1 : 0, "Current cycle")}
        ${stat("Payment Status", state.bill.paymentStatus, "Receipt verification")}
      </div>
      <section class="panel" style="margin-top:18px">
        <div class="panel-header"><div><h3>Consumer List</h3><p>Select a consumer for verification and billing review.</p></div><button class="secondary" data-route="register"><i data-lucide="user-plus"></i> Add User</button></div>
        <div class="consumer-list">
          ${consumers.map((user) => consumerRow(user)).join("")}
        </div>
      </section>
    `
  );
}

function consumerRow(user) {
  return `
    <button class="consumer-row ${state.selectedConsumerId === user.id ? "selected" : ""}" data-consumer="${user.id}">
      <span><strong>${user.name}</strong><small>${user.id} | ${user.email}</small></span>
      <span class="status info">${units(user.id)} units</span>
    </button>
  `;
}

function verifyView() {
  const consumer = selectedConsumer();
  const { first, last } = readingsFor(consumer.id);
  return shell(
    "Admin Verification Dashboard",
    `
      <section class="panel">
        <div class="panel-header"><div><h3>${consumer.name}</h3><p>Verify OCR values before bill generation.</p></div><span class="status ${state.bill.approved ? "ok" : "info"}">${state.bill.approved ? "Approved" : "Awaiting approval"}</span></div>
        <div class="proof-grid">
          ${proof("First Day Reading Image", first.timestamp, first.value, first.confidence)}
          ${proof("Last Day Reading Image", last.timestamp, last.value, last.confidence)}
        </div>
        <div class="form-grid" style="margin-top:18px">
          <div class="field"><label>First Reading</label><input id="firstReading" type="number" value="${first.value}" /></div>
          <div class="field"><label>Last Reading</label><input id="lastReading" type="number" value="${last.value}" /></div>
          <div class="field"><label>Units Consumed</label><input readonly value="${units(consumer.id)} units" /></div>
        </div>
        <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
          <button class="primary" data-action="approve-readings"><i data-lucide="badge-check"></i> Approve Readings</button>
          <button class="secondary" data-action="save-readings"><i data-lucide="pencil"></i> Modify Reading</button>
        </div>
      </section>
    `
  );
}

function billingView() {
  return shell(
    "Billing Module",
    `
      <section class="panel">
        <div class="panel-header"><div><h3>Generate Monthly Bill</h3><p>Total = Energy Charge + GST + Fixed Charges + Additional Charges.</p></div><button class="primary" data-action="generate-bill"><i data-lucide="file-text"></i> Generate Bill</button></div>
        <div class="form-grid">
          <div class="field"><label>GST</label><input id="gst" type="number" value="${state.bill.gst}" /></div>
          <div class="field"><label>Fixed Charges</label><input id="fixedCharge" type="number" value="${state.bill.fixedCharge}" /></div>
          <div class="field"><label>Additional Charges</label><input id="additionalCharge" type="number" value="${state.bill.additionalCharge}" /></div>
        </div>
        <div style="margin-top:18px">${billRows()}</div>
        <div class="bill-total"><span>Final Bill PDF Amount</span><strong>${currency(billAmount())}</strong></div>
      </section>
    `
  );
}

function analyticsView() {
  return shell("Usage Analytics", analyticsPanel());
}

function analyticsPanel() {
  const alert = highUsageAlert();
  return `
    <section class="panel" style="margin-top:18px">
      <div class="panel-header"><div><h3>Usage Analytics</h3><p>Monthly consumption graph powered by Chart.js.</p></div><span class="status warn">${usageChange()}% Up</span></div>
      <div class="usage-chart">
        <canvas id="usageChart" height="120"></canvas>
        ${alert ? `<div class="usage-alert"><i data-lucide="triangle-alert"></i>${alert}</div>` : ""}
      </div>
    </section>
  `;
}

function stat(label, value, note) {
  return `<article class="stat-card"><span>${label}</span><strong>${value}</strong><small>${note}</small></article>`;
}

function meterVisual(reading) {
  return `<div class="meter-visual"><div class="meter-box"><strong>KSEB Digital Meter</strong><div class="meter-window">${Number(reading).toFixed(1)}</div><div class="meter-meta"><span>kWh</span><span>OCR confidence 98.4%</span></div></div></div>`;
}

function billRows() {
  const consumer = selectedConsumer();
  const { first, last } = readingsFor(consumer.id);
  const energy = Math.round(units(consumer.id) * tariffRate);
  return `
    <div class="bill-row"><span>Consumer Name</span><strong>${consumer.name}</strong></div>
    <div class="bill-row"><span>Consumer ID</span><strong>${consumer.id}</strong></div>
    <div class="bill-row"><span>Billing Month</span><strong>${state.bill.month}</strong></div>
    <div class="bill-row"><span>First Reading</span><strong>${Number(first.value).toLocaleString("en-IN")} kWh</strong></div>
    <div class="bill-row"><span>Last Reading</span><strong>${Number(last.value).toLocaleString("en-IN")} kWh</strong></div>
    <div class="bill-row"><span>Units Consumed</span><strong>${units(consumer.id)} units</strong></div>
    <div class="bill-row"><span>Energy Charge</span><strong>${currency(energy)}</strong></div>
    <div class="bill-row"><span>GST + Fixed + Additional</span><strong>${currency(Number(state.bill.gst) + Number(state.bill.fixedCharge) + Number(state.bill.additionalCharge))}</strong></div>
    <div class="bill-row"><span>Payment Status</span><strong>${state.bill.paymentStatus}</strong></div>
  `;
}

function proof(title, timestamp, reading, confidence) {
  return `<article class="proof"><div class="proof-image"><i data-lucide="image"></i></div><div class="proof-body"><strong>${title}</strong><span>${timestamp} | ${Number(reading).toFixed(1)} kWh | ${confidence}% confidence</span></div></article>`;
}

function usageBar(label, height, highlight = false) {
  return `<div class="bar ${highlight ? "highlight" : ""}"><div class="bar-fill" style="height:${height}%"></div><span>${label}</span></div>`;
}

function timeline(title, text) {
  return `<div class="timeline-item"><div class="timeline-dot"></div><div><strong>${title}</strong><p>${text}</p></div></div>`;
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2800);
}

function showLoading(message) {
  document.querySelector(".loading-overlay")?.remove();
  const overlay = document.createElement("div");
  overlay.className = "loading-overlay";
  overlay.innerHTML = `<div class="loader"></div><strong>${message}</strong>`;
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 750);
}

function usageChange() {
  const history = state.usageHistory;
  const previous = history[history.length - 2] || 1;
  const activeId = currentUser()?.role === "consumer" ? currentUser().id : selectedConsumer().id;
  const current = units(activeId) || history[history.length - 1];
  return Math.round(((current - previous) / previous) * 100);
}

function highUsageAlert() {
  const change = usageChange();
  return change >= 12 ? `High Usage Alert: usage is up by ${change}% compared to last month.` : "";
}

function bindEvents() {
  document.querySelectorAll("[data-route]").forEach((item) => item.addEventListener("click", () => navigate(item.dataset.route)));
  document.querySelectorAll("[data-consumer]").forEach((item) =>
    item.addEventListener("click", () => {
      state.selectedConsumerId = item.dataset.consumer;
      saveState();
      navigate("verify");
    })
  );

  document.getElementById("loginForm")?.addEventListener("submit", login);
  document.getElementById("registerForm")?.addEventListener("submit", register);

  document.querySelectorAll("[data-action='toggle-theme']").forEach((button) => button.addEventListener("click", toggleTheme));
  document.querySelector("[data-action='logout']")?.addEventListener("click", logout);
  document.querySelector("[data-action='approve-readings']")?.addEventListener("click", () => {
    state.bill.approved = true;
    saveState();
    showToast("Readings approved.");
    render();
  });
  document.querySelector("[data-action='save-readings']")?.addEventListener("click", saveReadings);
  document.querySelector("[data-action='generate-bill']")?.addEventListener("click", () => {
    saveCharges();
    state.bill.status = "Generated";
    showToast("Monthly bill generated.");
    saveState();
    render();
  });
  document.querySelector("[data-action='upload-receipt']")?.addEventListener("click", uploadReceipt);
  document.querySelector("[data-action='mark-paid']")?.addEventListener("click", () => {
    state.bill.paymentStatus = "Verified";
    saveState();
    showToast("Payment marked as verified.");
    render();
  });
  document.getElementById("meterPhoto")?.addEventListener("change", previewMeterPhoto);
  document.querySelector("[data-action='simulate-ocr']")?.addEventListener("click", simulateOcr);
  document.querySelector("[data-action='save-scan']")?.addEventListener("click", saveScanReading);
  document.querySelector("[data-action='download-bill']")?.addEventListener("click", downloadBillPdf);

  ["gst", "fixedCharge", "additionalCharge"].forEach((id) => document.getElementById(id)?.addEventListener("input", saveCharges));
}

function saveReadings() {
  const { first, last } = readingsFor();
  first.value = Number(document.getElementById("firstReading").value);
  last.value = Number(document.getElementById("lastReading").value);
  saveState();
  showToast("OCR readings updated.");
  render();
}

function saveCharges() {
  ["gst", "fixedCharge", "additionalCharge"].forEach((id) => {
    const input = document.getElementById(id);
    if (input) state.bill[id] = Number(input.value);
  });
  saveState();
}

function uploadReceipt() {
  const file = document.getElementById("receiptInput")?.files?.[0];
  if (!file) {
    showToast("Choose a receipt file first.");
    return;
  }
  state.bill.paymentReceipt = file.name;
  state.bill.paymentStatus = "Pending Verification";
  saveState();
  showToast("Receipt uploaded for admin verification.");
  render();
}

function previewMeterPhoto(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const preview = document.getElementById("scanPreview");
  const reader = new FileReader();
  reader.onload = () => {
    preview.classList.add("has-image");
    preview.innerHTML = `<img src="${reader.result}" alt="Uploaded meter reading" /><span>${file.name}</span><div class="scan-line"></div>`;
    refreshIcons();
  };
  reader.readAsDataURL(file);
}

function simulateOcr() {
  const input = document.getElementById("scanReading");
  const confidence = document.getElementById("scanConfidence");
  const current = Number(input.value || readingsFor(currentUser().id).last.value);
  const preview = document.getElementById("scanPreview");
  preview?.classList.add("scanning");
  showLoading("Running OCR scan...");
  setTimeout(() => {
    input.value = (current + Math.round(Math.random() * 8 + 2)).toFixed(1);
    if (confidence) confidence.value = `${(96 + Math.random() * 3).toFixed(1)}%`;
    preview?.classList.remove("scanning");
    showToast("OCR extraction completed.");
  }, 1100);
}

function saveScanReading() {
  const user = currentUser();
  const { last } = readingsFor(user.id);
  const value = Number(document.getElementById("scanReading")?.value);
  if (!value) {
    showToast("Enter or extract a valid meter reading.");
    return;
  }
  last.value = value;
  last.timestamp = new Date().toLocaleString("en-IN");
  last.confidence = 98.4;
  state.bill.approved = false;
  state.bill.status = "Pending Verification";
  saveState();
  showToast("Meter photo reading saved for admin verification.");
  render();
}

function downloadBillPdf() {
  const jsPdf = window.jspdf?.jsPDF;
  if (!jsPdf) {
    showToast("PDF library not loaded. Opening print dialog instead.");
    window.print();
    return;
  }

  const consumer = selectedConsumer();
  const { first, last } = readingsFor(consumer.id);
  const energy = Math.round(units(consumer.id) * tariffRate);
  const doc = new jsPdf();
  doc.setFont("helvetica", "bold");
  doc.setFontSize(20);
  doc.text("KSEB MeterX Monthly Bill", 20, 22);
  doc.setFontSize(11);
  doc.setFont("helvetica", "normal");

  const rows = [
    ["Consumer Name", consumer.name],
    ["Consumer ID", consumer.id],
    ["Billing Month", state.bill.month],
    ["First Reading", `${first.value} kWh`],
    ["Last Reading", `${last.value} kWh`],
    ["Units Consumed", `${units(consumer.id)} units`],
    ["Energy Charge", currency(energy)],
    ["GST", currency(state.bill.gst)],
    ["Fixed Charges", currency(state.bill.fixedCharge)],
    ["Additional Charges", currency(state.bill.additionalCharge)],
    ["Total Amount", currency(billAmount())],
    ["Payment Status", state.bill.paymentStatus],
  ];

  rows.forEach(([label, value], index) => {
    const y = 42 + index * 11;
    doc.setFont("helvetica", "bold");
    doc.text(label, 20, y);
    doc.setFont("helvetica", "normal");
    doc.text(String(value), 85, y);
  });

  doc.save(`MeterX-${consumer.id}-${state.bill.month.replace(" ", "-")}.pdf`);
  showToast("Bill PDF downloaded.");
}

function renderCharts() {
  chartInstances.forEach((chart) => chart.destroy());
  chartInstances = [];
  const usageCanvas = document.getElementById("usageChart");
  const dashboardCanvas = document.getElementById("dashboardChart");
  if (!window.Chart) return;

  const css = getComputedStyle(document.body);
  const activeId = currentUser()?.role === "consumer" ? currentUser().id : selectedConsumer().id;
  const labels = ["Jul", "Aug", "Oct", "Nov", "Dec", "Jan"];
  const data = state.usageHistory.slice(0, 5).concat([units(activeId)]);
  const sharedOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color: css.getPropertyValue("--muted") }, grid: { color: "rgba(120,150,170,.12)" } },
      y: { ticks: { color: css.getPropertyValue("--muted") }, grid: { color: "rgba(120,150,170,.12)" } },
    },
    animation: { duration: 850, easing: "easeOutQuart" },
  };

  if (usageCanvas) {
    chartInstances.push(new Chart(usageCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Units",
            data,
            backgroundColor: ["rgba(34,230,214,.45)", "rgba(34,230,214,.35)", "rgba(34,230,214,.42)", "rgba(34,230,214,.32)", "rgba(34,230,214,.48)", "#22e6f0"],
            borderRadius: 8,
          },
        ],
      },
      options: sharedOptions,
    }));
  }

  if (dashboardCanvas) {
    chartInstances.push(new Chart(dashboardCanvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            data,
            borderColor: "#22e6f0",
            backgroundColor: "rgba(34,230,240,.14)",
            pointBackgroundColor: "#22e6f0",
            fill: true,
            tension: 0.35,
          },
        ],
      },
      options: sharedOptions,
    }));
  }
}

function render() {
  const user = currentUser();
  const publicRoutes = {
    login: () => authView("login"),
    register: () => authView("register"),
  };
  const privateRoutes = {
    "consumer-dashboard": consumerDashboard,
    bills: billsView,
    payment: paymentView,
    prediction: predictionView,
    "admin-dashboard": adminDashboard,
    verify: verifyView,
    billing: billingView,
    analytics: analyticsView,
  };

  if (!user && !publicRoutes[state.route]) state.route = "login";
  if (user?.role === "admin" && state.route === "architecture") state.route = "admin-dashboard";
  document.body.dataset.theme = state.theme;
  app.classList.remove("page-enter");
  app.innerHTML = publicRoutes[state.route]?.() || privateRoutes[state.route]?.() || authView("login");
  requestAnimationFrame(() => app.classList.add("page-enter"));
  bindEvents();
  refreshIcons();
  renderCharts();
}

window.resetMeterXDemo = resetDemo;
// initialize app: load state (from backend or local) then render
(async function init() {
  state = await loadState();
  render();
})();
