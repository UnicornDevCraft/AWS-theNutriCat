// This script handles the fetching and displaying of recipes, as well as the filtering and sorting functionality.

// This function fetches recipes from the server and updates the UI accordingly.
function fetchRecipes(page = 1, filter = "", sort = "", search = "") {
    const apiUrl = document.getElementById("recipes-api-url").value;
    let queryUrl = `${apiUrl}?page=${page}`;

    if (search) queryUrl += `&search=${search}`;
    if (filter) queryUrl += `&filter=${filter}`;
    if (sort) queryUrl += `&sort=${sort}`;

    fetch(queryUrl, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
        .then(response => {
            if (!response.ok) throw new Error("Failed to fetch recipes");
            return response.json();
        })
        .then(data => {
            const container = document.getElementById("recipes-container");
            container.innerHTML = "";

            if (data.recipes.length === 0) {
                container.innerHTML = `<p class="text-center mx-auto">No recipes found.</p>`;
            } else {
                data.recipes.forEach(recipe => {
                    container.innerHTML += `
                    <div class="col recipe-card">
                        <div class="card shadow-sm rounded-5 mx-auto">
                            <img src="${recipe.compressed_img_URL || recipe.quality_img_URL || '/static/img/recipes/placeholder-image.jpeg'}" alt="${recipe.title}" data-recipe-id="${recipe.id}" class="recipe-img">
                            <div class="card-body">
                                <h3 class="card-header text-center"><a href="#" class="text-secondary fs-6 recipe-link" data-recipe-id="{{ recipe.id }}">${recipe.title.charAt(0).toUpperCase() + recipe.title.slice(1).toLowerCase()}</a></h3>
                                <div class="d-flex justify-content-between align-items-center mt-3">
                                ${data.user ? `
                                    <div class="text-end mt-2">
                                        <button class="favorite-btn" data-recipe-id="${recipe.id}" aria-label="Add or remove from favorites">
                                            ${recipe.favorite ? `
                                                <i class="bi bi-heart-fill heart-icon" data-icon="heart" data-bs-toggle="tooltip" data-bs-placement="bottom"
                                                data-bs-custom-class="custom-tooltip" data-bs-title="Remove from favorites"></i>
                                            ` : `
                                                <i class="bi bi-heart heart-icon" data-icon="heart-outline" data-bs-toggle="tooltip" data-bs-placement="bottom"
                                                data-bs-custom-class="custom-tooltip" data-bs-title="Add to favorites"></i>
                                            `}
                                        </button>
                                    </div>
                                    ` : ''}
                                    <div class="cook-time d-flex justify-content-center align-items-center">
                                        &nbsp;<ion-icon name="time-outline"></ion-icon>
                                        &nbsp; <span class="text-white">${recipe.prep_time + recipe.cook_time}</span>&nbsp; 
                                    </div>
                                    <div class="recipe-tags d-flex justify-content-start align-items-center">
                                        ${recipe.tags.map(tag => `<button class="btn btn-sm btn-outline-secondary rounded-3 mx-1 filter-btn" data-filter="${tag.name}">${tag.name}</button>`).join('')}
                                    </div>
                                    <button type="button" class="btn btn-m btn-success rounded-4 text-white make" data-recipe-id="${recipe.id}">Make</button>
                                </div>
                            </div>
                        </div>
                    </div>`;
                });

                // Add 'active' class to all buttons with the same 'data-filter'
                document.querySelectorAll(`[data-filter="${filter}"]`).forEach(btn => {
                    btn.classList.add("active");
                });
            }
            attachFavoriteListeners();
            updatePagination(data.total_pages, page, filter, sort, search);
        })
        .catch(error => console.error("Error fetching recipes:", error));
};

// This function attaches event listeners to the favorite buttons and recipe images.
function attachFavoriteListeners() {
    document.querySelectorAll(".favorite-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const recipeId = this.getAttribute("data-recipe-id");
            const icon = this.querySelector(".heart-icon");
            this.disabled = true;

            const isNowFavorite = await toggleFavorite(recipeId);

            try {
                // Update the icon and tooltip based on the favorite status
                if (isNowFavorite === true) {
                    icon.setAttribute("data-icon", "heart");
                    icon.setAttribute("data-bs-title", "Remove from favorites");
                    icon.classList.replace("bi-heart", "bi-heart-fill");
                } else if (isNowFavorite === false) {
                    icon.setAttribute("data-icon", "heart-outline");
                    icon.setAttribute("data-bs-title", "Add to favorites");
                    icon.classList.replace("bi-heart-fill", "bi-heart");
                } else {
                    // Error or not logged in do nothing
                    console.warn("Favorite toggle failed or user not logged in.");
                }

                this.disabled = false;

            } catch (err) {
                console.error("Favorite toggle failed or user not logged in.", err);
                showAlertMessage("Error toggling favorite", "error");
            }
        });
    });
    // Attach click event to recipe images and links for redirect
    document.querySelectorAll(".make, .recipe-img, .recipe-link").forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const recipeId = this.getAttribute("data-recipe-id");
            window.location.href = `/recipe/${recipeId}`;
        });
    });
}

