


document.addEventListener("page-end", function (e) {
    console.log(e.detail); // Prints "Example of an event"
    get_more_uploads();
});

document.addEventListener("reload-filter-data", function (e) {
    console.log(e.detail);
    reload_uploads();
});


// Get more uploads
var upload_list = document.getElementById("upload_list");

var last_upload_id = null;

const upload_get_url = "/uploads";          //"{{url_for('subfeed.uploads')}}";
const upload_update_url = "/update";        // "{{url_for('subfeed.update')}}";


function add_uploads(uploads_data) {
    var template = document.getElementById("upload_template");

    for (let index = 0; index < uploads_data.length; index++) {
        const upload = uploads_data[index];

        // console.log(upload);

        // // Add upload
        var clone = template.content.cloneNode(true);

        /////////////////////////////////////////////////////////////////////////////
        var mainDIV = clone.getElementById("upload-id")
        // mainDIV.onclick = function () { open_video(upload["url"]); };
        mainDIV.id = "upload_" + upload["id"];
        mainDIV.href = upload["url"];

        tags = upload["tags"];
        var tag_string = "";
        tags.forEach(tag => {
            tag_string = tag_string + "" + tag["id"] + ",";
        });
        mainDIV.dataset.tagid = tag_string;

        mainDIV.style = "outline: 7px solid " + upload["color"] + "; "


        /////////////////////////////////////////////////////////////////////////////
        var image = clone.getElementById("image")
        image.src = upload["thumbnail_url"]


        /////////////////////////////////////////////////////////////////////////////
        var title_div = clone.getElementById("title")
        title_div.innerHTML = upload["title"]
        title_div.title = upload["title"]


        /////////////////////////////////////////////////////////////////////////////
        var channel_div = clone.getElementById("channel_name")
        channel_div.innerHTML = upload["channel"]["name"]


        /////////////////////////////////////////////////////////////////////////////
        var time_div = clone.getElementById("time")
        time_div.innerHTML = upload["time_relativ"]
        time_div.title = upload["dateTime"]


        upload_list.appendChild(clone);

        last_upload_id = upload["id"]
    }

    update_tagID_filtered();

    // TODO handle no more new uploads 
}


const getJSON = async url => {
    const response = await fetch(url);
    if (!response.ok) // check if response worked (no 404 errors etc...)
        throw new Error(response.statusText);

    const data = response.json(); // get JSON from the response
    return data; // returns a promise, which resolves to this data value
}

const upload_update_delay_ms = 1000;
var last_upload_time = +new Date() - (upload_update_delay_ms * 2);

var temp_run_count = 0;

function get_more_uploads() {
    console.log("Loading more uploads...");

    // rate limit incase of problems or something

    const now = +new Date();
    if (now - last_upload_time < upload_update_delay_ms) {
        console.log("rate limit reached");
        return
    }

    new_update_url = upload_get_url + "?";

    if (last_upload_id != null) {
        new_update_url = new_update_url + "last_upload_idx=" + last_upload_id;
    }

    if (current_filter_tag_id != null) {
        new_update_url = new_update_url + "&filter_tag=" + current_filter_tag_id;
    }

    console.log(new_update_url);
    console.log(current_filter_tag_id);

    getJSON(new_update_url).then(data => {

        console.log(data);
        add_uploads(data);


    }).catch(error => {
        console.error(error);
    });

    temp_run_count++;
    console.log("Run count: " + temp_run_count);

    last_upload_time = now;
}

// reload when changing filter tag
function reload_uploads() {
    console.log("reloading uploads");
    last_upload_id = null;

    var upload_grid = document.getElementById("upload_list");
    upload_grid.innerHTML = '';

    // var all_uploads = document.getElementsByClassName("music-grid-item")
    // console.log(all_uploads)
    // console.log(all_uploads.length)

    // for (let index = 0; index < all_uploads.length; index++) {
    //     const upload = all_uploads[index];
    //     upload.remove();
    // }

    // console.log(all_uploads)
    console.log(upload_grid)

    get_more_uploads();
}

function update_uploads() {
    displayLoading();

    console.log("Updating Uploads list...");
    console.log(upload_update_url);

    getJSON(upload_update_url).then(data => {

        console.log(data);
        console.log(data["response"]);

        if (data["response"] == "True") {
            location.reload();
        }

        if (data["response"] == "False") {
            console.log("Nothing New")
        }

        hideLoading();

    }).catch(error => {
        console.error(error);
        hideLoading();
    });

}

