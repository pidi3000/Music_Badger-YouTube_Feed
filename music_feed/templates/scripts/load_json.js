
const getJSON = async url => {
    const response = await fetch(url);
    if (!response.ok) // check if response worked (no 404 errors etc...)
        throw new Error(response.statusText);

    const data = response.json(); // get JSON from the response
    return data; // returns a promise, which resolves to this data value
}

function load_json(url, callback_Function) {
    getJSON(url).then(data => {

        console.log(data);
        callback_Function(data);

    }).catch(error => {
        console.error(error);
    });
}