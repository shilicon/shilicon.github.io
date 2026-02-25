(function () {
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");
  var stored = localStorage.getItem("theme");
  var prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;

  function setTheme(mode) {
    if (mode) {
      root.setAttribute("data-theme", mode);
      localStorage.setItem("theme", mode);
    } else {
      root.removeAttribute("data-theme");
      localStorage.removeItem("theme");
    }
    if (toggle) {
      var current = root.getAttribute("data-theme") || (prefersDark ? "dark" : "light");
      toggle.setAttribute("aria-pressed", current === "dark");
      toggle.textContent = current === "dark" ? "Light mode" : "Dark mode";
    }
  }

  if (stored) {
    setTheme(stored);
  } else {
    setTheme(prefersDark ? "dark" : "light");
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") || (prefersDark ? "dark" : "light");
      setTheme(current === "dark" ? "light" : "dark");
    });
  }

  var navLinks = document.querySelectorAll(".nav a");
  var path = window.location.pathname;
  var isHome = path === "/" || path === "/index.html";
  if (path === "/") {
    path = "/index.html";
  }
  navLinks.forEach(function (link) {
    var linkPath = link.getAttribute("href");
    if (linkPath === "/" && isHome) {
      link.classList.add("active");
      return;
    }
    if (linkPath && linkPath !== "#" && (path === linkPath || path === linkPath + "index.html")) {
      link.classList.add("active");
    }
  });
})();
