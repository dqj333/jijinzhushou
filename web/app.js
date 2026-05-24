const state = {
  config: null,
  summary: null,
  report: "",
};

const currency = new Intl.NumberFormat("zh-CN", {
  style: "currency",
  currency: "CNY",
  maximumFractionDigits: 0,
});

function $(selector) {
  return document.querySelector(selector);
}

function setStatus(message, type = "info") {
  const box = $("#status");
  box.hidden = !message;
  box.textContent = message || "";
  box.className = `status ${type === "error" ? "error" : ""}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let message = `请求失败：${response.status}`;
    try {
      const payload = await response.json();
      message = payload.message || payload.error || message;
    } catch {
      message = await response.text();
    }
    throw new Error(message);
  }
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return response.json();
  return response.text();
}

async function loadAll() {
  setStatus("正在加载本地数据...");
  const [config, summary, report] = await Promise.all([
    api("/api/config"),
    api("/api/summary"),
    api("/api/report/latest").catch(() => ""),
  ]);
  state.config = config;
  state.summary = summary;
  state.report = report;
  render();
  setStatus("");
}

function render() {
  renderOverview();
  renderHoldings();
  renderSettings();
  $("#reportText").textContent = state.report || "暂无日报。";
}

function renderOverview() {
  const context = state.summary?.context;
  const tradePlan = state.summary?.trade_plan;
  if (!context) return;

  $("#reportDate").textContent = context.report_date || "-";
  $("#totalValue").textContent = currency.format(context.portfolio?.total_value || 0);
  $("#dailyBudget").textContent = currency.format(tradePlan?.daily_budget || 0);
  $("#plannedAmount").textContent = currency.format(tradePlan?.planned_amount || 0);

  const buyItems = (tradePlan?.decisions || []).filter((item) => Number(item.amount || 0) > 0);
  $("#buyList").innerHTML = buyItems.length
    ? buyItems.map(renderBuyCard).join("")
    : `<div class="decision-card muted">今天没有达到买入金额阈值的基金。</div>`;

  const risks = context.portfolio?.risk_flags || [];
  $("#riskList").innerHTML = risks.length
    ? risks.map((risk) => `<div class="risk-item">${escapeHtml(risk)}</div>`).join("")
    : `<div class="risk-item muted">当前没有触发组合级风险。</div>`;

  $("#decisionRows").innerHTML = (tradePlan?.decisions || []).map(renderDecisionRow).join("");
}

function renderBuyCard(item) {
  return `
    <article class="decision-card">
      <div class="decision-title">
        <span>${escapeHtml(item.name)} (${escapeHtml(item.code)})</span>
        <span class="amount">${currency.format(item.amount || 0)}</span>
      </div>
      <div class="muted">评分 ${item.score ?? "-"}，净值日期 ${item.latest_date || "-"}</div>
      <div>${escapeHtml((item.reasons || []).slice(0, 3).join("；"))}</div>
    </article>
  `;
}

function renderDecisionRow(item) {
  return `
    <tr>
      <td><strong>${escapeHtml(item.name)}</strong><br><span class="muted">${escapeHtml(item.code)}</span></td>
      <td class="${tierClass(item.action || item.tier)}">${escapeHtml(item.action || item.tier || "-")}</td>
      <td>${currency.format(item.amount || 0)}</td>
      <td>${item.score ?? "-"}</td>
      <td>${item.latest_date || "-"}</td>
      <td>${escapeHtml((item.reasons || []).join("；"))}<br><span class="muted">${escapeHtml((item.risks || []).join("；"))}</span></td>
    </tr>
  `;
}

function tierClass(text) {
  if (!text) return "";
  if (text.includes("买") || text.includes("可以")) return "tier-buy";
  if (text.includes("禁止")) return "tier-block";
  return "tier-watch";
}

function renderHoldings() {
  const funds = state.config?.funds || [];
  $("#fundRows").innerHTML = funds
    .map(
      (fund, index) => `
      <tr data-index="${index}">
        ${inputCell("code", fund.code, "text")}
        ${inputCell("name", fund.name, "text", "name-input")}
        ${inputCell("type", fund.type, "text")}
        ${inputCell("category", fund.category, "text")}
        ${inputCell("holding_amount", fund.holding_amount, "number")}
        ${inputCell("target_ratio", fund.target_ratio, "number", "", "0.01")}
        ${inputCell("screenshot_profit_amount", fund.screenshot_profit_amount, "number")}
        ${inputCell("screenshot_profit_pct", fund.screenshot_profit_pct, "number")}
        <td><button class="danger" data-remove="${index}">删除</button></td>
      </tr>
    `
    )
    .join("");
}

function inputCell(name, value, type, className = "", step = "0.01") {
  const stepAttr = type === "number" ? ` step="${step}"` : "";
  return `<td><input class="${className}" data-field="${name}" type="${type}"${stepAttr} value="${escapeAttr(value ?? "")}"></td>`;
}

function renderSettings() {
  const profile = state.config?.profile || {};
  const form = $("#settingsForm");
  for (const [key, value] of Object.entries(profile)) {
    const field = form.elements[key];
    if (!field) continue;
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = value ?? "";
    }
  }
}

function collectConfigFromUi() {
  const config = structuredClone(state.config);
  const form = $("#settingsForm");
  const profile = config.profile;

  for (const field of form.elements) {
    if (!field.name) continue;
    if (field.type === "checkbox") {
      profile[field.name] = field.checked;
    } else if (field.type === "number") {
      profile[field.name] = field.value === "" ? null : Number(field.value);
    } else {
      profile[field.name] = field.value;
    }
  }

  config.funds = Array.from(document.querySelectorAll("#fundRows tr")).map((row) => {
    const oldFund = config.funds[Number(row.dataset.index)] || {};
    const fund = { ...oldFund };
    for (const input of row.querySelectorAll("input")) {
      const key = input.dataset.field;
      fund[key] = input.type === "number" ? (input.value === "" ? null : Number(input.value)) : input.value.trim();
    }
    return fund;
  });
  return config;
}

async function saveConfig() {
  setStatus("正在保存配置...");
  const payload = collectConfigFromUi();
  const result = await api("/api/config", { method: "PUT", body: JSON.stringify(payload) });
  state.config = result.config;
  renderHoldings();
  renderSettings();
  setStatus("配置已保存。");
}

async function run(mode) {
  setStatus(mode === "online" ? "正在联网更新净值并生成报告..." : "正在使用本地净值重新计算...");
  const result = await api("/api/run", { method: "POST", body: JSON.stringify({ mode }) });
  state.summary = result.summary;
  state.report = await api("/api/report/latest").catch(() => "");
  renderOverview();
  $("#reportText").textContent = state.report || "暂无日报。";
  const message = result.message || (result.ok ? "报告已生成。" : "报告生成失败，请查看终端输出。");
  setStatus(message, result.ok ? "info" : "error");
}

async function saveAndRun() {
  await saveConfig();
  await run("cached");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll("\n", " ");
}

function bindEvents() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      $(`#${button.dataset.tab}`).classList.add("active");
    });
  });

  $("#runCached").addEventListener("click", () => run("cached").catch((error) => setStatus(error.message, "error")));
  $("#runOnline").addEventListener("click", () => run("online").catch((error) => setStatus(error.message, "error")));
  $("#saveConfig").addEventListener("click", () => saveConfig().catch((error) => setStatus(error.message, "error")));
  $("#saveConfigAndRun").addEventListener("click", () => saveAndRun().catch((error) => setStatus(error.message, "error")));
  $("#saveSettings").addEventListener("click", () => saveConfig().catch((error) => setStatus(error.message, "error")));
  $("#saveSettingsAndRun").addEventListener("click", () => saveAndRun().catch((error) => setStatus(error.message, "error")));
  $("#reloadReport").addEventListener("click", async () => {
    state.report = await api("/api/report/latest").catch(() => "");
    $("#reportText").textContent = state.report || "暂无日报。";
  });
  $("#addFund").addEventListener("click", () => {
    state.config.funds.push({
      code: "",
      name: "",
      type: "",
      category: "",
      holding_amount: 0,
      shares: null,
      cost_nav: null,
      monthly_plan: 0,
      target_ratio: 0,
      screenshot_profit_amount: 0,
      screenshot_profit_pct: 0,
    });
    renderHoldings();
  });
  $("#fundRows").addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove]");
    if (!button) return;
    state.config.funds.splice(Number(button.dataset.remove), 1);
    renderHoldings();
  });
}

bindEvents();
loadAll().catch((error) => setStatus(error.message, "error"));
