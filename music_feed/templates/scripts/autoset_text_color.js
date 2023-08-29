
// Source:
// https://wunnle.com/dynamic-text-color-based-on-background

var hexDigits = new Array("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f");

window.addEventListener("load", autoset_text_color);

function autoset_text_color() {
    auto_color_elements = document.querySelectorAll("[data-autoset-text-color='true']");
    console.log(auto_color_elements.length)

    auto_color_elements.forEach(element => {
        // console.log(element)
        // console.log(element.style)
        // console.log(element.style.backgroundColor)
        // console.log(element.style.backgroundColor == "")
        // console.log(element.style.backgroundColor == null)

        const bgColor = get_element_bg_color(element);

        const textColor = getTextColor(bgColor);

        element.style.color = textColor;
    });

    console.log("Auto color DONE")
}

function get_element_bg_color(element) {
    // https://www.permadi.com/tutorial/cssGettingBackgroundColor/index.html
    
    let bg_color = element.style.backgroundColor; //window.getComputedStyle(element).backgroundColor;
    
    // console.log(element);
    // console.log(element.parentElement);
    // console.log(bg_color);

    if (bg_color == "") {
        // return rgb2hex(bg_color);
        bg_color = "rgb(70, 70, 70)"; //get_element_bg_color(element.parentElement)
    }

    return rgb2hex(bg_color);
}

//Function to convert rgb color to hex format
function rgb2hex(rgb) {
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}

function hex(x) {
    return isNaN(x) ? "00" : hexDigits[(x - x % 16) / 16] + hexDigits[x % 16];
}


function getRGB(c) {
    return parseInt(c, 16) || c;
}

function getsRGB(c) {
    return getRGB(c) / 255 <= 0.03928
        ? getRGB(c) / 255 / 12.92
        : Math.pow((getRGB(c) / 255 + 0.055) / 1.055, 2.4);
}

function getLuminance(hexColor) {
    return (
        0.2126 * getsRGB(hexColor.substr(1, 2)) +
        0.7152 * getsRGB(hexColor.substr(3, 2)) +
        0.0722 * getsRGB(hexColor.substr(-2))
    );
}

function getContrast(f, b) {
    const L1 = getLuminance(f);
    const L2 = getLuminance(b);
    return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
}

function getTextColor(bgColor) {
    const whiteContrast = getContrast(bgColor, "#ffffff");
    const blackContrast = getContrast(bgColor, "#000000");

    // console.log("contrast " + whiteContrast + " - " + blackContrast);

    return whiteContrast > blackContrast ? "#ffffff" : "#000000";
}