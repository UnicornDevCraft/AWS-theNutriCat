console.log("Menus JS loaded");

function fetchMenu(menu = ""){
    const apiUrl = document.getElementById("menus-api-url").value;
    let queryUrl = `${apiUrl}?menu=${menu}`;
    console.log("Fetching: ", queryUrl)

    fetch(queryUrl, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to fetch menus");
        return response.json();
    })
    .then(data => {
        const container = document.getElementById("menus-container");
        container.innerHTML = "";

    });
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