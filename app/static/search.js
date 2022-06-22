let activeDivisonElm = null;
function hideActiveDivision() {
    if (activeDivisonElm != null) {
        activeDivisonElm.style.display = "none";
    }
}

let dividedDeparts = ["61", "64", "65", "66"]

var radios = document.querySelectorAll('.depart-input > input');
for (var radio of radios) {
    if (dividedDeparts.indexOf(radio.value) != -1) {
        radio.addEventListener("click", function () {
            var target = document.getElementById("division-" + this.value);
            hideActiveDivision();
            target.style.display = "flex";
            activeDivisonElm = target;
        }, { "once": false });
        document.getElementById("division-" + radio.value).style.display = "none";
    } else {
        radio.addEventListener("click", hideActiveDivision, { "once": false });
    }
}