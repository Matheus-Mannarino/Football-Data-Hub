"use strict";
// O nome do clube permanece disponível se o servidor do escudo falhar.
document.querySelectorAll(".standings-crest").forEach((image) => {
    const hideBrokenCrest = () => { image.hidden = true; };
    image.addEventListener("error", hideBrokenCrest);
    if (image.complete && image.naturalWidth === 0) hideBrokenCrest();
});
