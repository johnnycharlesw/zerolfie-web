window.addEventListener('DOMContentLoaded', ()=>{
    let back_btn = document.getElementById("go-back-button");
    let foward_btn = document.getElementById("go-foward-button");
    let refresh_btn = document.getElementById("refresh-button");
    let home_btn = document.getElementById("home-button");
    let go_btn = document.getElementById("go-btn");
    let url_textbox = document.getElementById("url-textbox");
    let content_iframe = document.getElementById("browser-content");
    go_btn.addEventListener('click', ()=>{
        let url=url_textbox.value;
        content_iframe.src=url;
    });
})