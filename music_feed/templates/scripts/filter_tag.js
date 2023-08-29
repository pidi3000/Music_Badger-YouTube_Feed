


var current_filter_tag_id = -1;

var data_reload_event = new CustomEvent(
    "reload-filter-data",
    {
        "detail": "Reload or filter data using the filter tag: " + current_filter_tag_id,
        "filter_tag": current_filter_tag_id,
        "bubbles": true
    }
);


// filter_by_URL_Parameter();

window.addEventListener("load", filter_by_URL_Parameter);
// document.body.onload = function () {
//     filter_by_URL_Parameter();
// }


function set_Filter_Parameter_on_form_action(element_id) {
    form_url = document.getElementById(element_id).action
    var url = new URL(form_url);

    console.log(form_url)
    filter_tag = current_filter_tag_id;
    console.log(filter_tag);



    if (filter_tag != null) {
        url.searchParams.set("filter_tag", filter_tag);
        console.log(url);

        new_form_url = url.href
        console.log(new_form_url);

        document.getElementById(element_id).action = new_form_url
    }
}

function add_Parameter_to_URL(url, parameter_name, parameter_value) {
    var url = new URL(url);

    if (parameter_value != null) {
        url.searchParams.set("" + parameter_name, parameter_value);
    }

    return url.href
}

function get_Filter_URL_Parameter() {

    const queryString = window.location.search;
    console.log(queryString);

    const urlParams = new URLSearchParams(queryString);
    filter_tag = urlParams.get("filter_tag");
    // console.log(filter_tag);
    return filter_tag;
}

function filter_by_URL_Parameter() {
    filter_tag = get_Filter_URL_Parameter();

    if (filter_tag != null) set_tagID_filtered(filter_tag);
}

function update_tagID_filtered() {
    set_tagID_filtered(current_filter_tag_id);
}


function set_tagID_filtered(tag_id) {
    var reload_needed = current_filter_tag_id != tag_id;
    current_filter_tag_id = tag_id;

    if (reload_needed) {
        data_reload_event.filter_tag = current_filter_tag_id;
        document.dispatchEvent(data_reload_event);
    }


    all_uploads = document.querySelectorAll("[data-tagID]")


    // Client side filtering (old)

    // all_uploads.forEach(upload => {
    //     if (tag_id == -1) {
    //         upload.style.display = "block";
    //     } else if (tag_id == -2) {
    //         upload.style.display = "block";

    //         if (upload.dataset.tagid == "") {
    //             upload.style.display = "block";
    //         } else {
    //             upload.style.display = "none";
    //         }
    //     } else {
    //         upload_tags = upload.dataset.tagid;

    //         if (upload_tags.split(",").indexOf("" + tag_id) > -1) {
    //             upload.style.display = "block";
    //         } else {
    //             upload.style.display = "none";
    //         }
    //     }
    // });


    new_URL = add_Parameter_to_URL(location.href, "filter_tag", current_filter_tag_id);

    if (window.location != new_URL) {
        console.log("replace location")
        // window.location.replace(new_URL);
        // window.location.href = new_URL;
        window.history.pushState({ "html": "response.html", "filter_id": "response.pageTitle" }, "", new_URL);


    }

    // location.reload();
}


// https://stackoverflow.com/questions/824349/how-do-i-modify-the-url-without-reloading-the-page/3354511#3354511
window.onpopstate = function (e) {
    console.log("back")
    console.log(e)

    if (e.state) {
        console.log(e.state)
        filter_by_URL_Parameter();
        reload_uploads();
        // document.getElementById("content").innerHTML = e.state.html;
        // document.title = e.state.pageTitle;
    }
};
