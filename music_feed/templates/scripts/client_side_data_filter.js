

document.addEventListener("reload-filter-data", function (e) {
    // console.log(e); // Prints "Example of an event"
    console.log(e.detail); // Prints "Example of an event"
    // console.log(e.filter_tag); // Prints "Example of an event"
    filter_elements_by_id(e.filter_tag);
});

function filter_elements_by_id(tag_id){    
    let all_elements = document.querySelectorAll("[data-tagID]")

    // Client side filtering (old)
    
    all_elements.forEach(element => {
        if (tag_id == -1) { // Show ALL
            element.style.display = "block";

        } else if (tag_id == -2) {  // Show untagged
            element.style.display = "block";

            if (element.dataset.tagid == "") {
                element.style.display = "block";
            } else {
                element.style.display = "none";
            }

        } else {    // Filter by tag id
            let element_tags = element.dataset.tagid;

            if (element_tags.split(",").indexOf("" + tag_id) > -1) {
                element.style.display = "block";
            } else {
                element.style.display = "none";
            }
        }
    });
}