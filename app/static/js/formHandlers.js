// This file contains the JavaScript code for form events, button spinner, flash message timeouts and password toggle functionality.

// Sets up the form submission with a spinner
function setupPasswordToggles(toggleBtns) {
  toggleBtns.forEach((toggleBtn) => {
    toggleBtn.addEventListener("click", () => {
      const passwordField = toggleBtn.closest(".input-group")?.querySelector(".required-field");
      if (!passwordField) return;

      const isHidden = passwordField.type === "password";
      passwordField.setAttribute("type", isHidden ? "text" : "password");
      toggleBtn.classList.toggle("showing", isHidden);
    });
  });
}

// Sets up the form submission with a spinner
function setupFormSubmitWithSpinner(form, submitButton, successLabel = "Submitted") {
  form.addEventListener("submit", () => {
    if (submitButton.disabled) return;

    submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`;
    submitButton.disabled = true;

    setTimeout(() => {
      submitButton.innerHTML = `${successLabel} <i class="bi bi-send"></i>`;
      submitButton.disabled = false;
    }, 2000);
  });
}

// Updates submit button state
function updateSubmitButtonState(hasStatus, forButton) {
  const hasErrors = Object.values(hasStatus).some((status) => status !== 0);
  forButton.disabled = hasErrors;
  forButton.classList.toggle("disabled-button", hasErrors);
}

// Sets up the timeout for the flash messages
function autoDismissToasts() {
  document.querySelectorAll(".toast").forEach((toast) => {
    toast.timeOut = setTimeout(() => toast.remove(), 5500);
  });
}
