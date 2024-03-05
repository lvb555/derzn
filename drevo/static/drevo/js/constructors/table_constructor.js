let table = $("#table")
let row = $("#row")
let column = $("#column")
let element_row = $("#element_row")
let element_column = $("#element_column")

let row_is_group = $("#row_is_group")
let column_is_group = $("#column_is_group")

let delete_table = $("#delete_table")
let delete_row = $("#delete_row")
let delete_column = $("#delete_column")
let delete_element_modal = $("#delete_element_warning")

let type_of_tr = $('#type_of_tr')
let action = $('#action')
let create_edit_zn_form = $('#create_edit_zn_form');
let edit_main_zn_form = $('#edit_main_zn_form');

// При выборе строки, столбца, элемента строки или элемента столбца возможно редактирование или удаление
// выбранного элемента
row.change(function () { allow_actions($('#edit_row'), $('#delete_row'));});
column.change(function () { allow_actions($('#edit_column'), $('#delete_column')); });
element_row.change(function () { allow_actions($('#edit_element_row'), $('#delete_element_row')); });
element_column.change(function () { allow_actions($('#edit_element_column'), $('#delete_element_column')); });


// Добавление в модальное окно формы для создания знания
function addZnanie(relation) {
    type_of_tr.val(relation);
    action.val('create')
    if (relation === 'row' || relation === 'column' ) {
        let zn_tz_type;
        if ((relation === 'row' && row.children().length > 1) || (relation === 'column' && column.children().length > 1))
            zn_tz_type = 'heading';
        else zn_tz_type = 'any_type'
        $('#zn_tz_type').val(zn_tz_type);
        fetch(`/drevo/relation_in_table_create_update_view/?action=${action.val()}&zn_tz_type=${zn_tz_type}`)
            .then(response => response.json())
            .then(data => {
                $('#zn_form').html(`${data.zn_form}`);
                $('#order_of_rel_form').html(`${data.order_of_rel_form}`);
                $('#zn_tz_type').val(zn_tz_type);
             })
        if (relation === 'row') $('#create_edit_zn_title').text(`Создание строки`);
        else $('#create_edit_zn_title').text(`Создание столбца`);
    }
    else if (relation === 'element_row' || relation === 'element_column') {
        fetch(`/drevo/element_of_group_in_table_create_update_view/?action=${action.val()}`)
            .then(response => response.json())
            .then(data => {
                $('#zn_form').html(`${data.zn_form}`);
                $('#order_of_rel_form').html(`${data.order_of_rel_form}`);
             })
        if (relation === 'element_row') {
            $('#create_edit_zn_title').text(`Ввод названия элемента группы строк`);
            $('#parent_for_element_of_group').val(row.val());
        }
        else {
            $('#create_edit_zn_title').text(`Ввод названия элемента группы столбцов`);
            $('#parent_for_element_of_group').val(column.val());
        }
    }
    $('#create_edit_zn_modal').modal("show");
}

// Отправка созданного/модифицированного знания
create_edit_zn_form.on('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(create_edit_zn_form[0]);
    if (type_of_tr.val() === 'row' || type_of_tr.val() === 'column') {
        fetch('/drevo/relation_in_table_create_update_view/', {
         method: 'POST',
         body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (type_of_tr.val() === 'row') {
                if (action.val() === 'create') {
                    row.append(`<option id="${data.zn_id}" value="${data.zn_id}" selected>${data.zn_name}</option>`);
                    allow_actions($('#edit_row'), $('#delete_row'));
                }
                else {
                    $(`#row option[id="${data.zn_id}"]`).text(data.zn_name);
                }
                if (data.new_zn_tr_is_group) {
                    $('#add_row').prop('hidden', true);
                    row_is_group.val(true);
                    row.css('appearance', 'none');
                    $('#edit_element_row').css('cursor', 'default').attr("class", "text-secondary");
                    $('#delete_element_row').css('cursor', 'default').attr("class", "text-secondary");
                    $('#row_elements').removeAttr('hidden');
                }
            }
            else {
                if (action.val() === 'create') {
                    column.append(`<option id="${data.zn_id}" value="${data.zn_id}" selected>${data.zn_name}</option>`);
                    allow_actions($('#edit_column'), $('#delete_column'));
                }
                else {
                    $(`#column option[id="${data.zn_id}"]`).text(data.zn_name);
                }
                if (data.new_zn_tr_is_group) {
                    $('#add_column').prop('hidden', true);
                    column_is_group.val(true);
                    $('#edit_element_column').css('cursor', 'default').attr("class", "text-secondary");
                    $('#delete_element_column').css('cursor', 'default').attr("class", "text-secondary");
                    $('#column_elements').removeAttr('hidden');
                }

            }
        });
    }
    else if (type_of_tr.val() === 'element_row' || type_of_tr.val() === 'element_column') {
        fetch('/drevo/element_of_group_in_table_create_update_view/', {
         method: 'POST',
         body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (type_of_tr.val() === 'element_row') {
                if (action.val() === 'create') {
                    element_row.append(`<option id="${data.zn_id}" value="${data.zn_id}" selected>${data.zn_name}</option>`);
                    allow_actions($('#edit_element_row'), $('#delete_element_row'));
                }
                else {
                    $(`#element_row option[id="${data.zn_id}"]`).text(data.zn_name);
                }
            }
            else {
                if (action.val() === 'create') {
                    element_column.append(`<option id="${data.zn_id}" value="${data.zn_id}" selected>${data.zn_name}</option>`);
                    allow_actions($('#edit_element_column'), $('#delete_element_column'));
                }
                else {
                    $(`#element_column option[id="${data.zn_id}"]`).text(data.zn_name);
                }
            }
        });
    }
    $('#create_edit_zn_modal').modal("hide");
})

