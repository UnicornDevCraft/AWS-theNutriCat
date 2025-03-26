/* document.addEventListener("DOMContentLoaded", function () {
    const apiUrl = document.getElementById("recipes-api-url").value;

    document.querySelectorAll(".filter-option").forEach(item => {
        item.addEventListener("click", function (e) {
            e.preventDefault();
            const filterValue = this.getAttribute("data-filter");
            fetchRecipes(`${apiUrl}?filter=${filterValue}`);
        });
    });

    document.getElementById("sort-btn").addEventListener("click", function () {
        const currentSort = this.getAttribute("data-sort");
        const newSort = currentSort === "asc" ? "desc" : "asc";
        this.setAttribute("data-sort", newSort);
        this.textContent = `Sort Alphabetically (${newSort === "asc" ? "A-Z" : "Z-A"})`;
        fetchRecipes(`${apiUrl}?sort=${newSort}`);
    });

    document.querySelectorAll(".page-link").forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const page = this.getAttribute("data-page");
            fetchRecipes(`${apiUrl}?page=${page}`);
        });
    });

    function fetchRecipes(queryUrl) {
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

            if (data.length === 0) {
                container.innerHTML = "<p>No recipes found.</p>";
            } else {
                data.forEach(recipe => {
                    container.innerHTML += `
                        <div class="col recipe-card">
                            <div class="card shadow-sm rounded-5 mx-auto">
                                <img src="${recipe.compressed_img_URL || recipe.quality_img_URL || recipe.local_image_path}" alt="${recipe.title}">
                                <div class="card-body">
                                    <h3 class="card-header text-center text-secondary">${recipe.title}</h3>
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

            //updatePagination(data.page, data.total_pages); // Update pagination based on response
        })
        .catch(error => console.error("Error fetching recipes:", error));
    }

    function updatePagination(currentPage, totalPages) {
        const pagination = document.querySelector(".pagination");
        pagination.innerHTML = "";

        if (currentPage > 1) {
            pagination.innerHTML += `<li class="page-item"><a class="page-link page-link-btn" href="#" data-page="${currentPage - 1}"><i class="bi bi-chevron-bar-left"></i></a></li>`;
        }

        for (let i = 1; i <= totalPages; i++) {
            pagination.innerHTML += `<li class="page-item ${i === currentPage ? "active" : ""}"><a class="page-link page-link-btn" href="#" data-page="${i}">${i}</a></li>`;
        }

        if (currentPage < totalPages) {
            pagination.innerHTML += `<li class="page-item"><a class="page-link page-link-btn" href="#" data-page="${currentPage + 1}"><i class="bi bi-chevron-bar-right"></i></a></li>`;
        }
    }
});
 */