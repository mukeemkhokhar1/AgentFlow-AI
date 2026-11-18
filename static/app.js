const form = document.querySelector("#workflow-form");
const input = document.querySelector("#task-input");
const runButton = document.querySelector("#run-button");
const resultSection = document.querySelector("#result-section");
const toast = document.querySelector("#toast");

function notify(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2600);
}

document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.textContent;
    input.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const request = input.value.trim();
  if (request.length < 5) return notify("Please enter at least 5 characters.");
  runButton.disabled = true;
  runButton.querySelector("span").textContent = "Running…";
  try {
    const response = await fetch("/api/workflows", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({request})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Workflow failed.");
    renderResult(data);
    await loadHistory();
    notify("Workflow completed successfully.");
  } catch (error) {
    notify(error.message || "Unable to reach the server.");
  } finally {
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "Run workflow";
  }
});

function renderResult(data) {
  resultSection.classList.remove("hidden");
  document.querySelector("#result-status").textContent = data.status.toUpperCase();
  const descriptions = {
    "Planner Agent": "Creates a structured action plan",
    "Execution Agent": "Processes and tracks each step",
    "Review Agent": "Checks workflow completion"
  };
  document.querySelector("#agent-list").innerHTML = data.agents.map((agent) =>
    `<article class="agent"><strong>${escapeHtml(agent)}</strong><span>✓ Completed</span><p class="muted">${descriptions[agent]}</p></article>`
  ).join("");
  document.querySelector("#plan-list").innerHTML = data.plan.map((step) =>
    `<li>${escapeHtml(step)}</li>`
  ).join("");
  document.querySelector("#review-text").textContent =
    `${data.review.message} ${data.review.completed_steps}/${data.review.total_steps} steps completed. Workflow ID: ${data.id}.`;
  resultSection.scrollIntoView({behavior: "smooth", block: "start"});
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

async function loadHistory() {
  const target = document.querySelector("#history-list");
  try {
    const response = await fetch("/api/workflows");
    if (!response.ok) throw new Error("History unavailable");
    const items = await response.json();
    target.innerHTML = items.length ? items.map((item) =>
      `<div class="history-item"><span>${escapeHtml(item.request.slice(0, 90))}</span><span>${escapeHtml(item.status)}</span></div>`
    ).join("") : '<p class="muted">No workflows yet. Run your first workflow above.</p>';
  } catch {
    target.innerHTML = '<p class="muted">Unable to load workflow history.</p>';
  }
}

document.querySelector("#refresh-button").addEventListener("click", loadHistory);
loadHistory();
