// Navbar logic for all pages exept authorization
console.log("Navbar JS loaded");
if (!window.location.pathname.startsWith("/auth/")) {
    document.addEventListener("DOMContentLoaded", () => {
      // Declaring variables for navigation
      const offcanvasElement = document.getElementById("offcanvasNavbar");
      const links = document.querySelectorAll(".offcanvas a");
      const bsOffcanvas = new bootstrap.Offcanvas(offcanvasElement);
    /* let searchBtn = document.querySelector('.searchBtn');
    let closeBtn = document.querySelector('.closeBtn');
    let searchBox = document.querySelector('.searchBox');
    let navigation = document.querySelector('.navigation');
    let menuToggle = document.querySelector('.menuToggle');
    let nav = document.querySelector('nav');
    let dropnav = document.querySelector('#navbarNav');
    

    // Setting up search button
    searchBtn.addEventListener('click', () => {
        searchBox.classList.add('active');
        closeBtn.classList.add('active');
        searchBtn.classList.add('active');
        menuToggle.classList.add('hide');
        nav.classList.remove('open');
        navigation.classList.add('hide');
    });

    // Setting up menu button for small screens
    menuToggle.addEventListener('click', () => {
        nav.classList.toggle('open');
        searchBox.classList.remove('active');
        closeBtn.classList.remove('active');
        searchBtn.classList.remove('active');
    }); */

    // Toggle Search Box
    /* document.querySelector('#searchToggle').addEventListener("click", () => {
        document.querySelector('.searchBox').classList.toggle("d-none");
    }); */

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

function navigateTo(page) {
    const toURL = document.getElementById(`${page}-url`).value;
    window.location.href = toURL;
}
 
  

  
  