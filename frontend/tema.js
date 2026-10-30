const THEME_STORAGE_KEY = "cockpit-theme";
const rootElement = document.documentElement;
const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);

rootElement.dataset.theme = savedTheme === "light" ? "light" : "dark";

function updateThemeButton() {
    const button = document.getElementById("theme-toggle");
    if (!button) {
        return;
    }

    const nextTheme = rootElement.dataset.theme === "dark" ? "light" : "dark";
    const label = nextTheme === "light" ? "☀️ Ativar modo claro" : "🌙 Ativar modo escuro";
    button.textContent = label;
    button.setAttribute("aria-label", label);
    button.setAttribute("title", label);
}

window.toggleTheme = function() {
    const nextTheme = rootElement.dataset.theme === "dark" ? "light" : "dark";
    rootElement.dataset.theme = nextTheme;
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    updateThemeButton();
};

document.addEventListener("DOMContentLoaded", updateThemeButton);
