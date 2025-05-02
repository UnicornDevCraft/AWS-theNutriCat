// This file contains the JavaScript code for the create recipe page.

// Dynamically adds a new ingredient input row to the form
function addIngredient(ingredientData = null) {
  const container = document.getElementById('ingredients-container');
  const row = document.createElement('div');
  row.className = "row g-2 mb-2";

  row.innerHTML = `
      <div class="col-11">
        <input type="text" name="ingredient_name[]" class="form-control" placeholder="Ingredient" list="ingredient-list" title="Ingredient name" value="${ingredientData ? ingredientData.name : ''}" required>
      </div>
      <div class="col-auto">
        <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.closest('.row').remove()">
          ✕
        </button>
      </div>
      <div class="col-4 col-md-2">
        <input type="text" name="quantity[]" class="form-control" title="Ingredient quantity" placeholder="Qty" value="${ingredientData ? ingredientData.quantity : ''}">
      </div>
      <div class="col-4 col-md-2">
        <input type="text" name="unit[]" class="form-control" title="Quantity unit" placeholder="Unit" value="${ingredientData ? ingredientData.unit : ''}">
      </div>
      <div class="col-4 col-md-2">
        <input type="text" name="quantity_notes[]" class="form-control" title="Quantity notes" placeholder="(to taste)" value="${ingredientData ? ingredientData.quantity_notes : ''}">
      </div>
      <div class="col-5">
        <input type="text" name="ingredient_notes[]" class="form-control" title="Ingredient notes" placeholder="Note (e.g. cooked, raw, etc.)" value="${ingredientData ? ingredientData.notes : ''}">
      </div>
      
    `;

  container.appendChild(row);
}
// Dynamically adds a new instruction input row to the form
function addInstruction(instructionData = null) {
  const container = document.getElementById('instructions-container');
  const row = document.createElement('div');
  row.className = "row g-2 mb-2";

  row.innerHTML = `
      <div class="col-2">
        <input type="number" name="step[]" min="1" max="50" class="form-control" title="Step number" placeholder="Step" value="${instructionData ? instructionData.step : ''}" required>
      </div>
      <div class="col-9">
        <textarea name="instruction[]" class="form-control instruction" title="Instruction text" placeholder="Instruction" rows="3" required>${instructionData ? instructionData.text : ''}</textarea>
      </div>
      <div class="col-auto">
      <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.closest('.row').remove()">
          ✕
        </button>
      </div>
    `;
  container.appendChild(row);
  updateStepNumbers();
}
// Dynamically adds a new tag input row to the form.
function addTag(tagData = null) {
  const container = document.getElementById('tags-container');
  const row = document.createElement('div');
  row.className = "row g-2 mb-2";

  row.innerHTML = `
      <div class="col-11">
        <input type="text" name="tag[]" class="form-control" placeholder="Tag" title="Tag for the recipe" list="tag-list" value="${tagData ? tagData.name : ''}" required>
      </div>
      <div class="col-auto">
      <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.closest('.row').remove()">
          ✕
        </button>
      </div>
    `;
  container.appendChild(row);
}

// Checks the recipe form for validity and displays an alert if invalid
function checkRecipeForm(form, alertBox) {
  form.addEventListener("submit", function (event) {
    alertBox.classList.add('d-none'); // Hide any previous alert
    let customInvalid = false;

    // Bootstrap built-in validation
    if (!form.checkValidity()) {
      customInvalid = true;
      alertBox.textContent = "Please fill in all required fields.";
      // Scroll to the alert
      alertBox.scrollIntoView({ behavior: "smooth", block: "center" });
      alertBox.setAttribute("tabindex", "-1");
      alertBox.focus();
    }

    // Custom field checks
    const ingredients = document.querySelectorAll('input[name="ingredient_name[]"]');
    const instructions = document.querySelectorAll('textarea[name="instruction[]"]');
    const tags = document.querySelectorAll('input[name="tag[]"]');

    if (ingredients.length === 0 || instructions.length === 0 || tags.length === 0) {
      customInvalid = true;
      alertBox.textContent = "At least one ingredient, instruction, and tag is required.";
    }

    if (customInvalid) {
      event.preventDefault();
      event.stopPropagation();
      alertBox.classList.remove("d-none");

      // Auto-hide after 5 seconds
      setTimeout(() => {
        alertBox.classList.add("fade");
        alertBox.classList.remove("show");

        setTimeout(() => {
          alertBox.classList.add("d-none");
          alertBox.classList.remove("fade");
        }, 300);
      }, 5000);
    }

    form.classList.add("was-validated");
  });
}

// Updates the step numbers in the instruction form
function updateStepNumbers() {
  const stepInputs = document.querySelectorAll('input[name="step[]"]');
  stepInputs.forEach((input, index) => {
    input.value = index + 1;
  });
}

// Removes the image preview and clears the input field
function removeImage() {
  const imageInput = document.getElementById('image');
  imageInput.value = '';
  const currentImage = document.querySelector('.img-fluid');
  if (currentImage) {
    currentImage.style.display = 'none';
  }
}

// Shows a preview of the uploaded image
function showPreview() {
  const imageInput = document.getElementById('image');
  const preview = document.getElementById('image-preview');
  const uploadError = document.getElementById('upload-error');
  const maxSize = 4 * 1024 * 1024;

  imageInput.addEventListener('change', function () {
    uploadError.textContent = '';
    uploadError.classList.remove("alert", "alert-danger");

    const file = this.files[0];
    if (file) {
      if (file.size > maxSize) {
        uploadError.textContent = "File is too large! Maximum size is 4MB.";
        uploadError.classList.add("alert", "alert-danger");
        imageInput.value = "";
        preview.src = "#";
        preview.style.display = "none";
        return;
      }

      const reader = new FileReader();

      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };

      reader.readAsDataURL(file);
    } else {
      preview.src = '#';
      preview.style.display = 'none';
    }
  });
}

// This script is for the create and edit recipe pages.
// It handles the dynamic addition of ingredients, instructions, and tags,
// as well as form validation and image preview functionality.
if (window.location.pathname.startsWith('/create')) {
  document.addEventListener("DOMContentLoaded", function () {
    // Add the first ingredient row on page load
    addIngredient();
    addInstruction();
    addTag();
    btnShine();

    const form = document.getElementById("add-recipe-form");
    const alertBox = document.getElementById("form-alert");

    checkRecipeForm(form, alertBox);
    showPreview();
  });
} else if (window.location.pathname.startsWith('/edit')) {
  document.addEventListener("DOMContentLoaded", function () {
    // Prefill the ingredients, instructions
    btnShine();

    const form = document.getElementById("edit-recipe-form");
    const alertBox = document.getElementById("form-alert");

    checkRecipeForm(form, alertBox);
    showPreview();
  });
}