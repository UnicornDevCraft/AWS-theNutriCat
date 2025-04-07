
if (!window.location.pathname.startsWith("/auth/")) {
    document.addEventListener("DOMContentLoaded", () => {
        var TrandingSlider = new Swiper('.favorite-slider', {
            effect: 'coverflow',
            grabCursor: true,
            centeredSlides: true,
            loop: true,
            slidesPerView: 'auto',
            coverflowEffect: {
            rotate: 0,
            stretch: 0,
            depth: 100,
            modifier: 2.5,
            },
            pagination: {
            el: '.swiper-pagination',
            clickable: true,
            },
            navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
            }
        });

        const ratings = document.querySelectorAll(".dish-rating");

        ratings.forEach((rating) => {
            const ratingValue = parseFloat(rating.querySelector(".rating-value").textContent);
            const stars = rating.querySelectorAll(".star");

            stars.forEach((star, index) => {
            if (index < Math.floor(ratingValue)) {
                // Full star
                star.style.color = "gold";
            } else if (index < Math.ceil(ratingValue)) {
                // Partial star
                star.setAttribute("name", "star-half-outline")
                star.style.color = "gold";
            } else {
                star.style.color = "#ced4da";
            }
            });
        });

    });
};