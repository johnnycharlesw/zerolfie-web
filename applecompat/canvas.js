let framebuffer = new ImageData(window.innerWidth, window.innerHeight);
let canvas = document.getElementById('rootcanvas');
canvas.addEventListener("contextmenu", (e)=>{
    e.preventDefault();
});
let ctx = canvas.getContext("2d");

window.addEventListener('resize', (e)=>{
    framebuffer.width=window.innerWidth;
    framebuffer.height=window.innerHeight;
});

function drawFramebuffer(){
    ctx.reset();
    ctx.putImageData(framebuffer, 0, 0);
}

function filterCanvasContent(filter_img){
    for (let index = 0; index < filter_img.data.length; index++) {
        let filter_subpixel = filter_img.data[index];
        framebuffer.data[index]=framebuffer.data[index]*filter_subpixel;
    }
    drawFramebuffer();
}
function increaseCanvasBrightness(by_how_much){
    for (let index = 0; index < framebuffer.data.length; index++) {
        const subpixel = framebuffer.data[index];
        framebuffer.data[index] = subpixel+by_how_much;
    }
    drawFramebuffer();
}

function renderFrame(frame){
    filterCanvasContent(new ImageData(framebuffer.width, framebuffer.height));
    increaseCanvasBrightness(255);
    filterCanvasContent(frame);
}

function pageCanvas(){
    window.WKWebViewJavaScriptBridge.registerHandler('frameRendered', function (data, callback){
        let imported_image=new ImageData(framebuffer.width, framebuffer.height);
        imported_image.data=data;
        renderFrame(imported_image);
    });
}