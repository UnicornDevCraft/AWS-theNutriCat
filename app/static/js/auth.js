/* Registration form validation, letItSnow animation and button shine effect, timeout for flash notifications */

/* Button shine animation */
function btnShine() {
  const button = document.querySelector(".shining-btn");
  const text = button.textContent;
  button.innerHTML = "";

  for (let char of text) {
    let span = document.createElement("span");
    span.textContent = char === "  " ? "\u00A0" : char;
    button.appendChild(span);
  }
  let spans = button.querySelectorAll("span");

  button.addEventListener("mouseenter", () => {
    spans.forEach((span, index) => {
      setTimeout(() => {
        span.classList.add("hover");
      }, index * 50);
    });
  });

  button.addEventListener("mouseleave", () => {
    spans.forEach((span, index) => {
      setTimeout(() => {
        span.classList.remove("hover");
      }, index * 50);
    });
  });
}

// Snowfall animation
function letItSnow() {
  let container = document.querySelector("#container");
  let count = 50;
  for (var i = 0; i < count; i++) {
    let leftSnow = Math.floor(Math.random() * container.clientWidth);
    let topSnow = Math.floor(Math.random() * container.clientHeight);
    let widthSnow = Math.floor(Math.random() * count);
    let timeSnow = Math.floor((Math.random() * count) / 10 + 5);
    let blurSnow = Math.floor((Math.random() * count) / 2.5);
    let div = document.createElement("div");
    div.classList.add("snow");
    div.style.left = leftSnow + "px";
    div.style.top = topSnow + "px";
    div.style.width = widthSnow + "px";
    div.style.height = widthSnow + "px";
    div.style.animationDuration = timeSnow + "s";
    div.style.filter = "blur(" + blurSnow + "px)";
    container.appendChild(div);
  }
}

