


document.addEventListener("page-end", function (e) {
    console.log(e.detail); // Prints "Example of an event"
    get_more_channels();
});

document.addEventListener("reload-filter-data", function (e) {
    console.log(e.detail); // Prints "Example of an event"
    reload_channels();
});


// Get more channels
var channel_list = document.getElementById("channel_list");

var last_channel_id = null;

const channel_get_url = "/channels/page";          //"{{url_for('subfeed.channels')}}";


function add_channels(data) {
    var template = document.getElementById("channel_template");

    channels_data = data["channels"]
    tags_data = data["tags"]

    for (let index = 0; index < channels_data.length; index++) {
        const channel = channels_data[index];

        // console.log(channel);

        // // Add channel
        var clone = template.content.cloneNode(true);

        /////////////////////////////////////////////////////////////////////////////
        var mainDIV = clone.getElementById("channel_div")
        // mainDIV.onclick = function () { open_video(channel["url"]); };
        mainDIV.id = "channel_" + channel["id"];

        tags = channel["tags"];
        var tag_string = "";
        tags.forEach(tag => {
            tag_string = tag_string + "" + tag["id"] + ",";
        });
        mainDIV.dataset.tagid = tag_string;

        mainDIV.style = "outline: 5px solid " + channel["color"] + "; ";


        /////////////////////////////////////////////////////////////////////////////
        var id_text = clone.getElementById("channel_id");
        id_text.textContent  = "#" + channel["id"];

        var name_text = clone.getElementById("channel_name");
        name_text.href = channel["yt_link"]
        name_text.textContent = channel["name"]

        var channel_edit_link = clone.getElementById("channel_edit_link");
        channel_edit_link.href = "/channels/" + channel["id"] + "/edit"


        /////////////////////////////////////////////////////////////////////////////
        var image = clone.getElementById("channel_image_link")
        image.src = channel["profile_img_url"]


        /////////////////////////////////////////////////////////////////////////////
        // tag_edit_form_id
        /////////////////////////////////////////////////////////////////////////////
        var tag_edit_form = clone.getElementById("tag_edit_form_id")
        tag_edit_form.id = "edit_form_" + channel["id"]
        tag_edit_form.action = "/channels/" + channel["id"] + "/edit_tags"

        var tag_select = clone.getElementById("tag_edit_list")
        tag_select.onchange = function() {
            register_tag_change(channel["id"]);
        };

        var tag_edit_option_template = clone.getElementById("tag_edit_option_template")
        
        
        tags = channel["tags"];
        tags_data.forEach(tag => {
            var tag_edit_option_clone = tag_edit_option_template.content.cloneNode(true);

            tag_option = tag_edit_option_clone.getElementById("tag_edit_option")
            tag_option.style="background-color: " + tag["color"] + ";"
            tag_option.value = tag["name"]
            tag_option.text = tag["name"]

            if (channel["tags"].includes(tag)){
                tag_option.selected = true
            }else{
                tag_option.selected = false
            }

            
            tag_select.appendChild(tag_option);
        });

        var tag_edit_submit_btn = clone.getElementById("tag_edit_submit_btn")
        tag_edit_submit_btn.onclick = function() {
            send_tags_form(channel["id"]);
        };
        
        
        /////////////////////////////////////////////////////////////////////////////
        // Channel delete Form
        /////////////////////////////////////////////////////////////////////////////
        var channel_delete_form = clone.getElementById("channel_delete_form")
        channel_delete_form.action = "/channels/" + channel["id"] + "/delete"



        /////////////////////////////////////////////////////////////////////////////


        channel_list.appendChild(clone);

        last_channel_id = channel["id"]
    }

    update_tagID_filtered();

    // TODO handle no more new channels 
}


const getJSON = async url => {
    const response = await fetch(url);
    if (!response.ok) // check if response worked (no 404 errors etc...)
        throw new Error(response.statusText);

    const data = response.json(); // get JSON from the response
    return data; // returns a promise, which resolves to this data value
}

const channel_update_delay_ms = 1000;
var last_channel_time = +new Date() - (channel_update_delay_ms * 2);

var temp_run_count = 0;

function get_more_channels() {
    console.log("Loading more channels...");

    // rate limit incase of problems or something

    const now = +new Date();
    if (now - last_channel_time < channel_update_delay_ms) {
        console.log("rate limit reached");
        return
    }

    new_update_url = channel_get_url + "?";

    if (last_channel_id != null) {
        new_update_url = new_update_url + "last_channel_id=" + last_channel_id;
    }

    if (current_filter_tag_id != null) {
        new_update_url = new_update_url + "&filter_tag=" + current_filter_tag_id;
    }

    console.log(new_update_url);
    console.log(current_filter_tag_id);

    getJSON(new_update_url).then(data => {

        console.log(data);
        add_channels(data);


    }).catch(error => {
        console.error(error);
    });

    temp_run_count++;
    console.log("Run count: " + temp_run_count);

    last_channel_time = now;
}

// reload when changing filter tag
function reload_channels() {
    console.log("reloading channels");
    last_channel_id = null;

    var channel_list = document.getElementById("channel_list");
    channel_list.innerHTML = '';

    // var all_channels = document.getElementsByClassName("music-grid-item")
    // console.log(all_channels)
    // console.log(all_channels.length)

    // for (let index = 0; index < all_channels.length; index++) {
    //     const channel = all_channels[index];
    //     channel.remove();
    // }

    // console.log(all_channels)
    console.log(channel_list)

    get_more_channels();
}



get_more_channels();