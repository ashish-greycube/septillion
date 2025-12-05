$(document).ready(function() {
    let fullwidth = true;
    localStorage.container_fullwidth = fullwidth;
    $(document.body).toggleClass("full-width", fullwidth);
    console.log(localStorage.container_fullwidth, "=============In Toggle Full Width JS===============");
});