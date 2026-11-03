"use strict";
// Mantém o nome do clube visível quando o escudo externo não carrega.
document.querySelectorAll(".home .club-crest").forEach((image) => {
    function hideBrokenCrest() { image.hidden = true; }
    image.addEventListener("error", hideBrokenCrest);
    if (image.complete && image.naturalWidth === 0) hideBrokenCrest();
});
