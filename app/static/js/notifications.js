// This file contains functions to show notifications in the UI

// This function shows a flash message in the UI
function showFlashMessage(message, type = "info") {
  const container = document.getElementById("flash-container");

  if (!container) {
    console.warn("Flash container not found.");
    return;
  }

  // Create main toast element
  const toast = document.createElement("div");
  toast.className = `row toast ${type}`;

  // Icon span
  const icon = document.createElement("span");
  icon.className = "col material-symbols-outlined";
  icon.textContent = type === "success" ? "check_circle" : "error";
  icon.classList.add(type === "success" ? "type-success" : "type-error");

  // Content div
  const content = document.createElement("div");
  content.className = "col content";
  content.innerHTML = `
      <div class="title text-capitalize fs-5 fw-bold">${type}</div>
      <span class="fading">${message}</span>
    `;

  // Close button
  const close = document.createElement("span");
  close.className = "col material-symbols-outlined fading";
  close.textContent = "close";
  close.style.cursor = "pointer";
  close.onclick = () => toast.remove();

  // Append all to toast
  toast.appendChild(icon);
  toast.appendChild(content);
  toast.appendChild(close);

  // Append to container
  container.appendChild(toast);

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    toast.classList.add("fade");
    setTimeout(() => toast.remove(), 500);
  }, 5000);
};
