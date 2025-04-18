console.log("Menus JS loaded");
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