console.log("Menus JS loaded");

async function loadMenu(menuName) {
    try {
        const response = await fetch(`/menus/${menuName}`);
        const data = await response.json();

        const container = document.getElementById("menu-content");
        container.innerHTML = "";

        const colors = [
            'bg-success text-white',
            'bg-primary text-secondary',
            'bg-secondary text-white'
        ];

        let colorIndex = 0;

        const orderedDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

        for (const day of orderedDays) {
            const meals = data[day];
            if (!meals) continue;

            const dayLower = day.toLowerCase();
            const colorClass = colors[colorIndex % colors.length];
            colorIndex++;

            const card = `
                <div class="col-xs-10 col-s-8 col-sm-7 col-md-6 col-lg-4 d-flex flex-column mt-5 h-100">
                    <div class="card-wrapper h-100">
                        <div id="${dayLower}" class="day-of-week-card d-flex flex-column justify-content-between p-0 h-100">
                            <div class="week-card-header w-100 ${colorClass}">
                                <h2>${day}</h2>
                            </div>
                            <div class="week-card-content">
                                ${['Breakfast', 'Lunch', 'Dinner', 'Dessert'].map(meal => {
                                    const recipe = meals[meal]?.[0];
                                    const title = recipe?.title || '-';
                                    const url = recipe ? `/recipe/${recipe.id}` : '#';
                                    return `
                                    <span>${meal}</span>
                                    <a href="${url}">${title}</a>
                                    `;
                                }).join('')}
                                <span></span>
                                <p></p>
                            </div>
                            <div class="week-card-btn d-flex justify-content-center">
                                <button class="btn btn-outline-primary mx-auto my-3" data-bs-toggle="tooltip" data-bs-placement="bottom"
                                data-bs-custom-class="custom-tooltip" data-bs-title="Add ingredients to the shopping list">
                                <i class="bi bi-bag-plus-fill"></i>&nbsp; Add ingredients</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML("beforeend", card);
        }
    } catch (err) {
        console.error("Failed to load menu:", err);
    }
}

function addStartMenu(menuName){
    const section = document.getElementById("menu-container");
        section.innerHTML = "";
        
        const startSectionHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
            <path fill="#FFF" fill-opacity="1" d="M0,192L48,165.3C96,139,192,85,288,101.3C384,117,480,203,576,218.7C672,235,768,181,864,181.3C960,181,1056,235,1152,218.7C1248,203,1344,117,1392,74.7L1440,32L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"></path>
        </svg>
        <div class="menu-title text-center pb-3">
            <h1 id="menu-name-heading">${menuName} Menu</h1>
            <span class="text-secondary my-3">Click on the recipe to start creating!</span>
        </div>
        <div id="menu-content" class="row d-flex flex-row flex-wrap justify-content-evenly week-cards align-items-stretch mx-auto mt-3 pb-3">
        `

        // Add the section inside a container
        section.innerHTML = startSectionHTML;
}

function addMenu(menuName){
    addStartMenu(menuName);
    loadMenu(menuName);

    const container = document.getElementById("menu-container");

    const endSectionHTML = `
        </div>
        <div class="generate-shopping-list text-center my-5">
            <button type="button" class="btn btn-lg btn-primary text-secondary mx-auto my-4" data-bs-toggle="tooltip" data-bs-placement="bottom"
            data-bs-custom-class="custom-tooltip" data-bs-title="Add ingredients for the whole week"><i class="bi bi-bag-plus-fill"></i>&nbsp;  Add ingredients for the week</button>
        </div>
    `

    container.insertAdjacentHTML("beforeend", endSectionHTML);
}

if (window.location.pathname.startsWith("/menus")) {
    document.addEventListener("DOMContentLoaded", function () {
        const next = document.querySelector(".next");
        const prev = document.querySelector(".prev");
        const slider = document.querySelector(".slider");

        next.addEventListener("click", function () {
            const slides = document.querySelectorAll(".slides");
            slider.appendChild(slides[0]);
        });

        prev.addEventListener("click", function () {
            const slides = document.querySelectorAll(".slides");
            slider.prepend(slides[slides.length - 1]);
        });
    });
};