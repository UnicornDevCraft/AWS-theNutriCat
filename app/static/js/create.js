// This file contains the JavaScript code for the create recipe page.
console.log("Create recipe loaded");
function addIngredient() {
    const container = document.getElementById('ingredients-container');

    const row = document.createElement('div');
    row.className = "row g-2 mb-2";

    row.innerHTML = `
      <div class="col-12 col-md-6">
        <input type="text" name="ingredient_name[]" class="form-control" placeholder="Ingredient" list="ingredient-list" required>
      </div>
      <div class="col-4 col-md-2">
        <input type="text" name="quantity[]" class="form-control" placeholder="Qty">
      </div>
      <div class="col-4 col-md-2">
        <input type="text" name="unit[]" class="form-control" placeholder="Unit">
      </div>
      <div class="col-4 col-md-2">
        <input type="text" name="quantity_notes[]" class="form-control" placeholder="(to taste)">
      </div>
      <div class="col-12">
        <input type="text" name="ingredient_notes[]" class="form-control" placeholder="Note (e.g. cooked, raw, etc.)">
      </div>
    `;
    
    container.appendChild(row);
}

function addInstruction() {
    const container = document.getElementById('instructions-container');

    const row = document.createElement('div');
    row.className = "row g-2 mb-2";

    row.innerHTML = `
      <div class="col-4 col-md-2">
        <input type="text" name="step[]" class="form-control" placeholder="Step" required>
      </div>
      <div class="col-12">
        <textarea name="instruction[]" class="form-control instruction" placeholder="Instruction" rows="3" required></textarea>
      </div>
    `;
    
    container.appendChild(row);
  }

function addTag() {
    const container = document.getElementById('tags-container');

    const row = document.createElement('div');
    row.className = "row g-2 mb-2";

    row.innerHTML = `
      <div class="col-12">
        <input type="text" name="tag[]" class="form-control" placeholder="Tag" list="tag-list" required>
      </div>
    `;
    
    container.appendChild(row);
  }

  if (window.location.pathname.startsWith('/create')) {
    document.addEventListener("DOMContentLoaded", function () {
        // Add the first ingredient row on page load
        addIngredient();
        addInstruction();
        addTag();
        btnShine();

        const form = document.getElementById("add-recipe-form");
        const alertBox = document.getElementById("form-alert");

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
                
                // ⏱ Auto-hide after 5 seconds
                setTimeout(() => {
                    alertBox.classList.add("fade");
                    alertBox.classList.remove("show");
                
                    setTimeout(() => {
                    alertBox.classList.add("d-none");
                    alertBox.classList.remove("fade");
                    }, 300);
                    }, 5000);
            }

            form.classList.add("was-validated"); // Apply Bootstrap styles
        });
    });
    // Add event listener to the "Add Ingredient" button
    /* document.getElementById('add-ingredient').addEventListener('click', function() {
        addIngredient();
    }); */
  }