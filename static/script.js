if (document.readyState == "loading") {
    document.addEventListener('DOMContentLoaded', () => { main() });
} else {
    main();
}

function main() {
    listen_arrow_presses()

    $(".cell").change((event) => {
        if ((isNaN(event.target.value) && event.target.value !== '') || event.target.value === '0') {
            console.log(event.target.value.length)
            event.target.value = 1
        }
    })
    
    var rows = document.getElementsByClassName("row")
    $("#solve_btn").click(() => {
        hide_result_board()

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
                if (result.solution === "fail") {
                    alert("Wrong input. Can't solve.")
                    return
                }

                let result_div = document.getElementById("result_div")
                result_div.innerHTML = `<table class="result_table">
                        <caption>Result</caption>
                        <colgroup><col><col><col></colgroup>
                        <colgroup><col><col><col></colgroup>
                        <colgroup><col><col><col></colgroup>
                    </table>`

                var table = result_div.getElementsByClassName("result_table")[0]
                for (let i = 0; i < 3; ++i) {
                    let tbody = document.createElement("tbody")
                    table.appendChild(tbody)
                    for (let j = 0; j < 3; ++j) {
                        let tr = document.createElement("tr")
                        tr.classList.add("row_result")
                        tbody.appendChild(tr)
                        for (let k = 0; k < 9; ++k) {
                            let td = document.createElement("td")
                            td.classList.add("cell")
                            td.textContent = result.solution[3 * i + j][k]
                            tr.appendChild(td)
                        }
                    }
                }
            }
        })
    })

    var cells_input = document.getElementsByClassName("cell_input")
    $("#clear_btn").click(() => {
        hide_result_board()
        for (let i = 0; i < cells_input.length; ++i) {
            cells_input[i].value = ''
        }
    })

    var loader = document.getElementById("loader")
    $('#file_input').change((event) => {
        let formData = new FormData()
        formData.append("image", event.target.files[0])
        loader.style.display = 'block'

        $.ajax({
            type: "POST",
            url: "/process_image",
            contentType: false,
            cache: false,
            processData: false,
            data: formData,
            dataType: "json",
            success: (result) => {
                hide_result_board()
                if (result.result === "fail") {
                    alert("Processing image failed. Error:" + result.error)
                    return
                }

                for (let i = 0; i < cells_input.length; ++i) {
                    cells_input[i].value = (result.result[i] !== 0) ? result.result[i] : '' 
                }

                loader.style.display = 'none'
            },
            error: () => {
                loader.style.display = 'none'
                alert("Http request failed")
            }
        })
    })
}

function hide_result_board() {
    let result_div = document.getElementById("result_div")
    result_div.innerHTML = ""
}

function listen_arrow_presses() {
    document.addEventListener("keydown", function(event) {
        var cells_input = Array.from(document.getElementsByClassName("cell_input"))
        const focus_index = cells_input.findIndex(element => element === document.activeElement)
        if (focus_index < 0) {
            return
        }

        switch (event.key) {
            case "ArrowUp":
                if (focus_index >= 9) {
                    cells_input[focus_index - 9].focus()
                } else if (focus_index > 0) {
                    cells_input[focus_index + cells_input.length - 10].focus()
                }
                break;
            case "ArrowRight":
                if (focus_index < cells_input.length - 1) {
                    cells_input[focus_index + 1].focus()
                }
                break;
            case "ArrowDown":
                if (focus_index < cells_input.length - 9) {
                    cells_input[focus_index + 9].focus()
                } else if (focus_index < cells_input.length - 1) {
                    cells_input[focus_index - (cells_input.length - 10)].focus()
                }
                break;
            case "ArrowLeft":
                if (focus_index > 0) {
                    cells_input[focus_index - 1].focus()
                }
                break;
        }
    })
}
