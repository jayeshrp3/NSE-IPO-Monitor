"use strict";

function showError(container, message) {
  container.textContent = message;
  container.classList.remove("d-none");
  container.focus();
}

async function responseMessage(response) {
  try {
    const body = await response.json();
    return body.detail || "The request could not be completed.";
  } catch (error) {
    if (error instanceof SyntaxError) {
      return "The server returned an unreadable response.";
    }
    throw error;
  }
}

const ipoForm = document.querySelector("#ipo-form");
if (ipoForm) {
  ipoForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const errorBox = document.querySelector("#form-errors");
    errorBox.classList.add("d-none");

    const payload = {
      company_name: ipoForm.elements.company_name.value,
      opening_date: ipoForm.elements.opening_date.value,
      closing_date: ipoForm.elements.closing_date.value,
    };
    for (const field of ["allotment_date", "refund_date", "listing_date"]) {
      const input = ipoForm.elements[field];
      const clear = document.querySelector(`#clear_${field}`);
      if (clear?.checked) {
        payload[field] = "";
      } else if (input.value) {
        payload[field] = input.value;
      } else if (!ipoForm.dataset.ipoId) {
        payload[field] = "";
      }
    }

    const ipoId = ipoForm.dataset.ipoId;
    const url = ipoId ? `/api/ipos/${encodeURIComponent(ipoId)}` : "/api/ipos";
    const method = ipoId ? "PUT" : "POST";
    try {
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        showError(errorBox, await responseMessage(response));
        return;
      }
      const record = await response.json();
      window.location.assign(`/ipos/${record.id}`);
    } catch (error) {
      showError(errorBox, `Unable to reach the server: ${error.message}`);
    }
  });
}

for (const button of document.querySelectorAll("[data-delete-url]")) {
  button.addEventListener("click", async () => {
    const name = button.dataset.deleteName || "this IPO";
    if (!window.confirm(`Delete ${name}? This action cannot be undone.`)) {
      return;
    }
    button.disabled = true;
    try {
      const response = await fetch(button.dataset.deleteUrl, { method: "DELETE" });
      if (!response.ok) {
        const message = await responseMessage(response);
        window.alert(message);
        button.disabled = false;
        return;
      }
      window.location.assign("/");
    } catch (error) {
      window.alert(`Unable to reach the server: ${error.message}`);
      button.disabled = false;
    }
  });
}
