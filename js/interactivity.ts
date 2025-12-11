// Link handling
document.querySelectorAll("a:link").addEventListener("click", (e)=>{
    // Follow the link upon it being clicked
    if (__PyBark__.canVisit(e.target.href)) {
        window.location = e.target.href;
    }
});