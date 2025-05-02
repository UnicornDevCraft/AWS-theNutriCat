// This file contains the validation logic for the registration and log-in forms.

// Centralized validation router
function validateField(field, value) {
  switch (field) {
    case "email":
      return validateEmail(value);
    case "password":
      return validatePassw(value);
    case "confirm_password":
      return confirmPassw(value);
    case "terms":
      return checkTerms();
    default:
      return "";
  }
}

// All input validations
function setupInputValidation(inputFields, formStatus, submitButton) {
  inputFields.forEach((inputField) => {
    const field = inputField.dataset.field;
    const feedback = inputField.closest(".input-group, .check")?.querySelector(".feedback");

    inputField.addEventListener("focus", () => {
      if (!inputField.value && feedback) {
        feedback.innerHTML = `Please enter your ${field.replace("_", " ")}`;
        feedback.style.color = "white";
      }

      if (field.includes("password")) {
        const toggleBtn = inputField.closest(".input-group")?.querySelector(".toggleBtn");
        toggleBtn?.classList.remove("hidden");
      }
    });

    inputField.addEventListener("input", () => {
      const value = inputField.name === "terms" ? inputField.checked : inputField.value.trim();
      const status = validateField(field, value);
      if (feedback) {
        feedback.innerHTML = status !== "Looks good!" ? status : "";
        feedback.style.color = status !== "Looks good!" ? "#f84e5f" : "inherit";
      }

      formStatus[field] = status === "Looks good!" ? 0 : 1;
      updateSubmitButtonState(formStatus, submitButton);
    });

    inputField.addEventListener("blur", () => {
      if (formStatus[field] === 0 && feedback) {
        feedback.innerHTML = "";
      }
    });
  });
}

// Validates email
function validateEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  let error = "";
  if (email.length < 1) {
    error = "An email address is required";
  } else if (!emailPattern.test(email)) {
    error = "Please enter a valid email address (e.g., user@example.com)";
  } else {
    error = "Looks good!";
  }
  return error;
}

// Validate password
function validatePassw(password) {
  const lower = new RegExp("(?=.*[a-z])");
  const upper = new RegExp("(?=.*[A-Z])");
  const number = new RegExp("(?=.*[0-9])");
  const special = new RegExp("(?=.*[!@#$%^&*])");
  const length = new RegExp("(?=.{8,128})");
  let error = "";

  if (!lower.test(password)) {
    error = "At least one lowercase character required";
  } else if (!upper.test(password)) {
    error = "At least one uppercase character required";
  } else if (!number.test(password)) {
    error = "At least one number required";
  } else if (!special.test(password)) {
    error = "At least one special character required";
  } else if (!length.test(password)) {
    error = "At least 8 characters required";
  } else {
    error = "Looks good!";
  }
  return error;
}

// Confirm Password
function confirmPassw(confirmPassword) {
  let error = "";
  if (confirmPassword === document.querySelector("#password").value) {
    error = "Looks good!";
  } else {
    error = "Passwords do not match";
  }
  return error;
}

// Check terms
function checkTerms() {
  const terms = document.querySelector("#terms");
  let error = "";

  if (terms.checked) {
    error = "Looks good!";
  } else {
    error = "Please accept the terms and conditions";
  }
  return error;
}