// This function updates the pagination UI based on the total number of pages and the current page.
function updatePagination(totalPages, currentPage = 1, filter = "", sort = "", search = "") {
    const paginationContainer = document.querySelector(".pagination");
    paginationContainer.innerHTML = "";

    if (currentPage > 1) {
        paginationContainer.innerHTML += `
            <li class="page-item">
                <a class="page-link page-link-btn" href="#" onclick="fetchRecipes(${currentPage - 1}, '${filter}', '${sort}', '${search}')">
                    <i class="bi bi-chevron-bar-left"></i>
                </a>
            </li>`;
    }

    for (let p = 1; p <= totalPages; p++) {
        paginationContainer.innerHTML += `
            <li class="page-item ${p === currentPage ? 'active' : ''}">
                <a class="page-link page-link-btn" href="#" onclick="fetchRecipes(${p}, '${filter}', '${sort}', '${search}')">${p}</a>
            </li>`;
    }

    if (currentPage < totalPages) {
        paginationContainer.innerHTML += `
            <li class="page-item">
                <a class="page-link page-link-btn" href="#" onclick="fetchRecipes(${currentPage + 1}, '${filter}', '${sort}', '${search}')">
                    <i class="bi bi-chevron-bar-right"></i>
                </a>
            </li>`;
    }
};

// This function handles the search
function searchRecipes(filter = "", sort = "") {
    const searchQuery = document.getElementById('searching-input').value.trim();
    const encodedSearch = encodeURIComponent(searchQuery);

    fetchRecipes(1, filter, sort, encodedSearch);
};

// This function toggles the favorite status of a recipe and updates the UI
async function toggleFavorite(recipeId) {
    try {
        const response = await fetch(`/toggle_favorite/${recipeId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
        });

        if (response.status === 401) {
            alert("Please log in to add favorites!");
            return null;
        }

        const data = await response.json();

        if (data.success) {
            showAlertMessage(data.message, "success");
            return data.favorite;
        } else {
            showAlertMessage(data.message, "error");
            console.error("Error toggling favorite:", data.error);
            return null;
        }
    } catch (error) {
        console.error("Request failed:", error);
        return null;
    }
}

// This function shows an alert message in the flash container
function showAlertMessage(message, type = "info") {
    const container = document.getElementById("flash-container");

    if (!container) {
        console.warn("Flash container not found.");
        return;
    }

    const alert = document.createElement("div");
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = "alert";
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.appendChild(alert);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove("show");
        alert.classList.add("fade");
        setTimeout(() => alert.remove(), 500); // remove after fade out
    }, 5000);
}

// Handle filter and sorting on the recipes page
if (window.location.pathname.startsWith("/recipes")) {
    document.addEventListener("DOMContentLoaded", function () {
        let currentFilter = "";
        let currentSort = "";
        let currentSearch = "";
        const urlParams = new URLSearchParams(window.location.search);
        const activeFilter = urlParams.get('filter');
        const searchInput = document.getElementById("searching-input");
        const searchForm = document.getElementById("search-form");

        if (searchInput && searchForm) {
            searchInput.addEventListener("keypress", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    searchRecipes(currentFilter, currentSort);
                }
            });
        }

        if (activeFilter) {
            document.querySelectorAll('.filter-btn').forEach(button => {
                const filter = button.getAttribute('data-filter');
                if (filter === activeFilter) {
                    button.classList.add('active');
                }
            });
        }
        // Search button event listener
        document.getElementById("search-btn").addEventListener("click", function (e) {
            e.preventDefault();
            searchRecipes(currentFilter, currentSort);
        });
        // Filter button event listener
        document.addEventListener("click", function (e) {
            if (e.target.classList.contains("filter-btn") || e.target.classList.contains("filter-option")) {
                e.preventDefault();

                // Remove 'active' class from all filter buttons
                document.querySelectorAll(".filter-option, .filter-btn").forEach(btn => {
                    btn.classList.remove("active");
                });

                let selectedFilter = e.target.getAttribute("data-filter");

                // Add 'active' class to all buttons with the same filter
                document.querySelectorAll(`[data-filter="${selectedFilter}"]`).forEach(btn => {
                    btn.classList.add("active");
                });

                // Update filter and fetch new results
                currentFilter = selectedFilter;
                fetchRecipes(1, currentFilter, currentSort, currentSearch);
            }
        });
        // Sort button event listener
        document.getElementById("sort-btn").addEventListener("click", function () {
            let currentSort = this.getAttribute("data-sort");

            // Toggle sorting: default → asc → desc → default
            if (currentSort === "default") {
                currentSort = "asc";
            } else if (currentSort === "asc") {
                currentSort = "desc";
            } else {
                currentSort = "default";
            }

            // Update button attribute
            this.setAttribute("data-sort", currentSort);

            // Update button icon and text
            this.innerHTML = `Sort by the title&nbsp;
                <i class="bi ${currentSort === "asc" ? "bi-sort-alpha-down" : currentSort === "desc" ? "bi-sort-alpha-down-alt" : "bi-filter"}"></i>`;

            // Call fetchRecipes with the new sorting order
            fetchRecipes(1, currentFilter, currentSort, currentSearch);
        });
        
        attachFavoriteListeners();
    });
};
