"use strict";

const form = document.getElementById("analysis-form");
const input = document.getElementById("announcement");
const status = document.getElementById("status");
const results = document.getElementById("results");

function addText(parent, tag, label, value) {
  const element = document.createElement(tag);
  if (label) {
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    element.appendChild(strong);
  }
  element.appendChild(document.createTextNode(value ?? "Not available"));
  parent.appendChild(element);
}

function displayAnalysis(data) {
  results.replaceChildren();
  addText(results, "p", "Schema version", data.schema_version);
  for (const [name, field] of Object.entries(data)) {
    if (!["company_name", "opening_date", "closing_date", "allotment_date", "refund_date", "listing_date"].includes(name)) continue;
    const item = document.createElement("div");
    addText(item, "p", name.replaceAll("_", " "), field.value);
    addText(item, "p", "Status", field.status);
    if (field.evidence) addText(item, "p", "Evidence", field.evidence);
    if (field.message) addText(item, "p", "Note", field.message);
    results.appendChild(item);
  }
  addText(results, "p", "Summary", data.summary);
  for (const warning of data.warnings) addText(results, "p", "Warning", warning);
  addText(results, "p", "Independent validation", data.validation.valid ? "Passed" : "Failed");
  for (const error of data.validation.errors) addText(results, "p", "Validation issue", error);
  results.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "Analyzing locally…";
  results.replaceChildren();
  results.hidden = true;
  try {
    const response = await fetch("/api/v1/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ announcement_text: input.value }),
    });
    const data = await response.json();
    if (!response.ok) {
      status.textContent = data.message || data.detail?.message || "Analysis failed.";
      return;
    }
    displayAnalysis(data);
    status.textContent = "Analysis complete.";
  } catch {
    status.textContent = "The local application could not be reached.";
  }
});
