const API = "http://127.0.0.1:8000/api";
let lastEstimateTotal = null;
let lastPayload = null;
let dialogCompanyIds = [];
const selectedIds = new Set();
const companyById = {};

const $ = (id) => document.getElementById(id);
const inr = (n) => "₹" + Number(n).toLocaleString("en-IN");

// ---------- 1. Estimator ----------
$("estimate-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("estimate-error").hidden = true;

    const payload = {
    plot_size: Number($("plot_size").value),
    floors: Number($("floors").value),
    finish_level: $("finish_level").value,
  };

  lastPayload = payload;
  
  try {
    const res = await fetch(`${API}/estimate/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");

    lastEstimateTotal = data.total;
    $("range").textContent = `${inr(data.low)} – ${inr(data.high)}`;
    $("area").textContent = `Estimated built-up area: ${data.built_up_area} sq ft`;

    const tbody = $("items");
    tbody.innerHTML = "";
    data.items.forEach((row) => {
      const tr = document.createElement("tr");
      [row.item, inr(row.rate), inr(row.cost)].forEach((text) => {
        const td = document.createElement("td");
        td.textContent = text;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    $("result").hidden = false;
  } catch (err) {
    $("estimate-error").textContent = err.message;
    $("estimate-error").hidden = false;
  }
});

// ---------- 2. Companies ----------
function updateSelectionBar() {
  const n = selectedIds.size;
  $("selection-bar").hidden = n === 0;
  $("sel-count").textContent = `${n} selected`;
}

async function loadCompanies() {
  const city = $("city").value.trim();
  const url = `${API}/companies/` + (city ? `?city=${encodeURIComponent(city)}` : "");
  const box = $("companies");
  box.textContent = "Loading...";

  try {
    const res = await fetch(url);
    const list = await res.json();
    box.innerHTML = "";
    if (list.length === 0) { box.textContent = "No verified companies found."; return; }

    list.forEach((c) => {
      companyById[c.id] = c;
      const div = document.createElement("div");
      div.className = "company";

      const check = document.createElement("input");
      check.type = "checkbox";
      check.className = "pick";
      check.checked = selectedIds.has(c.id);
      check.addEventListener("change", () => {
        check.checked ? selectedIds.add(c.id) : selectedIds.delete(c.id);
        updateSelectionBar();
      });

      const info = document.createElement("div");
      info.style.flex = "1";
      const h4 = document.createElement("h4");
      h4.textContent = c.name;
      const p1 = document.createElement("p");
      p1.className = "muted";
      p1.textContent = `${c.city} · ⭐ ${c.rating} · ${c.years_experience} yrs · ${c.projects_completed} projects`;
      const p2 = document.createElement("p");
      p2.textContent = c.description;
      info.append(h4, p1, p2);

      const btn = document.createElement("button");
      btn.textContent = "Request quote";
      btn.addEventListener("click", () => openQuote([c.id]));

      div.append(check, info, btn);
      box.appendChild(div);
    });
  } catch (err) {
    box.textContent = "Could not load companies. Is the backend running?";
  }
}

$("search-btn").addEventListener("click", loadCompanies);
$("city").addEventListener("keydown", (e) => { if (e.key === "Enter") loadCompanies(); });
$("sel-request").addEventListener("click", () => openQuote([...selectedIds]));
loadCompanies();

// ---------- 3. Quote request (one or many companies) ----------
function openQuote(ids) {
  dialogCompanyIds = ids;
  const names = ids.map((id) => companyById[id] && companyById[id].name).filter(Boolean);
  $("quote-title").textContent = ids.length === 1
    ? `Request a quote from ${names[0]}`
    : `Request quotes from ${ids.length} companies`;
  $("quote-msg").textContent = "";
  $("quote-dialog").showModal();
}

$("q_cancel").addEventListener("click", () => $("quote-dialog").close());

$("quote-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const phone = $("q_phone").value.trim();
  const payload = {
    companies: dialogCompanyIds,
    customer_name: $("q_name").value,
    customer_phone: phone,
    customer_email: $("q_email").value,
    message: $("q_message").value,
    estimated_cost: lastEstimateTotal,
  };

  try {
    const res = await fetch(`${API}/quote-requests/bulk/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error("Please check your details and try again.");

    try {
      localStorage.setItem("last_ref", data.reference);
      localStorage.setItem("last_phone", phone);
    } catch (_) {}

    $("quote-msg").textContent =
      `Sent to ${data.count} company(ies). Your reference code: ${data.reference}. ` +
      `Save it, then open "Compare your quotes" with this code and your phone number.`;
    $("quote-form").reset();
    selectedIds.clear();
    updateSelectionBar();
    document.querySelectorAll(".pick").forEach((c) => (c.checked = false));
  } catch (err) {
    $("quote-msg").textContent = err.message;
  }
});

// ---------- PDF report ----------
$("pdf-btn").addEventListener("click", async () => {
  if (!lastPayload) return;
  try {
    const res = await fetch(`${API}/estimate/pdf/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastPayload),
    });
    if (!res.ok) throw new Error("Could not create the PDF.");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "construction-estimate.pdf";
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    $("estimate-error").textContent = err.message;
    $("estimate-error").hidden = false;
  }
});