// Updates submit button state
function updateSubmitButtonState(hasStatus, forButton) {
  const hasErrors = Object.values(hasStatus).some((status) => status !== 0);
  forButton.disabled = hasErrors;
  forButton.classList.toggle("disabled-button", hasErrors);
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

if (window.location.pathname.startsWith("/auth/register")) {
  document.addEventListener("DOMContentLoaded", () => {
    letItSnow();
    btnShine();
    // Declaring variables for registration form validation
    const form = document.querySelector("#registration-form");
    const submitButton = document.querySelector("#submit-registration-form");
    let inputFields = form.querySelectorAll(".required-field");
    let toggleBtns = document.querySelectorAll(".toggleBtn");

    let formStatus = {
      email: 1,
      password: 1,
      confirm_password: 1,
      terms: 1,
    };

    // Updating submit button state
    updateSubmitButtonState(formStatus, submitButton);

    inputFields.forEach((inputField) => {
      let feedback = inputField
        .closest(".input-group, .check")
        .querySelector(".feedback");
      // Listen on focus and provide instructions to fill in the fields
      inputField.addEventListener("focus", () => {
        const fieldType = inputField.dataset.field;
        if (!inputField.value) {
          feedback.innerHTML = `Please enter your ${fieldType.replace(
            "_",
            " "
          )}`;
          feedback.style.color = "white";
        }

        if (fieldType.includes("password")) {
          let toggleBtn = inputField
            .closest(".input-group")
            .querySelector(".toggleBtn");
          toggleBtn.classList.remove("hidden");
        }
      });
      // Validating fields and updating status
      inputField.addEventListener("input", () => {
        const value = inputField.value.trim();
        let status = "";
        if (inputField.name === "email") {
          status = validateEmail(value);
        } else if (inputField.name === "password") {
          status = validatePassw(value);
        } else if (inputField.name === "confirmation") {
          status = confirmPassw(value);
        } else {
          status = checkTerms();
        }
        // Setting status as the feedback message
        if (status !== "Looks good!") {
          feedback.innerHTML = status;
          feedback.style.color = "#f84e5f";
        } else {
          feedback.innerHTML = "";
        }

        formStatus[inputField.dataset.field] = status === "Looks good!" ? 0 : 1;

        // Updating submit button state
        updateSubmitButtonState(formStatus, submitButton);
      });

      // Cleaning feedback when out of focus
      inputField.addEventListener("blur", () => {
        if (formStatus[inputField.dataset.field] === 0) {
          feedback.innerHTML = "";
        }
      });
    });

    // Show or hide password
    toggleBtns.forEach((toggleBtn) => {
      toggleBtn.addEventListener("click", () => {
        let passwordField = toggleBtn
          .closest(".input-group")
          .querySelector(".required-field");
        if (passwordField.type === "password") {
          passwordField.setAttribute("type", "text");
          toggleBtn.classList.add("showing");
        } else {
          passwordField.setAttribute("type", "password");
          toggleBtn.classList.remove("showing");
        }
      });
    });

    // Submit form with a spinner
    form.addEventListener("submit", () => {
      if (submitButton.disabled) return;

      // Show spinner and simulate submission
      submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`;
      submitButton.disabled = true;

      // Simulate server processing
      setTimeout(() => {
        /* alert("Form submitted successfully!"); */
        submitButton.innerHTML = `Submited <i class="bi bi-send"></i>`;
        submitButton.disabled = false;
      }, 2000);
    });
  });

  // Notifications configuration
  let toasts = document.querySelectorAll(".toast");
  toasts.forEach((toast) => {
    toast.timeOut = setTimeout(() => toast.remove(), 5500);
  });
} else if(window.location.pathname.startsWith("/auth/login")) {
    document.addEventListener("DOMContentLoaded", () => {
        letItSnow();
        btnShine();
        // Declaring variables for login form validation
        const form = document.querySelector("#login-form");
        const submitButton = document.querySelector("#submit-login-form");
        let inputFields = form.querySelectorAll(".required-field");
        let toggleBtns = document.querySelectorAll(".toggleBtn");
    
        let formStatus = {
          email: 1,
          password: 1,
        };
    
        // Updating submit button state
        updateSubmitButtonState(formStatus, submitButton);
        console.log(formStatus);

        inputFields.forEach((inputField) => {
            let feedback = inputField.closest(".input-group").querySelector(".feedback");
            // Listen on focus and provide instructions to fill in the fields
            inputField.addEventListener("focus", () => {
              const fieldType = inputField.dataset.field;
              if (!inputField.value) {
                feedback.innerHTML = `Please enter your ${fieldType}`;
                feedback.style.color = "white";
              }
      
              if (fieldType.includes("password")) {
                let toggleBtn = inputField.closest(".input-group").querySelector(".toggleBtn");
                toggleBtn.classList.remove("hidden");
              }
            });
            // Validating fields and updating status
            inputField.addEventListener("input", () => {
              const value = inputField.value.trim();
              let status = "";
              if (inputField.name === "email") {
                status = validateEmail(value);
              } else if (inputField.name === "password") {
                status = validatePassw(value);
              }
              // Setting status as the feedback message
              if (status !== "Looks good!") {
                feedback.innerHTML = status;
                feedback.style.color = "#f84e5f";
              } else {
                feedback.innerHTML = "";
              }
      
              formStatus[inputField.dataset.field] = status === "Looks good!" ? 0 : 1;
      
              // Updating submit button state
              updateSubmitButtonState(formStatus, submitButton);
            });
      
            // Cleaning feedback when out of focus
            inputField.addEventListener("blur", () => {
              if (formStatus[inputField.dataset.field] === 0) {
                feedback.innerHTML = "";
              }
            });
          });
      
          // Show or hide password
          toggleBtns.forEach((toggleBtn) => {
            toggleBtn.addEventListener("click", () => {
              let passwordField = toggleBtn
                .closest(".input-group")
                .querySelector(".required-field");
              if (passwordField.type === "password") {
                passwordField.setAttribute("type", "text");
                toggleBtn.classList.add("showing");
              } else {
                passwordField.setAttribute("type", "password");
                toggleBtn.classList.remove("showing");
              }
            });
          });
      
          // Submit form with a spinner
          form.addEventListener("submit", () => {
            if (submitButton.disabled) return;
      
            // Show spinner and simulate submission
            submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`;
            submitButton.disabled = true;
      
            // Simulate server processing
            setTimeout(() => {
              /* alert("Form submitted successfully!"); */
              submitButton.innerHTML = `Login <i class="bi bi-send"></i>`;
              submitButton.disabled = false;
            }, 2000);
          });
        });
      
        // Notifications configuration
        let toasts = document.querySelectorAll(".toast");
        toasts.forEach((toast) => {
          toast.timeOut = setTimeout(() => toast.remove(), 5500);
        });
}
