if (document.readyState == "loading") {
    document.addEventListener('DOMContentLoaded', () => { main() });
} else {
    main();
}

function main() {
    var cells = document.getElementsByClassName("cell")
    for (var i = 0; i <cells.length; ++i) {
        cells[i].addEventListener("change", (event) => {
            if (isNaN(event.target.value) || event.target.value == 0) {
                event.target.value = 1
            }
        })
    }
}
