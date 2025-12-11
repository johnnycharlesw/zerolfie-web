"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
(() => {
    // Automodernization script: Fixes old web content to use modern standards BTS so old websites still function
    // Replace blink elements with modern versions
    document.querySelectorAll('blink').forEach(element => {
        let modernVersionOfElement = document.createElement('span');
        modernVersionOfElement.classList.add('-zerolfie-web-internals-blink');
        modernVersionOfElement.innerHTML = element.innerHTML;
        element.replaceWith(modernVersionOfElement);
    });
    // Replace acronym elements with abbr equivalents
    document.querySelectorAll("acronym").forEach(element => {
    });
})();
// Apply CSS for deprecated elements in real time
async function cssApplyLoop() {
    while (true) {
        cssApply();
        await new Promise(r => setTimeout(r, 1000)); // 1-second delay
    }
}
function cssApply() {
    setTimeout(blinkElements, 1000);
}
function blinkElements() {
    document.querySelectorAll('span.-zerolfie-web-internals-blink').forEach(element => {
        if (element.style.display === 'none') {
            element.style.display = "inherit";
        }
        else {
            element.style.display = "none";
        }
    });
}
//# sourceMappingURL=automodernizer.js.map