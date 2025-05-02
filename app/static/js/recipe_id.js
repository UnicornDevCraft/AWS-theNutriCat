// This file contains functions to handle the favorite button and serving size adjustment on the recipe page


// This function parses a string representing a quantity (like "1", "1/2", or "1 1/2") into a float
function parseQuantity(str) {
    // Converts "1", "1/2", or "1 1/2" into a float
    if (!str) return null;
    const parts = str.trim().split(' ');
    let total = 0;

    for (const part of parts) {
        if (part.includes('/')) {
            const [numerator, denominator] = part.split('/');
            total += parseFloat(numerator) / parseFloat(denominator);
        } else {
            total += parseFloat(part);
        }
    }

    return total;
}

// This function formats a float into a string representing a quantity (like "1", "1/2", or "1 1/2")
function formatQuantity(value) {
    // Round to nearest 1/4 for simplicity
    if (value == null) return '';

    const quarters = Math.round(value * 4);
    const whole = Math.floor(quarters / 4);
    const remainder = quarters % 4;

    let result = whole ? `${whole}` : '';
    if (remainder === 1) result += whole ? ' 1/4' : '1/4';
    else if (remainder === 2) result += whole ? ' 1/2' : '1/2';
    else if (remainder === 3) result += whole ? ' 3/4' : '3/4';

    return result.trim();
}

// This function updates the ingredient quantities based on the servings
function updateQuantities() {
    ingredientQuantities.forEach(span => {
        const original = span.dataset.original;
        const unit = span.dataset.unit;

        const originalValue = parseQuantity(original);
        if (originalValue == null) return;

        const newValue = originalValue * currentServings / originalServings;
        span.textContent = `${formatQuantity(newValue)}${unit ? ' ' + unit : ''}`;
    });
}

// This script is for the recipe page to handle the serving size adjustment and favorite button functionality
if (window.location.pathname.startsWith("/recipe/")) {
    document.addEventListener("DOMContentLoaded", function () {
        // Initialize the serving size adjustment
        const minusBtn = document.querySelector('.btn.minus');
        const plusBtn = document.querySelector('.btn.plus');
        const valueDisplay = document.querySelector('.value');
        const ingredientQuantities = document.querySelectorAll('.ingredient-quantity');

        let originalServings = parseInt(valueDisplay.textContent);
        let currentServings = originalServings;

        minusBtn.addEventListener('click', () => {
            if (currentServings > 1) {
                currentServings--;
                valueDisplay.textContent = currentServings;
                updateQuantities();
            }
        });

        plusBtn.addEventListener('click', () => {
            currentServings++;
            valueDisplay.textContent = currentServings;
            updateQuantities();
        });

        updateQuantities();
    });

    // Function to toggle favorite status
    document.querySelectorAll(".favorite-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const recipeId = this.getAttribute("data-recipe-id");
            const icon = this.querySelector(".heart-icon");

            // Disable button while waiting
            this.disabled = true;

            const isNowFavorite = await toggleFavorite(recipeId);

            if (isNowFavorite === true) {

                // Now it's a favorite
                icon.setAttribute("data-icon", "heart");
                icon.setAttribute("data-bs-title", "Remove from favorites");
                icon.classList.replace("bi-heart", "bi-heart-fill");
            } else if (isNowFavorite === false) {
                // Now it's removed from favorites
                icon.setAttribute("data-icon", "heart-outline");
                icon.setAttribute("data-bs-title", "Add to favorites");
                icon.classList.replace("bi-heart-fill", "bi-heart");
            } else {
                // Error or not logged in: do nothing or revert state if needed
                console.warn("Favorite toggle failed or user not logged in.");
            }

            this.disabled = false;
        });
    });

    // Add redirect functionality to filtered buttons
    document.querySelectorAll(".filtered-btn").forEach(button => {
        button.addEventListener("click", function () {
            const filter = this.getAttribute("data-filter");
            window.location.href = `/recipes?page=1&filter=${filter}`;
        });
    });
};