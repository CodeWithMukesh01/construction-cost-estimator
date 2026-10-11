// After deployment, change this to your live backend URL, e.g. "https://YOUR-NAME.onrender.com/api"
const ADMIN_API = "http://127.0.0.1:8000/api";

const $ = (id) => document.getElementById(id);
const inr = (n) => (n == null ? "–" : "₹" + Math.round(n).toLocaleString("en-IN"));
const show = (v, suffix = "") => (v == null ? "–" : v + suffix);
let charts = [];

function getToken() { try { return localStorage.getItem("admin_token"); } catch (_) { return null; } }
function setToken(t) { try { t ? localStorage.setItem("admin_token", t) : localStorage.removeItem("admin_token"); } catch (_) {} }

function logout() {
  setToken(null);
  $("dash").hidden = true;
  $("login-card").hidden = false;
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("login-msg").textContent = "";
  try {
    const res = await fetch(`${ADMIN_API}/staff/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: $("a_user").value.trim(), password: $("a_pass").value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Invalid username or password.");
    setToken(data.token);
    $("who").textContent = "Signed in as " + data.username;
    $("login-form").reset();
    load();
  } catch (err) {
    $("login-msg").textContent = err.message;
  }
});

$("logout").addEventListener("click", logout);
$("refresh").addEventListener("click", load);

function kpi(label, value, sub) {
  const div = document.createElement("div");
  div.className = "kpi";
  const v = document.createElement("div");
  v.className = "kpi-value";
  v.textContent = value;
  const l = document.createElement("div");
  l.className = "kpi-label";
  l.textContent = label;
  div.append(v, l);
  if (sub) {
    const s = document.createElement("div");
    s.className = "kpi-sub";
    s.textContent = sub;
    div.appendChild(s);
  }
  return div;
}

function drawChart(canvasId, config) {
  const c = new Chart($(canvasId), config);
  charts.push(c);
}

function render(d) {
  $("login-card").hidden = true;
  $("dash").hidden = false;

  const k = $("kpis");
  k.innerHTML = "";
  k.append(
    kpi("Estimates generated", d.estimates_total, `${d.estimates_7d} in the last 7 days`),
    kpi("Quote requests", d.requests_total, `${d.requests_7d} in the last 7 days · ${d.projects} projects`),
    kpi("Verified companies", d.companies_verified, `${d.companies_pending} pending verification`),
    kpi("Quote response rate", show(d.response_rate, "%"), `${d.quotes_received} quotes received`),
    kpi("Avg quotes per project", show(d.avg_quotes_per_project)),
    kpi("Estimate → request", show(d.estimate_to_request_rate, "%"), "projects ÷ estimates"),
    kpi("Quote vs estimate", d.avg_gap_pct == null ? "–" : (d.avg_gap_pct > 0 ? "+" : "") + d.avg_gap_pct + "%",
        "average gap, final quote vs estimate"),
    kpi("Average estimate", inr(d.avg_estimate)),
  );

  charts.forEach((c) => c.destroy());
  charts = [];

  drawChart("weekly-chart", {
    type: "bar",
    data: {
      labels: d.weekly.map((w) =>
        new Date(w.week + "T00:00:00").toLocaleDateString("en-IN", { day: "2-digit", month: "short" })),
      datasets: [{ label: "Estimates", data: d.weekly.map((w) => w.count), backgroundColor: "#c2410c" }],
    },
    options: {
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });

  drawChart("finish-chart", {
    type: "bar",
    data: {
      labels: d.by_finish.map((f) => f.level[0].toUpperCase() + f.level.slice(1)),
      datasets: [{ label: "Estimates", data: d.by_finish.map((f) => f.count), backgroundColor: "#1f2a33" }],
    },
    options: {
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  });

  const body = $("top-body");
  body.innerHTML = "";
  if (d.top_companies.length === 0) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = "No quote requests yet.";
    tr.appendChild(td);
    body.appendChild(tr);
  }
  d.top_companies.forEach((c) => {
    const tr = document.createElement("tr");
    [c.name, c.city, c.received, c.answered].forEach((val, i) => {
      const td = document.createElement("td");
      td.textContent = val;
      if (i < 2) td.style.textAlign = "left";
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });
}

async function load() {
  try {
    const res = await fetch(`${ADMIN_API}/staff/analytics/`, {
      headers: { Authorization: `Token ${getToken()}` },
    });
    if (res.status === 401 || res.status === 403) { logout(); return; }
    render(await res.json());
  } catch (err) {
    $("login-msg").textContent = "Could not reach the backend. Is Django running?";
  }
}

if (getToken()) load();