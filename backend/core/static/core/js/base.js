"use strict";

const menuButton = document.querySelector(".menu-toggle");
const navigation = document.getElementById("navegacao-principal");

if (menuButton && navigation) {
    const mobile = window.matchMedia("(max-width: 960px)");
    function setOpen(open) {
        menuButton.setAttribute("aria-expanded", String(open));
        navigation.hidden = mobile.matches && !open;
    }
    function syncMenu() {
        menuButton.hidden = !mobile.matches;
        setOpen(false);
    }
    menuButton.addEventListener("click", () => {
        setOpen(menuButton.getAttribute("aria-expanded") !== "true");
    });
    navigation.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && mobile.matches) {
            setOpen(false);
            menuButton.focus();
        }
    });
    navigation.addEventListener("click", (event) => {
        if (event.target.closest("a") && mobile.matches) setOpen(false);
    });
    mobile.addEventListener("change", syncMenu);
    syncMenu();
}