// Добавление в модальное окно формы для редактирования знания
function editZnanie(relation) {
    type_of_tr.val(relation);
    action.val('edit')
    let zn_id;
    if (relation === 'row' || relation === 'column' ) {
        let zn_tz_type = 'any_type'
        $('#zn_tz_type').val(zn_tz_type);
        if (relation === 'row') zn_id = row.val();
        else zn_id = column.val();
        fetch(`/drevo/relation_in_table_create_update_view/?action=${action.val()}&zn_tz_type=${zn_tz_type}&zn_id=${zn_id}`)
            .then(response => response.json())
            .then(data => {
                $('#zn_form').html(`${data.zn_form}`);
                $('#order_of_rel_form').html(`${data.order_of_rel_form}`);
             })
        if (relation === 'row') $('#create_edit_zn_title').text(`Редактирование строки`);
        else $('#create_edit_zn_title').text(`Редактирование столбца`);
        $('#edited_zn_id').val(zn_id);
        $('#create_edit_zn_modal').modal("show");
    }
    else if (relation === 'element_row' || relation === 'element_column') {
        // $('#relation_type').val('row');
        let zn_tz_type = 'any_type'
        if (relation === 'element_row') zn_id = element_row.val();
        else zn_id = element_column.val();
        fetch(`/drevo/element_of_group_in_table_create_update_view/?action=${action.val()}&zn_tz_type=${zn_tz_type}&zn_id=${zn_id}`)
            .then(response => response.json())
            .then(data => {
                $('#zn_form').html(`${data.zn_form}`);
                $('#order_of_rel_form').html(`${data.order_of_rel_form}`);
             })
        if (relation === 'element_row') {
            $('#create_edit_zn_title').text(`Редактирование элемента группы строк`);
            $('#parent_for_element_of_group').val(row.val());
        }
        else {
            $('#create_edit_zn_title').text(`Редактирование  элемента группы столбцов`);
            $('#parent_for_element_of_group').val(row.val());
        }
        $('#edited_zn_id').val(zn_id);
        $('#create_edit_zn_modal').modal("show");
    }
    else if (relation === 'table') {
        $('#main_zn_edit_modal').modal('show');
    }
}

// Отправка модифицированного главного знания - таблицы
edit_main_zn_form.on('submit', (event) => {
    event.preventDefault();
    let uuid = $('#main_zn_edit_form_uuid').val();
    $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData());
    const formData = new FormData(edit_main_zn_form[0]);
    fetch('/drevo/edit_main_zn_in_constructor/', {
     method: 'POST',
     body: formData,
    })
    .then(response => response.json())
    .then(data => {
        $('#table_name').text(`Таблица: «${data.zn_name}»`);
        $('#main_zn_edit_modal').modal('hide');
    })
})

// Удаление таблицы (при подтверждении пользователем)
delete_table.on('click', function(){
    let table_id = table.val()
    if (table_id) {
        $('.delete-confirmation').text(`Вы действительно хотите удалить данную таблицу? Все связанные знания также удалятся!`);
        delete_element_modal.modal("show");
        $('.js-okay-successful').click(function () {
            let group_in_table = false;
            if (row_is_group.val() || column_is_group.val()) group_in_table = true;
            fetch(`/drevo/delete_table/?id=${table_id}&group_in_table=${group_in_table}`, {
                method: 'DELETE',
                headers: {
                     'Content-Type': 'application/json',
                     'X-CSRFToken': csrftoken
                 }
            })
            .then(response => {
                if (response.ok) {
                    delete_element_modal.modal("hide");
                    $('#success_delete_main_zn').modal("show");
                } else {
                    delete_element_modal.modal("hide");
                    $('#delete_element_error_message').text('Невозможно удалить таблицу, так как к ней привязана заполненная ячейка');
                    $('#delete_element_errors').modal('show');
                }
            })
        })
    }
})

