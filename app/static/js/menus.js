// This file contains the JavaScript code for the menus page
// It handles the slider functionality and the display of recipes and shopping info

// Function to add the start section of the menu
function addStartMenu(menuName) {
    // Get the container for the menu and clear its content
    const section = document.getElementById("menu-container");
    section.innerHTML = "";

    // Create the start section HTML with the menu name
    const startSectionHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
        <path fill="#FFF" fill-opacity="1" d="M0,192L48,165.3C96,139,192,85,288,101.3C384,117,480,203,576,218.7C672,235,768,181,864,181.3C960,181,1056,235,1152,218.7C1248,203,1344,117,1392,74.7L1440,32L1440,0L1392,0C1344,0,1248,0,1152,0C1056,0,960,0,864,0C768,0,672,0,576,0C480,0,384,0,288,0C192,0,96,0,48,0L0,0Z"></path>
    </svg>
    <div class="menu-title text-center pb-3">
        <h1 id="menu-name-heading" class="display-2">${menuName} Menu</h1>
        <div class="heading-line mb-5"></div>
        <span class="text-secondary my-3">Click on the recipe to start creating!</span>
    </div>
    <div id="menu-content" class="row d-flex flex-row flex-wrap justify-content-evenly week-cards align-items-stretch mx-auto mt-3 pb-3">
    `

    // Add the section inside a container
    section.innerHTML = startSectionHTML;
}

// Function to display the recipes for each day of the week
function displayMenuRecipes(recipesByDay) {
    // Get the container for the menu and clear its content
    const container = document.getElementById("menu-content");
    container.innerHTML = "";

    // Set up the colors for the cards and the order of the days
    const colors = [
        'bg-success text-white',
        'bg-primary text-secondary',
        'bg-secondary text-white'
    ];

    let colorIndex = 0;

    const orderedDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

    // Create cards for each day of the week
    for (const day of orderedDays) {
        const meals = recipesByDay[day];
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
                    </div>
                </div>
            </div>
        `;

        // Insert the card into the container
        container.insertAdjacentHTML("beforeend", card);
    }
}

// Helper to generate each accordion item
function createAccordionItem(id, title, content) {
    if (!content) return '';  // Skip if no content
    const isShoppingList = title.includes("Shopping List");

    return `
        <div class="accordion-item">
            <h2 class="accordion-header" id="heading-${id}">
                <button class="accordion-button p-3 text-secondary collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${id}" aria-expanded="false" aria-controls="collapse-${id}">
                    ${title}
                </button>
            </h2>
            <div id="collapse-${id}" class="accordion-collapse collapse" aria-labelledby="heading-${id}" data-bs-parent="#shopping-info-accordion">
                <div class="accordion-body position-relative">
                    ${isShoppingList ? `
                    <button class="btn btn-sm btn-outline-primary position-relative top-0 m-2" onclick="copyToClipboard('content-${id}', event)">
                        <i class="bi bi-clipboard"></i> Copy
                    </button>
                ` : ''}
                    <div id="content-${id}" class="bg-light p-3 rounded overflow-auto" style="max-height: 400px;">${content}</div>
                </div>
            </div>
        </div>
    `;
}

// Function to display the shopping information
function displayShoppingInfo(info) {
    const shoppingInfoContainer = document.getElementById("shopping-info-container");

    if (!shoppingInfoContainer) {
        console.warn("No shopping info container found.");
        return;
    }

    // Create the accordion item HTML
    const accordionHTML = `
    <div class="accordion my-5" id="shopping-info-accordion">
        ${createAccordionItem("shoppinglist", "🛒 Shopping List", renderStructuredShoppingList(info.shopping_list))}
        ${createAccordionItem("preparations", "🧑‍🍳 Preparations", renderShoppingText(info.preparations, "paragraphs"))}
        ${createAccordionItem("meatmarinades", "🥩 Meat Marinades", renderStructuredShoppingList(info.meat_marinades))}
        ${createAccordionItem("dressings", "🥗 Salad Dressings", renderStructuredShoppingList(info.dressings))}
        ${createAccordionItem("rulesandtips", "💡 Rules and Tips", renderShoppingText(info.rules_and_tips, "paragraphs"))}
    </div>
    `;

    shoppingInfoContainer.innerHTML = accordionHTML;
}

