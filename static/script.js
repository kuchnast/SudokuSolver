if (document.readyState == "loading") {
    document.addEventListener('DOMContentLoaded', () => { main() });
} else {
    main();
}

function main() {
    $(".cell").change((event) => {
        if ((isNaN(event.target.value) && event.target.value !== '') || event.target.value === '0') {
            console.log(event.target.value.length)
            event.target.value = 1
        }
    })
    
    var rows = document.getElementsByClassName("row")
    $("#solve_btn").click(() => {
        const DIMENSION = 9
        var data_table = []
        for (let i = 0; i < rows.length; ++i) {
            data_table.push([])
            let cells = rows[i].getElementsByClassName("cell")
            for (let j = 0; j < cells.length; ++j) {
                data_table[i].push(cells[j].value == '' ? 0 : Number(cells[j].value))
            }
        }

        $.ajax({
            type: "POST",
            url: "/solve",
            data: JSON.stringify(data_table),
            contentType: "application/json",
            dataType: "json",
            success: (result) => {
                console.log(result)
            }
        })
    })

    var cells = document.getElementsByClassName("cell")
    $("#clear_btn").click(() => {
        for (let i = 0; i < cells.length; ++i) {
            cells[i].value = ''
        }
    })
}
