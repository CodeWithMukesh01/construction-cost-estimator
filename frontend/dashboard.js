const API_URL = "https://construction-cost-estimator-1.onrender.com";
const API = `${API_URL}/api`;
const $ = (id) => document.getElementById(id);
const inr = (n) => (n == null ? "–" : "₹" + Number(n).toLocaleString("en-IN"));

function token() { return localStorage.getItem("token"); }

function showDashboard() {
  $("login-card").hidden = true;
  $("dash-card").hidden = false;
  $("welcome").textContent = "Welcome, " + (localStorage.getItem("company") || "");
  $("verify-note").textContent = localStorage.getItem("verified") === "true"
    ? "Your company is verified and listed."
    : "Your company is awaiting admin verification. You will be listed once approved.";
  loadRequests();
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("login-msg").textContent = "";
  try {
    const res = await fetch(`${API}/company/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: $("l_user").value.trim(), password: $("l_pass").value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Invalid username or password.");
    localStorage.setItem("token", data.token);
    localStorage.setItem("company", data.company);
    localStorage.setItem("verified", data.is_verified);
    showDashboard();
  } catch (err) {
    $("login-msg").textContent = err.message;
  }
});

$("logout").addEventListener("click", () => {
  localStorage.clear();
  location.reload();
});

function makeRequestCard(r) {
  const div = document.createElement("div");
  div.className = "company request-card";

  const info = document.createElement("div");
  info.style.flex = "1";
  const h4 = document.createElement("h4");
  h4.textContent = r.customer_name + " · " + r.customer_phone;
  const p1 = document.createElement("p");
  p1.className = "muted";
  p1.textContent = "Customer estimate: " + inr(r.estimated_cost) + " · " +
    new Date(r.created_at).toLocaleString("en-IN");
  const p2 = document.createElement("p");
  p2.textContent = r.message || "(no message)";

  // quote form
  const form = document.createElement("form");
  form.className = "quote-inline";
  const amount = document.createElement("input");
  amount.type = "number"; amount.min = "1"; amount.required = true;
  amount.placeholder = "Your quote (₹)";
  amount.value = r.company_quote || "";
  const note = document.createElement("input");
  note.type = "text"; note.placeholder = "Note (timeline, what's included)";
  note.value = r.company_note || "";
  const btn = document.createElement("button");
  btn.type = "submit";
  btn.textContent = r.company_quote ? "Update quote" : "Send quote";
  const msg = document.createElement("span");
  msg.className = "muted";

  form.append(amount, note, btn, msg);
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    msg.textContent = "Saving...";
    try {
      const res = await fetch(`${API}/company/requests/${r.id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Token ${token()}` },
        body: JSON.stringify({ company_quote: Number(amount.value), company_note: note.value }),
      });
      if (!res.ok) throw new Error("Could not save. Check the amount.");
      msg.textContent = "Saved ✔";
      btn.textContent = "Update quote";
    } catch (err) {
      msg.textContent = err.message;
    }
  });

  info.append(h4, p1, p2, form);
  div.append(info);
  return div;
}

async function loadRequests() {
  const box = $("requests");
  box.textContent = "Loading...";
  const res = await fetch(`${API}/company/requests/`, {
    headers: { Authorization: `Token ${token()}` },
  });
  if (res.status === 401) { localStorage.clear(); location.reload(); return; }
  const list = await res.json();
  box.innerHTML = "";
  if (list.length === 0) { box.textContent = "No quote requests yet."; return; }
  list.forEach((r) => box.appendChild(makeRequestCard(r)));
}

if (token()) showDashboard();