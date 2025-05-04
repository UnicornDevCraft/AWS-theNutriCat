// Navbar logic for all pages exept authorization

if (!window.location.pathname.startsWith("/auth/")) {
    document.addEventListener("DOMContentLoaded", () => {
        // Declaring variables for navigation
        const offcanvasElement = document.getElementById("offcanvasNavbar");
        const links = document.querySelectorAll(".offcanvas a");
        const bsOffcanvas = new bootstrap.Offcanvas(offcanvasElement);

        // Closing menu after click on the link
        links.forEach((link) => {
            link.addEventListener('click', () => {
                links.forEach((link) => { link.classList.remove('active') });
                link.classList.add('active');
                bsOffcanvas.hide();
            });
        });

        // Setting up tooltips on navigation
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

        // Notifications configuration
        let toasts = document.querySelectorAll(".toast");
        toasts.forEach((toast) => {
            toast.timeOut = setTimeout(() => toast.remove(), 5500);
        });
    });
}

// Load categories when modal opens
const searchModal = document.getElementById('searchModal');
if (searchModal) {
    searchModal.addEventListener('show.bs.modal', () => {
        const searchInput = document.querySelector("#searchModal input[type='search']");
        const recipeUrlPrefix = document.getElementById("recipe-id-url").value;
        const menusApiUrl = document.getElementById("menus-api-url").value;
        const recipeAPIUrl = document.getElementById("recipes-api-url").value;
        const searchButton = document.getElementById("search-button");

        const categoriesContainer = document.getElementById("search-categories");
        categoriesContainer.innerHTML = ""; // clear on each open
        fetch('/menus/categories')
            .then(res => res.json())
            .then(categories => {
                categories.forEach(category => {
                    const card = `
                        <div class="col-6 col-sm-4 col-md-3">
                            <a href="#" data-category="${category.name}" class="text-decoration-none menu-category-link">
                                <div class="card h-100 text-center">
                                    <img src="${category.image_url}" class="card-img-top" alt="${category.name}">
                                    <div class="card-body p-2">
                                        <h5 class="card-title">${category.name}</h5>
                                    </div>
                                </div>
                            </a>
                        </div>`;
                    categoriesContainer.insertAdjacentHTML("beforeend", card);
                });
            });

        // Delegate click event after categories load
        categoriesContainer.addEventListener("click", (e) => {
            const link = e.target.closest(".menu-category-link");
            if (!link) return;

            e.preventDefault(); // Stop default navigation

            const category = link.dataset.category;
            sessionStorage.setItem("selectedMenu", category);
            // Close modal and redirect
            const bsModal = bootstrap.Modal.getInstance(searchModal);
            if (bsModal) bsModal.hide();
            //window.location.href = `${menusApiUrl}#menu-container`;
            window.location.href = `${menusApiUrl}?menu=${encodeURIComponent(category)}#menu-container`;

        });

        // Search input event listener for suggestions
        const suggestionsList = document.getElementById('searchSuggestions');
        searchInput.addEventListener('input', async function () {
            const query = searchInput.value.trim();
            if (query.length < 2) {
                suggestionsList.style.display = 'none';
                return;
            }

            try {
                let response = await fetch('/search?q=' + encodeURIComponent(query));
                let recipes = await response.json();

                if (recipes.length === 0) {
                    suggestionsList.style.display = 'none';
                    return;
                }

                suggestionsList.innerHTML = '';

                for (let recipe of recipes) {
                    const item = document.createElement('li');
                    item.className = 'list-group-item list-group-item-action d-flex align-items-center gap-2';

                    item.innerHTML = `
                        ${recipe.thumbnail ? `<img src="${recipe.thumbnail}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:4px;">` : ''}
                        <span>${recipe.title}</span>
                    `;

                    item.addEventListener('click', () => {
                        window.location.href = `${recipeUrlPrefix}${recipe.id}`;
                    });

                    suggestionsList.appendChild(item);
                }

                suggestionsList.style.display = 'block';

            } catch (error) {
                console.error('Error fetching search suggestions:', error);
            }
        });

        // Hide suggestions if clicked outside
        document.addEventListener('click', function (event) {
            if (!searchInput.contains(event.target) && !suggestionsList.contains(event.target)) {
                suggestionsList.style.display = 'none';
            }
        });

        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query.length >= 2) {
                window.location.href = `${recipeAPIUrl}?page=1&search=${encodeURIComponent(query)}`;
            }
        });
    });
}




