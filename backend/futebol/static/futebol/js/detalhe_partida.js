"use strict";
document.querySelectorAll(".scoreboard-crest").forEach((image) => {
    const hideBrokenCrest = () => { image.hidden = true; };
    image.addEventListener("error", hideBrokenCrest);
    if (image.complete && image.naturalWidth === 0) hideBrokenCrest();
});
