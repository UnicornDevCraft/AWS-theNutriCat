console.log("Recipe ID JS loaded");
if (window.location.pathname.startsWith("/recipe/")) {
    document.addEventListener("DOMContentLoaded", function () {
        console.log(window.location.pathname)

        const minusBtn = document.querySelector('.btn.minus');
        const plusBtn = document.querySelector('.btn.plus');
        const valueDisplay = document.querySelector('.value');
        const ingredientQuantities = document.querySelectorAll('.ingredient-quantity');
    
        let originalServings = parseInt(valueDisplay.textContent);
        let currentServings = originalServings;
    
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

    document.querySelectorAll(".favorite-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const recipeId = this.getAttribute("data-recipe-id");
            const icon = this.querySelector(".heart-icon");
    
            // Optional: disable button while waiting
            this.disabled = true;
    
            const isNowFavorite = await toggleFavorite(recipeId);
    
            if (isNowFavorite === true) {
                
                // Now it's a favorite
                icon.setAttribute("name", "heart");
                icon.setAttribute("data-bs-title", "Remove from favorites");
                icon.classList.replace("bi-heart", "bi-heart-fill");
            } else if (isNowFavorite === false) {
                // Now it's removed from favorites
                icon.setAttribute("name", "heart-outline");
                icon.setAttribute("data-bs-title", "Add to favorites");
                icon.classList.replace("bi-heart-fill", "bi-heart");
            } else {
                // Error or not logged in: do nothing or revert state if needed
                console.warn("Favorite toggle failed or user not logged in.");
            }
    
            this.disabled = false;
        });
    });

    document.querySelectorAll(".filtered-btn").forEach(button => {
        button.addEventListener("click", function () {
            const filter = this.getAttribute("data-filter");
            window.location.href = `/recipes?page=1&filter=${filter}`;
        });
    });
    
};