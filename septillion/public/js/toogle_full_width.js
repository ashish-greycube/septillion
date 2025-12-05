$(document).ready(function() {
    console.log("=============In Toggle Full Width JS===============");
    // let fullwidth = JSON.parse(localStorage.container_fullwidth || "true");
    let fullwidth = "true";
    console.log(fullwidth, "===========fullwidth===================")
    localStorage.container_fullwidth = fullwidth;
    $(document.body).toggleClass("full-width", fullwidth);
    // console.log("===========fullwidth===================")

});