"use strict";
// Preserva a identificação do clube se o escudo externo não carregar.
document.querySelectorAll(".fixture-crest").forEach((image) => {
    const hideBrokenCrest = () => { image.hidden = true; };
    image.addEventListener("error", hideBrokenCrest);
    if (image.complete && image.naturalWidth === 0) hideBrokenCrest();
});
