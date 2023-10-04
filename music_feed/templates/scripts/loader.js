
const loader = document.querySelector("#loading");


// showing loading
function displayLoading() {
    loader.classList.add("display");
    // to stop loading after some time
    setTimeout(() => {
        loader.classList.remove("display");
    }, 120*1000);
}

// hiding loading 
function hideLoading() {
    loader.classList.remove("display");
}