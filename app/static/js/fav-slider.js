async function toggleFavorite(recipeId) {
    try {
        const response = await fetch(`/toggle_favorite/${recipeId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });

        if (response.status === 401) {
            console.warn("User is not logged in.");
            alert("Please log in to add favorites!");
            return;
        }

        const data = await response.json();
        if (data.success) {
            if (data.favorite){
                console.log("Recipe added to favorites!", data.favorite);
                return (data.favorite);
            } else {
                console.log("Recipe removed from favorites!", data.favorite);
                return (data.favorite);
            }
            console.log("Favorite toggled successfully!", data);
        } else {
            console.error("Error toggling favorite:", data.error);
        }
    } catch (error) {
        console.error("Request failed:", error);
    }
}


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

        document.querySelectorAll(".favorite-btn").forEach(button => {
            button.addEventListener("click", function () {
                const recipeId = this.getAttribute("data-recipe-id");
                const icon = this.querySelector(".heart-icon");
                const isFavorite = icon.getAttribute("name") === "heart";
                console.log("Recipe ID:", recipeId);
                console.log("Is favorite:", isFavorite);
                console.log(icon.getAttribute("name"));
    
                // Toggle icon state
                icon.setAttribute("name", isFavorite ? "heart-outline" : "heart");
    
                // Send request to backend
                if (toggleFavorite(recipeId) === true) {
                    icon.setAttribute("name", "heart");
                    icon.classList.replace("bi-heart", "bi-heart-fill");
                } else {
                    icon.setAttribute("name", "heart-outline");
                    icon.classList.replace("bi-heart-fill", "bi-heart");
                }
            });
        });
    });
};