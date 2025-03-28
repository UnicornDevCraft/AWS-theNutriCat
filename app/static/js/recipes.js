window.fetchRecipes = function (page = 1, filter = "", sort = "") {
    const apiUrl = document.getElementById("recipes-api-url").value;
    let queryUrl = `${apiUrl}?page=${page}`;

    if (filter) queryUrl += `&filter=${filter}`;
    if (sort) queryUrl += `&sort=${sort}`;
    console.log(queryUrl)
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
            container.innerHTML = "<p>No recipes found.</p>";
        } else {
            data.recipes.forEach(recipe => {
                container.innerHTML += `
                    <div class="col recipe-card">
                        <div class="card shadow-sm rounded-5 mx-auto">
                            <img src="${recipe.compressed_img_URL || recipe.quality_img_URL || recipe.local_image_path}" alt="${recipe.title}">
                            <div class="card-body">
                                <h3 class="card-header text-center text-secondary">${recipe.title.charAt(0).toUpperCase() + recipe.title.slice(1).toLowerCase()}</h3>
                                <div class="d-flex justify-content-between align-items-center mt-3">
                                    <div class="cook-time d-flex justify-content-center align-items-center">
                                        &nbsp;<ion-icon name="time-outline"></ion-icon>
                                        &nbsp; <span class="text-white">${recipe.prep_time + recipe.cook_time}</span>&nbsp; 
                                    </div>
                                    <div class="recipe-tags d-flex justify-content-start align-items-center">
                                        ${recipe.tags.map(tag => `<button class="btn btn-sm btn-outline-secondary rounded-3 mx-1">${tag.name}</button>`).join('')}
                                    </div>
                                    <button type="button" class="btn btn-m btn-success rounded-4 text-white make">Make</button>
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
        }

        updatePagination(data.total_pages, page, filter, sort);
    })
    .catch(error => console.error("Error fetching recipes:", error));
};

window.updatePagination = function (totalPages, currentPage = 1, filter = "", sort = "") {
    const paginationContainer = document.querySelector(".pagination");
    paginationContainer.innerHTML = "";

    if (currentPage > 1) {
        paginationContainer.innerHTML += `
            <li class="page-item">
                <a class="page-link page-link-btn" href="#" onclick="fetchRecipes(${currentPage - 1}, '${filter}', '${sort}')">
                    <i class="bi bi-chevron-bar-left"></i>
                </a>
            </li>`;
    }

    for (let p = 1; p <= totalPages; p++) {
        paginationContainer.innerHTML += `
            <li class="page-item ${p === currentPage ? 'active' : ''}">
                <a class="page-link page-link-btn" href="#" onclick="fetchRecipes(${p}, '${filter}', '${sort}')">${p}</a>
            </li>`;
    }

    if (currentPage < totalPages) {
        paginationContainer.innerHTML += `
            <li class="page-item">
                <a class="page-link page-link-btn" href="#" onclick="fetchRecipes(${currentPage + 1}, '${filter}', '${sort}')">
                    <i class="bi bi-chevron-bar-right"></i>
                </a>
            </li>`;
    }
};

// Handle filter and sorting
document.addEventListener("DOMContentLoaded", function () {
    let currentFilter = "";
    let currentSort = "";

    document.querySelectorAll(".filter-option").forEach(item => {
        item.addEventListener("click", function (e) {
            e.preventDefault();
            currentFilter = this.getAttribute("data-filter");
            fetchRecipes(1, currentFilter, currentSort);
        });
    });

    document.getElementById("sort-btn").addEventListener("click", function () {
        let currentSort = this.getAttribute("data-sort");
        console.log(currentSort)
        // Toggle sorting: default → asc → desc → default
        if (currentSort === "default") {
            currentSort = "asc";
        } else if (currentSort === "asc") {
            currentSort = "desc";
        } else {
            currentSort = "default";  // Reset to original order
        }
        console.log(currentSort)
        // Update button attribute
        this.setAttribute("data-sort", currentSort);

        // Update button icon and text
        this.innerHTML = `Sort by the title&nbsp;
            <i class="bi ${currentSort === "asc" ? "bi-sort-alpha-down" : currentSort === "desc" ? "bi-sort-alpha-down-alt" : "bi-filter"}"></i>`;
        console.log(currentSort)
        // Call fetchRecipes with the new sorting order
        fetchRecipes(1, currentFilter, currentSort);
    });

});
