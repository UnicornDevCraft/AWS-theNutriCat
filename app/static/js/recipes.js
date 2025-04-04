window.fetchRecipes = function (page = 1, filter = "", sort = "", search = "") {
    const apiUrl = document.getElementById("recipes-api-url").value;
    let queryUrl = `${apiUrl}?page=${page}`;

    if (search) queryUrl += `&search=${search}`;
    if (filter) queryUrl += `&filter=${filter}`;
    if (sort) queryUrl += `&sort=${sort}`;
    console.log("Fetching: ", queryUrl)
    
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
            console.log("Recipes:", data.recipes)
            data.recipes.forEach(recipe => {
                container.innerHTML += `
                    <div class="col recipe-card">
                        <div class="card shadow-sm rounded-5 mx-auto">
                            <img src="${recipe.compressed_img_URL || recipe.quality_img_URL || recipe.local_image_path}" alt="${recipe.title}" data-recipe-id="${ recipe.id }" class="recipe-img">
                            <div class="card-body">
                                <h3 class="card-header text-center"><a href="#" class="text-secondary fs-6 recipe-link" data-recipe-id="{{ recipe.id }}">${recipe.title.charAt(0).toUpperCase() + recipe.title.slice(1).toLowerCase()}</a></h3>
                                <div class="d-flex justify-content-between align-items-center mt-3">
                                    <div class="cook-time d-flex justify-content-center align-items-center">
                                        &nbsp;<ion-icon name="time-outline"></ion-icon>
                                        &nbsp; <span class="text-white">${recipe.prep_time + recipe.cook_time}</span>&nbsp; 
                                    </div>
                                    <div class="recipe-tags d-flex justify-content-start align-items-center">
                                        ${recipe.tags.map(tag => `<button class="btn btn-sm btn-outline-secondary rounded-3 mx-1 filter-btn" data-filter="${ tag.name }">${tag.name}</button>`).join('')}
                                    </div>
                                    <button type="button" class="btn btn-m btn-success rounded-4 text-white make" data-recipe-id="${ recipe.id }">Make</button>
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
        
        updatePagination(data.total_pages, page, filter, sort, search);
    })
    .catch(error => console.error("Error fetching recipes:", error));
};

window.updatePagination = function (totalPages, currentPage = 1, filter = "", sort = "", search = "") {
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

window.searchRecipes = function (filter = "", sort = "") {
    const searchQuery = document.getElementById('search-input').value.trim();
    const encodedSearch = encodeURIComponent(searchQuery);

    console.log("Searching for:", searchQuery);
    fetchRecipes(1, filter, sort, encodedSearch);
};

// Handle filter and sorting
if (window.location.pathname.startsWith("/recipes")) {
    document.addEventListener("DOMContentLoaded", function () {
        let currentFilter = "";
        let currentSort = "";
        let currentSearch = "";

        document.getElementById("search-btn").addEventListener("click", function (e) {
            e.preventDefault();
            searchRecipes(currentFilter, currentSort);
        });

        document.addEventListener("click", function (e) {
            if (e.target.classList.contains("filter-btn") || e.target.classList.contains("filter-option")) {
                e.preventDefault();
                console.log("Clicked on filter:", e.target);
        
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

        document.querySelectorAll(".make, .recipe-img, .recipe-link").forEach(button => {
            button.addEventListener("click", function(e) {
                e.preventDefault();
                const recipeId = this.getAttribute("data-recipe-id");
                window.location.href = `/recipe/${recipeId}`;
            });
        });

    


    });
};
