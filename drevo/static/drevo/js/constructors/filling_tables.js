let table = $("#table");
let row = $("#row");
let column = $("#column");
let element_row = $("#element_row")
let element_column = $("#element_column")
let zn_in_cell = $("#znanie");
let new_znanie = $("#new-znanie");
let select_zn = $('#select_zn');
let create_zn_for_rel = $('#create_zn_for_rel');
let choose_zn_for_cell = $('#zn_choose');
let create_zn = document.getElementById('create_zn');
let row_id, column_id;
let choose_row_type = "row", choose_column_type = "column";

function checkSelection() {
    if (element_row.val()) {
        row_id = element_row.val();
        choose_row_type = "element_row";
        if (element_column.val()) {
            column_id = element_column.val();
            choose_column_type = "element_column";
        } else if (element_column.length === 0 && column.val()) {
            column_id = column.val();
        }
    } else if (element_column.val()) {
        column_id = element_column.val();
        choose_column_type = "element_column";
        if (element_row.length === 0 && row.val()) {
            row_id = row.val();
        }
    }
    else if (row.val() && column.val()) {
        row_id = row.val();
        column_id = column.val();
    }
    if (row_id && column_id) {
        $("#edit_znanie").css('cursor', 'pointer').attr("class", "text-primary");
        fetch(`/drevo/get_cell_for_table/?table_id=${table.val()}&row_id=${row_id}&column_id=${column_id}`)
        .then(response => response.json())
        .then(data => {
             zn_in_cell.prop('disabled', false)
            if (Object.keys(data).length > 0) {
                let key = Object.keys(data);
                let value = Object.values(data);
                zn_in_cell.empty().append(`<option value="${key}" selected>${value}</option>`);
            }
            else {
                zn_in_cell.empty().append(`<option value="">В этой ячейке еще нет знания!</option>`);
            }
        });
    }
}

row.add(column).on('change', function () {
    checkSelection();
});

element_row.add(element_column).on('change', function () {
    checkSelection();
});

function addZnanie() {
    select_zn.select2();
    new_znanie.prop('hidden', true);
    if (zn_in_cell.val()) select_zn.find(`option[value="${zn_in_cell.val()}"]`).remove();
    create_zn_for_rel.modal("show");
}

$("#open_table").on('click', function(){
  window.open(`/drevo/znanie/${table.val()}`);
});

function newZnanie() {
    if (new_znanie.is(':hidden')) new_znanie.removeAttr('hidden');
    else new_znanie.prop('hidden', true);
}
create_zn.addEventListener('submit', (event) => {
    let uuid = $('#zn_form_uuid').val();
    $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData());
    event.preventDefault();
    const formData = new FormData(create_zn);
    fetch('/drevo/create_zn_for_cell/', {
     method: 'POST',
     body: formData,
    })
    .then(response => response.json())
    .then(data => {
        select_zn.append(`<option value="${data.zn_id}" selected>${data.zn_name}</optionselected>`);
        new_znanie.prop('hidden', true);
        create_zn.reset();
        CKEDITOR.instances[uuid].setData('');
    });
})
choose_zn_for_cell.click(function() {
    if (select_zn.val() !== '') {
        const data = { table_id: table.val(), row_id: row_id,  column_id: column_id, selected_zn_for_cell_id: select_zn.val()};
            fetch('/drevo/save_zn_to_cell_in_table/', {
             method: 'POST',
             body: JSON.stringify(data),
             headers: {
                 'X-CSRFToken': csrftoken
             }
           })
          .then(response => {
              zn_in_cell.empty().append(`<option value="${select_zn.val()}" selected>${select_zn.find('option:selected').text()}</option>`);
          });
        create_zn_for_rel.modal("hide");
    }
});
