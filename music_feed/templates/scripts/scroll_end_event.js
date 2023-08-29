// https://stackoverflow.com/questions/10059888/detect-when-scroll-reaches-the-bottom-of-the-page-without-jquery
// https://jsfiddle.net/W75mP/

const page_end_event = new CustomEvent("page-end", { "detail": "Example of an event", "bubbles": true });

// document.onscroll = function () {
document.addEventListener("scroll", function (event) {
    if (document.documentElement.scrollTop + window.innerHeight >= document.documentElement.scrollHeight - 10) {
        document.dispatchEvent(page_end_event);
    }
});

// document.addEventListener("scroll", function (event) {
//     if (getDocHeight() <= getScrollXY()[1] + window.innerHeight - 10) {
//         document.dispatchEvent(page_end_event);

//     }
// });


//below taken from http://www.howtocreate.co.uk/tutorials/javascript/browserwindow
function getScrollXY() {
    var scrOfX = 0, scrOfY = 0;
    if( typeof( window.pageYOffset ) == 'number' ) {
        //Netscape compliant
        scrOfY = window.pageYOffset;
        scrOfX = window.pageXOffset;
    } else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
        //DOM compliant
        scrOfY = document.body.scrollTop;
        scrOfX = document.body.scrollLeft;
    } else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
        //IE6 standards compliant mode
        scrOfY = document.documentElement.scrollTop;
        scrOfX = document.documentElement.scrollLeft;
    }
    return [ scrOfX, scrOfY ];
}

//taken from http://james.padolsey.com/javascript/get-document-height-cross-browser/
function getDocHeight() {
    var D = document;
    return Math.max(
        D.body.scrollHeight, D.documentElement.scrollHeight,
        D.body.offsetHeight, D.documentElement.offsetHeight,
        D.body.clientHeight, D.documentElement.clientHeight
    );
}