let table = $("#table");
let row = $("#row");
let column = $("#column");
let element_row = $("#element_row")
let element_column = $("#element_column")
let zn_in_cell = $("#znanie");
let select_zn = $('#select_zn');
let create_zn_for_cell_modal = $('#create_zn_for_cell_modal');
let choose_zn_for_cell_modal = $('#choose_zn_for_cell_modal');

let create_zn_form =  document.getElementById('create_zn_form');
let row_id, column_id;

let choose_zn_btn =  $("#choose_zn_btn");
let create_zn_btn = $("#create_zn_btn");
let delete_zn_btn = $("#delete_zn_btn");
let delete_element_modal = $("#delete_element_warning")

// Если выбраны и строка (элемент строки), и столбец (элемент столбца), то показывается знание, привязанное к ячейке
function checkSelection() {
    if (!row.val() || !column.val() ||
        (element_row.length !== 0 && !element_row.val()) ||
        (element_column.length !== 0 && !element_column.val())) return;
    if (element_row.val()) row_id = element_row.val();
    else row_id = row.val();
    if (element_column.val()) column_id = element_column.val();
    else column_id = column.val();
    choose_zn_btn.prop('disabled', false).attr("class", "btn btn-outline-info");
    create_zn_btn.prop('disabled', false).attr("class", "btn btn-outline-primary");
    fetch(`/drevo/get_cell_for_table/?table_id=${table.val()}&row_id=${row_id}&column_id=${column_id}`)
    .then(response => response.json())
    .then(data => {
         zn_in_cell.prop('disabled', false)
        if (Object.keys(data).length > 0) {
            let key = Object.keys(data);
            let value = Object.values(data);
            zn_in_cell.empty().append(`<option value="${key}" selected>${value}</option>`);
            delete_zn_btn.prop('disabled', false).attr("class", "btn btn-outline-danger");
        }
        else {
            zn_in_cell.empty().append(`<option value="">В этой ячейке еще нет знания!</option>`);
            delete_zn_btn.prop('disabled', true).attr("class", "btn btn-outline-secondary");
        }
    });
}

row.add(column).on('change', function () {
    checkSelection();
});

element_row.add(element_column).on('change', function () {
    checkSelection();
});
// Открытие окна для создания знания в ячейке
create_zn_btn.click(function () {
    let uuid = $('#zn_form_uuid').val();
    CKEDITOR.instances[uuid].setData('');
    create_zn_form.reset();
    create_zn_for_cell_modal.modal("show");
})

// Сохранение созданного знания и привязка к ячейке таблицы
create_zn_form.addEventListener('submit', (event) => {
    let uuid = $('#zn_form_uuid').val();
    $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData());
    event.preventDefault();
    const formData = new FormData(create_zn_form);
    formData.append('table_id', table.val());
    formData.append('row_id', row_id);
    formData.append('column_id', column_id);
    fetch('/drevo/create_zn_for_cell/', {
     method: 'POST',
     body: formData,
    })
    .then(response => response.json())
    .then(data => {
        zn_in_cell.empty().append(`<option value="${data.zn_id}" selected>${data.zn_name}</option>`);
        delete_zn_btn.prop('disabled', false).attr("class", "btn btn-outline-danger");
        create_zn_for_cell_modal.modal("hide");
    });
})

// Открытие окна для выбора нового знания в ячейке
choose_zn_btn.click(function () {
    select_zn.select2();
    if (zn_in_cell.val()) select_zn.find(`option[value="${zn_in_cell.val()}"]`).remove();
    choose_zn_for_cell_modal.modal("show");
})

// Сохранение выбранного знания в ячейке таблицы
$('#zn_choose').click(function() {
    if (select_zn.val() !== '') {
        const data = { table_id: table.val(), row_id: row_id,  column_id: column_id, selected_zn_for_cell_id: select_zn.val()};
            fetch('/drevo/save_zn_to_cell_in_table_from_request/', {
             method: 'POST',
             body: JSON.stringify(data),
             headers: {
                 'X-CSRFToken': csrftoken
             }
           })
          .then(response => {
              zn_in_cell.empty().append(`<option value="${select_zn.val()}" selected>${select_zn.find('option:selected').text()}</option>`);
              delete_zn_btn.prop('disabled', false).attr("class", "btn btn-outline-danger");
              choose_zn_for_cell_modal.modal("hide");
          });
    }
});

// Удаление связей со знанием в данной ячейке таблицы
delete_zn_btn.click(function () {
    let zn_id = zn_in_cell.val()
    if (zn_id) {
        $('.delete-confirmation').text(`Вы действительно хотите удалить знание в данной ячейке?`);
        delete_element_modal.modal("show");
        $('.js-okay-successful').click(function () {
            const data = { table_id: table.val(), row_id: row_id,  column_id: column_id, selected_zn_for_cell_id: zn_id};
            fetch(`/drevo/delete_zn_in_cell_in_table/`, {
                method: 'DELETE',
                body: JSON.stringify(data),
                headers: {
                     'Content-Type': 'application/json',
                     'X-CSRFToken': csrftoken
                 }
            })
            .then(response => {
                if (response.ok) {
                    delete_element_modal.modal("hide");
                    delete_zn_btn.prop('disabled', true).attr("class", "btn btn-outline-secondary");
                    zn_in_cell.empty().append(`<option value="" selected>Выберите или создайте знание</option>`);
                } else {
                    delete_element_modal.modal("hide");
                    delete_zn_btn.prop('disabled', true).attr("class", "btn btn-outline-secondary");
                    $('#delete_element_error_message').text('Вы не можете удалить ячейку таблицы, так как не являетесь создателем связей с ней.');
                    $('#delete_element_errors').modal('show');
                }
            })
        })
    }
})

$("#open_table").on('click', function(){
  window.open(`/drevo/znanie/${table.val()}`);
});