// Function to turn shopping info into a list
function renderShoppingText(lines, mode = "list") {
    if (mode === "list") {
        return `
          <ul class="list-group list-group-flush row d-flex flex-row flex-wrap justify-content-start">
            ${lines.map(line => `<li class="list-group-item col-md-4">${line}</li>`).join('')}
          </ul>
        `;
    } else if (mode === "paragraphs") {
        return lines.map(line => `<p>${line}</p>`).join('');
    }
}

// Function to render structured shopping list
function renderStructuredShoppingList(structuredList) {
    return structuredList.map(group => `
      <h3 class="my-3 ms-3 fs-5 fw-bold text-secondary">${group.category}</h3>
      ${renderShoppingText(group.items, "list")}
    `).join('');
}

// Function to copy text to clipboard and show a tooltip
function copyToClipboard(elementId, event) {
    // Get the text from the specified element
    const text = document.getElementById(elementId)?.innerText;
    const button = event.currentTarget;

    if (text) {
        navigator.clipboard.writeText(text).then(() => {
            showTooltip(button, "Copied!");
        }).catch(err => {
            console.error("Failed to copy text:", err);
        });
    }
}

// Show floating tooltip near the button
function showTooltip(button, message) {
    // Create tooltip element
    const tooltip = document.createElement("div");
    tooltip.className = "copy-tooltip";
    tooltip.innerText = message;

    // Position the tooltip
    const rect = button.getBoundingClientRect();
    tooltip.style.position = "fixed";
    tooltip.style.top = `${rect.top - 30}px`;
    tooltip.style.left = `${rect.left + rect.width / 2}px`;
    tooltip.style.transform = "translateX(-50%)";
    tooltip.style.background = "#f7801c";
    tooltip.style.color = "white";
    tooltip.style.padding = "5px 10px";
    tooltip.style.borderRadius = "5px";
    tooltip.style.fontSize = "0.8rem";
    tooltip.style.zIndex = "1055";
    tooltip.style.opacity = "0";
    tooltip.style.transition = "opacity 0.3s ease";

    document.body.appendChild(tooltip);

    // Fade in
    requestAnimationFrame(() => {
        tooltip.style.opacity = "1";
    });

    // After 1.5 seconds, fade out and remove
    setTimeout(() => {
        tooltip.style.opacity = "0";
        setTimeout(() => {
            tooltip.remove();
        }, 300);
    }, 1500);
}

// Function to add a menu when it is selected from the slider
async function addMenu(menuName) {
    addStartMenu(menuName);
    // Fetch the menu data from the server to display it in the menu container
    try {
        const response = await fetch(`/menus/${menuName}`);
        const data = await response.json();

        if (response.ok) {
            const { recipes_by_day, shopping_info } = data;

            displayMenuRecipes(recipes_by_day);
            // Create the end section HTML with container for the the shopping info
            const container = document.getElementById("menu-container");
            const endSectionHTML = `
                </div>
                <div id="shopping-info-container" class="container"></div>
            `;
            container.insertAdjacentHTML("beforeend", endSectionHTML);

            if (shopping_info) {
                displayShoppingInfo(shopping_info);
            }
        } else {
            console.error(data.error);
        }
    } catch (error) {
        console.error("Error loading menu:", error);
    }
}

if (window.location.pathname.startsWith("/menus")) {
    document.addEventListener("DOMContentLoaded", function () {
        // Set up the slider functionality
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

        // Check if a menu name is stored in sessionStorage
        let selectedMenu = sessionStorage.getItem("selectedMenu");

        // If not in sessionStorage, check URL query parameter
        if (!selectedMenu) {
            const urlParams = new URLSearchParams(window.location.search);
            selectedMenu = urlParams.get("menu");
        }
        // If a menu name is found, add the menu
        if (selectedMenu) {
            addMenu(selectedMenu);
            sessionStorage.removeItem("selectedMenu");
        }
    });
};