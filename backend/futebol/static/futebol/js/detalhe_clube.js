"use strict";
document.querySelectorAll(".club-detail-crest").forEach((image) => {
    const hideBrokenCrest = () => { image.hidden = true; };
    image.addEventListener("error", hideBrokenCrest);
    if (image.complete && image.naturalWidth === 0) hideBrokenCrest();
});
