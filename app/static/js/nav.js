// Navbar logic for all pages exept authorization
console.log("Navbar JS loaded");

if (!window.location.pathname.startsWith("/auth/")) {
    document.addEventListener("DOMContentLoaded", () => {
        // Declaring variables for navigation
        const offcanvasElement = document.getElementById("offcanvasNavbar");
        const links = document.querySelectorAll(".offcanvas a");
        const bsOffcanvas = new bootstrap.Offcanvas(offcanvasElement);

        // Closing menu after click on the link
        links.forEach((link) => {
            link.addEventListener('click', () => {
                links.forEach((link) => {link.classList.remove('active')});
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
 
  

  
  