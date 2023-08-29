
var register_tag_changes = [];

function send_all_tags_form(){
    console.log(register_tag_changes);

    var temp = register_tag_changes;
    temp.forEach(element => {
        console.log(element);
        console.log(element == "");
        console.log(element == null);
        send_tags_form(element);
    });

    register_tag_changes = [];
}

function send_tags_form(channel_id) {
    const form_element = document.getElementById("edit_form_" + channel_id);

    // var channel_data = load_json();
    // console.log(channel_data);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "" + form_element.action);
    xhr.onload = function (event) {
        // console.log(xhr);
        console.log(xhr.status);

        if (xhr.status == 200) {
            var channel_element = document.getElementById("channel_" + channel_id);

            var channel_data_raw = event.target.response;
            var channel_data = JSON.parse(channel_data_raw);

            // console.log(channel_data_raw);
            console.log(channel_data);
            // alert("Success, server responded with: " + channel_data_raw);

            // tags_list = form_element.getElementById("tags");
            // tags_options = form_element.querySelectorAll("option");


            delete channel_element.dataset.tagid
            // console.log("");
            // console.log(channel_element);

            tags = channel_data["tags"];
            var tag_string = "";
            tags.forEach(tag => {
                tag_string = tag_string + "" + tag["id"] + ",";
            });
            // console.log(tag_string);

            channel_element.dataset.tagid = tag_string;

            channel_element.style = "outline: 5px solid " + channel_data["color"] + "; "
            // channel_element.style.outline.color = "#ffffff";


            // console.log("");
            delete register_tag_changes[register_tag_changes.indexOf(channel_id)];
            // register_tag_changes = register_tag_changes.splice(register_tag_changes.indexOf(channel_id), 1);
            console.log(register_tag_changes);

            console.log(channel_element);
            update_tagID_filtered();
        } else {
            alert("ERROR, response status: " + xhr.status)
        }



    };
    // or onerror, onabort
    var formData = new FormData(form_element);
    xhr.send(formData);
}

function register_tag_change(channel_id) {
    register_tag_changes.indexOf(channel_id) === -1 ?
        register_tag_changes.push(channel_id) :                 // Condition False
        console.log("This item already exists: " + channel_id); // Condition True

    console.log(register_tag_changes);
}