// This file contains the Javascript code for registration and sign-in forms.

if (window.location.pathname.startsWith("/auth/register")) {
  document.addEventListener("DOMContentLoaded", () => {
    letItSnow();
    btnShine();

    // Declaring variables for registration form validation
    const form = document.querySelector("#registration-form");
    const submitButton = document.querySelector("#submit-registration-form");
    const inputFields = form.querySelectorAll(".required-field");
    const toggleBtns = document.querySelectorAll(".toggleBtn");

    const formStatus = {
      email: 1,
      password: 1,
      confirm_password: 1,
      terms: 1,
    };

    // Updating form status and submit button state
    updateSubmitButtonState(formStatus, submitButton);
    setupInputValidation(inputFields, formStatus, submitButton);
    setupPasswordToggles(toggleBtns);
    setupFormSubmitWithSpinner(form, submitButton, "Submitted");
    autoDismissToasts();
  });
} else if (window.location.pathname.startsWith("/auth/login")) {
  document.addEventListener("DOMContentLoaded", () => {
    letItSnow();
    btnShine();

    // Declaring variables for login form validation
    const form = document.querySelector("#login-form");
    const submitButton = document.querySelector("#submit-login-form");
    const inputFields = form.querySelectorAll(".required-field");
    const toggleBtns = document.querySelectorAll(".toggleBtn");

    const formStatus = {
      email: 1,
      password: 1,
    };

    // Updating form status and submit button state
    updateSubmitButtonState(formStatus, submitButton);
    setupInputValidation(inputFields, formStatus, submitButton);
    setupPasswordToggles(toggleBtns);
    setupFormSubmitWithSpinner(form, submitButton, "Login");
    autoDismissToasts();
  });
} else if (window.location.pathname.startsWith("/auth/forgot-password")) {
  document.addEventListener("DOMContentLoaded", () => {
    letItSnow();
    btnShine();

    // Declaring variables for forgot password form validation
    const form = document.querySelector("#forgot-password-form");
    const submitButton = document.querySelector("#submit-forgot-password-form");
    const inputFields = form.querySelectorAll(".required-field");

    const formStatus = {
      email: 1,
    };
    // Updating form status and submit button state
    updateSubmitButtonState(formStatus, submitButton);
    setupInputValidation(inputFields, formStatus, submitButton);

    // Add form submission listener to check email only after submission
    form.addEventListener('submit', async (e) => {
      e.preventDefault(); // Prevent default form submission to control flow

      const emailInput = document.querySelector('#email');
      const email = emailInput.value.trim();

      // Check if email exists in the database
      const res = await fetch(`/auth/check-email?email=${encodeURIComponent(email)}`);
      const data = await res.json();

      if (!data.exists) {
        showAlertMessage("This email is not registered", "danger");
      } else {
        // Proceed to submit the form if the email is valid
        form.submit();
        setupFormSubmitWithSpinner(form, submitButton, "Submitted");
      }
    });

    autoDismissToasts();
  });
} else if (window.location.pathname.startsWith("/auth/reset-password")) {
  document.addEventListener("DOMContentLoaded", () => {
    letItSnow();
    btnShine();

    // Declaring variables for reset password form validation
    const form = document.querySelector("#reset-password-form");
    const submitButton = document.querySelector("#submit-reset-password-form");
    const inputFields = form.querySelectorAll(".required-field");
    const toggleBtns = document.querySelectorAll(".toggleBtn");

    const formStatus = {
      password: 1,
      confirm_password: 1,
    };
    // Updating form status and submit button state
    updateSubmitButtonState(formStatus, submitButton);
    setupInputValidation(inputFields, formStatus, submitButton);
    setupPasswordToggles(toggleBtns);
    setupFormSubmitWithSpinner(form, submitButton, "Submitted");
    autoDismissToasts();
  });
} else if (window.location.pathname.startsWith("/auth/profile")) {
  // Setting up the profile page change password modal
  const modal = document.getElementById("changePasswordModal");

  modal.addEventListener("shown.bs.modal", () => {
    const form = document.querySelector("#changePasswordForm");
    if (form) {
      const submitButton = document.querySelector("#submit-change-password-form");
      const inputFields = form.querySelectorAll(".required-field");

      const formStatus = {
        password: 1,
        confirm_password: 1,
      };

      // Updating form status and submit button state
      updateSubmitButtonState(formStatus, submitButton);
      setupInputValidation(inputFields, formStatus, submitButton);
      setupFormSubmitWithSpinner(form, submitButton, "Submitted");
    }
  });
}
