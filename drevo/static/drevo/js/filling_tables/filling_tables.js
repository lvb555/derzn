let table = $("#id_table")
let row = $("#id_row")
let column = $("#id_column")
let zn_in_cell = $("#id_znanie")

function checkSelection() {
    if (row.val() && column.val()) {
        $("#add_znanie").prop('disabled', false);
        const data = { id_table: table.val(), id_row: row.val(), id_column: column.val()};
        let url = document.querySelector('script[data-get-cell]').getAttribute('data-get-cell');
        fetch(url, {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json',
               'X-CSRFToken': csrftoken
           },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                let key = Object.keys(data);
                let value = Object.values(data);
                zn_in_cell.empty();
                zn_in_cell.append(`<option value="${key}" selected>${value}</option>`);
            }
         })
        .catch((error) => {
        console.log('Error:', error);
        });
    }
}

async function saveZnToCell(znanie_for_cell_id) {
    const data = { table_id: table.val(), row_id: row.val(), column_id: column.val(), znanie_in_cell_id: znanie_for_cell_id};
    let url = document.querySelector('script[data-save-zn]').getAttribute('data-save-zn');
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        });
    } catch (error) {
        console.log('Error:', error);
    }

}

row.change( function () {
    checkSelection();
});

column.change( function () {
    checkSelection();
});


function addZnanie() {
    window.open(`/drevo/new_zn_for_cell_in_table/table_id/${table.val()}/row_id/${row.val()}/column_id/${column.val()}`, 'modal', 'Width=1280,Height=650');
}

 $("#btn_show").on('click', function(){
  window.open(`/drevo/znanie/${table.val()}`);
 });
