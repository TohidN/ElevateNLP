document.addEventListener("DOMContentLoaded", () => {
    //htmx.logger = function(elt, event, data) {
    //    if(console) {
    //        console.log(event, elt, data);
    //    }
    //}
    //console.log(`Document is ready!`);

    // If elements containing `force-refresh="true"` attribute are triggered, after modal is closed, page will be refreshed
    page_modal = document.getElementById('page-modal');
    page_modal.addEventListener('hidden.bs.modal', e => { if(window.force_refresh_on_modal_hide){ location.reload(); } })
    htmx.on("htmx:afterOnLoad", (e) => { if(e.detail.elt.getAttribute("force-refresh")=='true'){ window.force_refresh_on_modal_hide = true; } });
});

document.addEventListener("DOMContentLoaded", () => {
    htmx.on("hidden.bs.modal", () => {
        // empty modal after it has been hidden. otherwise after loading a new modal old content will be shown until response re-fills it
        document.getElementById("modal-container").innerHTML = "";
    });

    htmx.on("htmx:afterOnLoad", (e) => {
        // change selected tab, if a tab was loaded
        if (e.detail.elt.parentNode.parentNode.classList.contains('nav-tabs') && e.detail.xhr.response){
            var descendants = e.detail.elt.parentNode.parentNode.querySelectorAll(".active");
            for(var counter = 0; counter < descendants.length; counter++){
                descendants[counter].classList.remove('active');
            }
            e.detail.elt.classList.add('active');
        }
    });

    htmx.on("htmx:beforeSwap", function(e) {
        if (e.detail.target.id == "main-container" && e.detail.xhr.response){
            // solve issue where new page is loaded, then back button shows page with open modal
            modal = bootstrap.Modal.getInstance(document.getElementById('page-modal'));
            modal.hide();
            document.getElementById('page-modal').style.display = 'none';

            // solve issue where page load finished, but modal's effect on <body>'s class and style remains
            if (document.body.classList.contains('modal-open')){
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty("overflow");
                document.body.style.removeProperty("padding-right");
            }

            // Solve issue with partial loading of page from modal where `modal-backdrop` remains
            var backdrop = document.getElementsByClassName("modal-backdrop");
            for(var counter = 0; counter < backdrop.length; counter++){
                backdrop[counter].remove();
            }
        }
       
    });

});