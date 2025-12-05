$(document).ready(function() {
    console.log("=============DOCUMENT READY===============");
    let fullwidth = localStorage.container_fullwidth
    console.log(fullwidth, "============localStorage.container_fullwidth==========")
    if (fullwidth == false || fullwidth == "false") {
        console.log("===============inside if=============")
        frappe.ui.toolbar.toggle_full_width()
    }
});


// document.addEventListener("DOMContentLoaded", function() {
//   // Code to be executed once the DOM is ready
//     console.log("DOM is ready!");
//     let fullwidth = localStorage.container_fullwidth
//     console.log(fullwidth, "============localStorage.container_fullwidth==========")
//     if (fullwidth == false || fullwidth == "false") {
//         console.log("===============inside if=============")
//         frappe.ui.toolbar.toggle_full_width()
//     }
// });