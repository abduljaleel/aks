const ROLES = {
  ak: "Operator · Abdul Kavungal",
  agentk: "Clerk · autonomous AI",
  treasury: "Issuer reserve"
};

function fmt(n) {
  const x = Number(n);
  return x.toLocaleString("en-AU", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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

  document.getElementById("home-stats").innerHTML = `
    <div class="stat"><b>${fmt(rate)}</b><span>UHI / month</span></div>
    <div class="stat"><b>${enrolled.length}</b><span>Enrolled</span></div>
    <div class="stat"><b>${fmt(circulating)}</b><span>In wallets</span></div>
  `;

  const tb = document.querySelector("#wallet-table tbody");
  tb.innerHTML = Object.entries(wallets).map(([id, bal]) => `
    <tr>
      <td><code>${id}</code></td>
      <td>${ROLES[id] || "Member"}</td>
      <td class="num">${fmt(bal)} AK$</td>
    </tr>
  `).join("");

  document.getElementById("uhi-cards").innerHTML = `
    <div class="card"><strong>${fmt(rate)} AK$</strong>Monthly rate, Melbourne calendar</div>
    <div class="card"><strong>${enrolled.join(" · ")}</strong>Enrolled this cycle</div>
  `;

  const txb = document.querySelector("#tx-table tbody");
  const rows = (data.tx || []).slice().reverse();
  txb.innerHTML = rows.map(t => {
    let detail = t.reason || "";
    if (t.type === "uhi") detail = `${t.period} → ${(t.to || []).join(", ")}`;
    else if (t.to) detail = `${detail} → ${t.to}`;
    const amt = t.amount || t.rate || "";
    return `<tr>
      <td>${t.at ? when(t.at) : ""}</td>
      <td>${t.type}</td>
      <td>${detail}</td>
      <td class="num">${amt ? fmt(amt) : ""}</td>
    </tr>`;
  }).join("");
}

fetch("data/ledger.json")
  .then(r => r.json())
  .then(render)
  .catch(() => {
    document.getElementById("home-stats").innerHTML = "<p class='fine'>Ledger failed to load.</p>";
  });
