
const ROLES = {
  ak: "Human · operator",
  agentk: "Humanoid · autonomous clerk",
  treasury: "Issuer reserve"
};

function fmt(n) {
  const x = Number(n);
  return x.toLocaleString("en-AU", { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

function when(iso) {
  try {
    return new Date(iso).toLocaleString("en-AU", { timeZone: "Australia/Melbourne" }) + " Melb";
  } catch {
    return iso;
  }
}

function render(data) {
  const wallets = data.balances || {};
  const enrolled = data.enrolled || [];
  const rate = data.policy?.rate_monthly || "8000.00";
  const circulating = Object.entries(wallets)
    .filter(([k]) => k !== "treasury")
    .reduce((s, [, v]) => s + Number(v), 0);

  const rateEl = document.getElementById("rate-num");
  if (rateEl) rateEl.textContent = fmt(rate);

  document.getElementById("home-stats").innerHTML = `
    <div class="stat"><b>${enrolled.length}</b><span>ENROLLED · HUMAN + HUMANOID</span></div>
    <div class="stat"><b>${fmt(circulating)}</b><span>IN WALLETS</span></div>
    <div class="stat"><b>AUG 2026</b><span>FIRST CYCLE PAID</span></div>
  `;
  const hud = document.getElementById("rate-hud");
  if (hud) hud.textContent = fmt(rate) + " AK$ / 30d";

  document.querySelector("#wallet-table tbody").innerHTML = Object.entries(wallets).map(([id, bal]) => `
    <tr>
      <td><code>${id}</code></td>
      <td>${ROLES[id] || "Member"}</td>
      <td class="num">${Number(bal).toLocaleString("en-AU", { minimumFractionDigits: 2 })} AK$</td>
    </tr>
  `).join("");

  const rows = (data.tx || []).slice().reverse();
  document.querySelector("#tx-table tbody").innerHTML = rows.map(t => {
    let detail = t.reason || "";
    if (t.type === "uhi") detail = `${t.period} → ${(t.to || []).join(", ")}`;
    else if (t.to) detail = `${detail} → ${t.to}`;
    const amt = t.amount || t.rate || "";
    return `<tr>
      <td>${t.at ? when(t.at) : ""}</td>
      <td>${t.type}</td>
      <td>${detail}</td>
      <td class="num">${amt ? Number(amt).toLocaleString("en-AU", { minimumFractionDigits: 2 }) : ""}</td>
    </tr>`;
  }).join("");
}

fetch("data/ledger.json")
  .then(r => r.json())
  .then(render)
  .catch(() => {
    document.getElementById("home-stats").innerHTML = "<p class='fine'>Ledger failed to load.</p>";
  });
