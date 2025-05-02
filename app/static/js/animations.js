// This file contains the JavaScript code for various animations used in the web application.

// Button shine animation
function btnShine() {
  const button = document.querySelector(".shining-btn");
  const text = button.textContent;
  button.innerHTML = "";

  for (let char of text) {
    const span = document.createElement("span");
    span.textContent = char === "  " ? "\u00A0" : char;
    button.appendChild(span);
  }

  const spans = button.querySelectorAll("span");

  button.addEventListener("mouseenter", () => {
    spans.forEach((span, index) => {
      setTimeout(() => {
        span.classList.add("hover");
      }, index * 50);
    });
  });

  button.addEventListener("mouseleave", () => {
    spans.forEach((span, index) => {
      setTimeout(() => {
        span.classList.remove("hover");
      }, index * 50);
    });
  });
}

// Snowfall animation
function letItSnow() {
  const container = document.querySelector("#container");
  const count = 50;

  for (var i = 0; i < count; i++) {
    const leftSnow = Math.floor(Math.random() * container.clientWidth);
    const topSnow = Math.floor(Math.random() * container.clientHeight);
    const widthSnow = Math.floor(Math.random() * count);
    const timeSnow = Math.floor((Math.random() * count) / 10 + 5);
    const blurSnow = Math.floor((Math.random() * count) / 2.5);
    const div = document.createElement("div");
    div.classList.add("snow");
    div.style.left = leftSnow + "px";
    div.style.top = topSnow + "px";
    div.style.width = widthSnow + "px";
    div.style.height = widthSnow + "px";
    div.style.animationDuration = timeSnow + "s";
    div.style.filter = "blur(" + blurSnow + "px)";
    container.appendChild(div);
  }
}
