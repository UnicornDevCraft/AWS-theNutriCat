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

    // Updating submit button state
    updateSubmitButtonState(formStatus, submitButton);
    setupInputValidation(inputFields, formStatus, submitButton);
    setupPasswordToggles(toggleBtns);
    setupFormSubmitWithSpinner(form, submitButton, "Submitted");
    autoDismissToasts();
  });
} else if(window.location.pathname.startsWith("/auth/login")) {
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

        updateSubmitButtonState(formStatus, submitButton);
        setupInputValidation(inputFields, formStatus, submitButton);
        setupPasswordToggles(toggleBtns);
        setupFormSubmitWithSpinner(form, submitButton, "Login");
        autoDismissToasts();          
  });
}