// Открытие модального окна для подтверждения удаления строки
delete_row.on('click', function(){
    let row_id = row.val()
    if (row_id) {
        $('.delete-confirmation').text(`Вы действительно хотите удалить данную строку?`);
        delete_element_modal.modal("show");
        $('.js-okay-successful').click(function () {
            deleteRelation('row', row_is_group);
        })
    }
})

// Открытие модального окна для подтверждения удаления столбца
delete_column.on('click', function(){
    let column_id = column.val()
    if (column_id) {
        $('.delete-confirmation').text(`Вы действительно хотите удалить данный столбец?`);
        delete_element_modal.modal("show");
        $('.js-okay-successful').click(function () {
            deleteRelation('column', column_is_group)
        })
    }
})

// Удаление строки/столбца (при подтверждении пользователем)
function deleteRelation(relation, is_group) {
    let relation_id;
    if (relation === 'row') relation_id = row.val()
    else relation_id = column.val()
    fetch(`/drevo/delete_row_or_column/?id=${relation_id}&is_group=${is_group.val()}&table_id=${table.val()}`, {
        method: 'DELETE',
        headers: {
             'Content-Type': 'application/json',
             'X-CSRFToken': csrftoken
         }
    })
    .then(response => {
        if (response.ok) {
            if (relation === 'row') {
                $('#row option:selected').remove();
                delete_element_modal.modal("hide");
                if (is_group) {
                    $('#add_row').removeAttr('hidden');
                    $('#row_elements').hide();
                    $('#row option#create_row').prop('selected', true);
                    row_is_group.val(false);
                }
            }
            else {
                $('#column option:selected').remove();
                delete_element_modal.modal("hide");
                if (is_group) {
                    $('#add_column').removeAttr('hidden');
                    $('#column_elements').hide();
                    $('#column option#create_column').prop('selected', true);
                    column_is_group.val(false);
                }
            }
            delete_element_modal.modal("hide");
        } else {
            delete_element_modal.modal("hide");
            if (relation === 'row') {
                if (is_group.val()) $('#delete_element_error_message').text('Невозможно удалить строку, так как к ней привязан элемент строки.');
                else $('#delete_element_error_message').text('Невозможно удалить строку, так как к ней привязана заполненная ячейка.');
            }
            else {
                if (is_group.val()) $('#delete_element_error_message').text('Невозможно удалить столбец, так как к нему привязан элемент столбца.');
                else $('#delete_element_error_message').text('Невозможно удалить столбец, так как к нему привязана заполненная ячейка.');
            }
            $('#delete_element_errors').modal('show');
        }
     })
}

// Открытие модального окна для подтверждения удаления элемента строки
$("#delete_element_row").on('click', function(){
    let element_row_id = element_row.val()
    if (element_row_id) {
        $('.delete-confirmation').text(`Вы действительно хотите удалить элемент строки?`)
        delete_element_modal.modal("show");
        $('.js-okay-successful').click(function () {
            deleteElement('row')
        })
    }
})

// Открытие модального окна для подтверждения удаления элемента столбца
$("#delete_element_column").on('click', function(){
    let element_column_id = element_column.val()
    if (element_column_id) {
        $('.delete-confirmation').text(`Вы действительно хотите удалить элемент столбца?`)
        delete_element_modal.modal("show");
        $('.js-okay-successful').click(function () {
            deleteElement('column')
        })
    }
})

// Удаление элемента строки/столбца (при подтверждении пользователем)
function deleteElement(relation) {
    let relation_id = 0
    if (relation === 'row') relation_id = element_row.val()
    else relation_id = element_column.val()
    fetch(`/drevo/delete_element_of_relation/?id=${relation_id}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (response.ok) {
            if (relation === 'row') {
                $('#element_row option:selected').remove();
                $('#element_row option:first').prop('selected', true);
                delete_element_modal.modal("hide");
            } else {
                $('#element_column option:selected').remove();
                $('#element_column option:first').prop('selected', true);
                delete_element_modal.modal("hide");
            }
        } else {
            if (relation === 'row')
                $('#delete_element_error_message').text('Невозможно удалить элемент строки, так как к нему привязана ячейка');
            else
                $('#delete_element_error_message').text('Невозможно удалить элемент столбца, так как к нему привязана ячейка');
            $('#delete_element_errors').modal('show');
        }
     })
}

// Открытие таблицы, если в ней есть хотя бы одна строка и столбец. В противном случае
// открытие окна с сообщением об ошибке
$("#open_table").on('click', function(){
    let table_id = table.val()
    if (table_id) {
        fetch(`/drevo/row_and_column_existence/?id=${table_id}`)
        .then(response => response.json())
        .then(data => {
            if (!data.is_row_and_column_exist) {
                $('.message-open-warning').text(`В таблице должны быть хотя бы одна строка и столбец!`)
                $('#table_open_errors').modal('show');
            }
            else {
                window.open(`/drevo/znanie/${table.val()}`);
            }
        })
        .catch((error) => {
            console.log('Error:', error);
        });
        }
});
