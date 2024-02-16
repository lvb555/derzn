let bz = $('#bz');
let tr = $('#tr');
let rz = $('#rz');
let order = $('#order');
let rz_list = [];

let add_rel_zn = $('#add_rel_zn');
let edit_rel_zn = $('#edit_rel_zn');
let create_edit_relation_modal = $('#create_edit_relation_modal');
let edit_main_algorithm = document.getElementById('edit_main_zn_form');
let edit_zn = document.getElementById('edit_zn_form');
let create_zn = document.getElementById('create_zn');
let for_rel_type = $('#for_rel_type');
let last_tr_id = $('#last_tr_id');
let last_rz_id = $('#last_rz_id');
let current_action = $('#current_action');

let new_zn_tz = $('#create_zn_modal #id_tz');
let editing_zn_name = $('#edit_zn_modal #id_name');
let zn_id_in_edit_form = $('#edit_zn_form #edited_zn_id');
let zn_id_in_create_form = $('#create_zn_form #edited_zn_id');

// Кнопки «Конструктор шаблона текста» в форме создания и редактирования знания
let textOfDocumentTemplateButtonForCreateZn = $('<button class="btn btn-info mt-3">').text('Конструктор шаблона текста');
new_zn_tz.after(textOfDocumentTemplateButtonForCreateZn);
let textOfDocumentTemplateButtonForEditZn = $('<button class="btn btn-info mt-3">').text('Конструктор шаблона текста');
editing_zn_name.after(textOfDocumentTemplateButtonForEditZn);

function add_relation(parent_zn_id) {
    fetch(`/drevo/rel_in_tree_constructor/create/?parent_id=${parent_zn_id}`)
        .then(response => {
            if (response.status === 409) {
                $('#error_create_relation_modal').modal('show');
                $('#error_create_relation_message').text(`Для базового знания уже создано максимальное количество
                связей! Вы можете удалить существующие связи, чтобы добавить новую.`)

            }
            return response.json();
        })
        .then(data => {
            order.val(null);
            current_action.val('create');
            add_rel_zn.css('cursor','default').attr("class", "text-secondary");
            edit_rel_zn.css('cursor','default').attr("class", "text-secondary");
            $('#title_create_edit_rel_modal').text(`Создание связи`);
            $('#bz').empty().append(`<option id="${data['bz']['id']}" value="${data['bz']['id']}">${data['bz']['name']}</option>`);
            tr.empty();
            if (data['relations'].length !== 1) {
               tr.append(`<option selected disabled>-----</option>`);
               tr.css('pointer-events', 'auto');
            }
            data['relations'].forEach(item => {
                tr.append(`<option id="${item['id']}" value="${item['id']}">${item['name']}</option>`)
            })
            if (data['relations'].length === 1) {
                tr.css('pointer-events', 'none');
                add_rel_zn.css('cursor','pointer').attr("class", "text-success");
                rz.prop('disabled', false).empty().select2().append(`<option selected disabled>-----</option>`);
                data.rel_zn.forEach(item => {
                    const option = $('<option>').val(item.id).text(item.name);
                    rz.append(option);
                });
                new_zn_tz.empty()
                if (data.rel_tz.length !== 1) new_zn_tz.append(`<option selected disabled>-----</option>`).prop('disabled', false);
                data.rel_tz.forEach(item => {
                    const option = $('<option>').val(item.id).text(item.name);
                    if (data.rel_tz.length === 1) textOfDocumentTemplateButtonForCreateZn.prop('hidden', false)
                    else textOfDocumentTemplateButtonForCreateZn.prop('hidden', true);
                    new_zn_tz.append(option);
                });
            }
            else {
                rz.empty();
            }
            if (data['bz']['editable']) $('#bz_edit').show();
            else $('#bz_edit').hide();
            create_edit_relation_modal.modal("show");
        });
}


textOfDocumentTemplateButtonForCreateZn.click(function () {
    if (!$('#create_zn #id_name').val()) return
    if (!zn_id_in_create_form.val()) {
        let uuid = $('#new_zn_form_create_uuid').val();
        $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData());
        const formData = new FormData(create_zn);
        fetch('/drevo/create_zn_in_tree_constructor/', {
         method: 'POST',
         body: formData,
        })
        .then(response => response.json())
        .then(data => {
            zn_id_in_create_form.val(`${data.zn_id}`)
            window.open(`drevo/znanie/${$('#main_zn_id').val()}/document-template/edit-text/${data.zn_id}`, 'modal', 'Width=1280,Height=650');
        });
    }
    else window.open(`drevo/znanie/${$('#main_zn_id').val()}/document-template/edit-text/${zn_id_in_create_form.val()}`, 'modal', 'Width=1280,Height=650');
})

function edit_relation(rel_id) {
    fetch(`/drevo/rel_in_tree_constructor/edit/?rel_id=${rel_id}`)
        .then(response => response.json())
        .then(data => {
            current_action.val('edit');
            $('#title_create_edit_rel_modal').text(`Редактирование связи`);
            $('#bz').empty().append(`<option id="${data['bz']['id']}" value="${data['bz']['id']}">${data['bz']['name']}</option>`);
            if (data['bz']['editable']) $('#bz_edit').show();
            else $('#bz_edit').hide();
            tr.empty().append(`<option disabled>-----</option>`)
                .append((`<option id="${data['selected_tr']['id']}" value="${data['selected_tr']['id']}" selected>${data['selected_tr']['name']}</option>`));
            if (data['other_tr'].length !== 0) {
                data['other_tr'].forEach(item => {
                    tr.append(`<option id="${item['id']}" value="${item['id']}">${item['name']}</option>`)
                });
                tr.css('pointer-events', 'auto');
            }
            else tr.css('pointer-events', 'none');
            $.map(data.other_rz, (obj) => obj.text = obj.name);
            rz_list = data.other_rz;
            rz_list.push({id: data.selected_rz.id, text: data.selected_rz.name, selected: true})
            rz.prop('disabled', false).empty().removeAttr('hidden').select2({
                data: rz_list
            })
            last_tr_id.val(`${data['selected_tr']['id']}`);
            last_rz_id.val(`${data.selected_rz.id}`);
            if (data.selected_order.id) order.val(`${data.selected_order.id}`)
            else order.val(null);
            add_rel_zn.css('cursor','pointer').attr("class", "text-success");
            if (data['selected_rz']['editable']) edit_rel_zn.css('cursor','pointer').attr("class", "text-primary").show();
            else edit_rel_zn.hide();
            new_zn_tz.empty()
            if (data.rel_tz.length !== 1) new_zn_tz.append(`<option selected disabled>-----</option>`).prop('disabled', false);
            data.rel_tz.forEach(item => {
                const option = $('<option>').val(item.id).text(item.name);
                if (data.rel_tz.length === 1) textOfDocumentTemplateButtonForCreateZn.prop('hidden', false)
                else textOfDocumentTemplateButtonForCreateZn.prop('hidden', true);
                new_zn_tz.append(option);
            });
            create_edit_relation_modal.modal("show");
        });
}


textOfDocumentTemplateButtonForEditZn.click(function () {
    window.open(`/drevo/znanie/${$('#main_zn_id').val()}/document-template/edit-text/${zn_id_in_edit_form.val()}`);
})

// Получение видов связей, учитывая выбранное базовое знание
tr.change(function() {
    let bz_id = bz.val();
    let tr_id = tr.val();
    order.val(null);
    fetch(`/drevo/get_rel_zn_in_tree_constructor_from_request/?bz_id=${bz_id}&tr_id=${tr_id}`)
        .then(response => response.json())
        .then(data => {
            if (Object.entries(data).length !== 0) {
                rz.prop('disabled', false).empty().select2().append(`<option selected disabled>-----</option>`);
                data.rel_zn.forEach(item => {
                    const option = $('<option>').val(item.id).text(item.name);
                    rz.append(option);
                });
                new_zn_tz.empty().append(`<option selected disabled>-----</option>`).prop('disabled', false);
                data.rel_tz.forEach(item => {
                    const option = $('<option>').val(item.id).text(item.name);
                    new_zn_tz.append(option);
                });
            }
            add_rel_zn.css('cursor','pointer').attr("class", "text-success");
        });
})

// Получение порядка выбранной связи (при выборе связанной связи) и проверка, является ли пользователь создателем св. знания
rz.change(function() {
    let bz_id = bz.val();
    let tr_id = tr.val();
    let rz_id = rz.val();
    fetch(`/drevo/is_current_user_creator_of_zn/?id=${rz_id}`)
        .then(response => response.json())
        .then(data => {
            if (data['editable']) edit_rel_zn.show().css('cursor','pointer').attr("class", "text-primary");
            else edit_rel_zn.hide();
        });
    fetch(`/drevo/get_order_of_relation/?bz_id=${bz_id}&tr_id=${tr_id}&rz_id=${rz_id}`)
        .then(response => response.json())
        .then(data => {
            if (data['order']) order.val(`${data['order']}`);
            else order.val(null);
        });
})
function delete_relation(bz_id, rz_id) {
    $('.delete-confirmation').text(`Вы уверены, что хотите удалить связь?`);
    $('#delete_relation_modal').modal("show");
    $('.js-okay-successful').click(function () {
        fetch(`/drevo/delete_relation_in_tree_constructor/?bz_id=${bz_id}&rz_id=${rz_id}`, {
         method: 'DELETE',
         headers: {
             'Content-Type': 'application/json',
             'X-CSRFToken': csrftoken
         }
         })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect_url;
            $('#create_relation').modal("hide");
        });
    })
}
function add_znanie() {
    $('#title_create_edit_rel_modal').text(`Создание связи`);
    create_zn.reset();
    zn_id_in_create_form.val(null);
    $('#create_zn_modal').modal('show');
}

create_zn.addEventListener('submit', (event) => {
    event.preventDefault();
    let uuid = $('#new_zn_form_edit_uuid').val();
    $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData())
    if (zn_id_in_create_form.val()) {
        const formData = new FormData(create_zn);
        fetch(`/drevo/edit_znanie_in_tree_constructor/`, {
         method: 'POST',
         body: formData,
        })
        .then(data => {
            rz.append(`<option value="${data.zn_id}" selected>${data.zn_name}</option>`);
            $('#create_zn_modal').modal('hide');
        });
    }
    else {
        const formData = new FormData(create_zn);
        fetch('/drevo/create_zn_in_tree_constructor/', {
         method: 'POST',
         body: formData,
        })
        .then(response => response.json())
        .then(data => {
            rz.append(`<option value="${data.zn_id}" selected>${data.zn_name}</option>`);
            $('#create_zn_modal').modal('hide');
        });
    }
})


function edit_znanie(for_type) {
    $('#title_create_edit_rel_modal').text(`Редактирование связи`);
    let zn_id;
    if (for_type === 'for_bz') zn_id = bz.val();
    else zn_id = rz.val();
    for_rel_type.val(for_type);
    fetch(`/drevo/edit_znanie_in_tree_constructor/?zn_id=${zn_id}`)
    .then(response => response.json())
    .then(data => {
        $('#edit_zn_form #id_name').val(`${data.zn_name}`);
        if (data.zn_href) $('#edit_zn_form #id_href').val(`${data.zn_href}`);
        if (data.zn_source_com) $('#edit_zn_form #id_source_com').val(`${data.zn_source_com}`);
        const uuid = $('#new_zn_form_edit_uuid').val();
        if (data.zn_content) {
            CKEDITOR.instances[uuid].setData(data.zn_content);
        }
        $('#edit_zn_images_form').html(data.images_form);
        $('#edit_zn_file_form').html(data.file_form);
        zn_id_in_edit_form.val(`${zn_id}`);

        $('#edit_zn_modal').modal('show');
    });
}
edit_zn.addEventListener('submit', (event) => {
    event.preventDefault();
    let uuid = $('#new_zn_form_edit_uuid').val();
    $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData())
    const formData = new FormData(edit_zn);
    fetch(`/drevo/edit_znanie_in_tree_constructor/`, {
     method: 'POST',
     body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (for_rel_type.val() === 'for_bz') {
            bz.find(`option[value="${data.zn_id}"]`).text(`${data.zn_name}`);
        }
        else {
            index = rz_list.findIndex((zn => zn.id === data.zn_id));
            if (rz_list[index]?.text) {
                rz_list[index].text = data.zn_name
            }
            rz.empty().select2({
                data: rz_list
            })
        }
        $('#edit_zn_modal').modal('hide');
    });
})
function editMainZnanie() {
    $('#main_zn_edit_modal').modal("show");
}

function deleteMainZnanie(type_of_zn, zn_id) {
    if (type_of_zn === 'algorithm') {
        $('.delete-confirmation').text(`Вы действительно хотите удалить этот алгоритм? Все связанные знания (кроме внутренних знаний «Алгоритм») также удалятся!`)
        $('#delete_element_warning').modal("show");
        $('.js-okay-successful').click(function () {
            fetch(`/drevo/delete_algorithm/?id=${zn_id}`)
                .then(response => {
                    $('#delete_element_warning').modal("hide");
                    $('#success_delete_main_zn').modal("show");
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
        })
    }
    else if (type_of_zn === 'document') {
        $('.delete-confirmation').text(`Вы действительно хотите удалить этот документ? Все связанные знания также удалятся!`)
        $('#delete_element_warning').modal("show");
        $('.js-okay-successful').click(function () {
            fetch(`/drevo/delete_complex_zn/?id=${zn_id}`)
                .then(response => {
                    $('#delete_element_warning').modal("hide");
                    $('#success_delete_main_zn').modal("show");
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
        })
    }
}
edit_main_algorithm.addEventListener('submit', (event) => {
    event.preventDefault();
    let uuid = $('#main_zn_edit_form_uuid').val();
    $(`#${uuid}`).val(CKEDITOR.instances[uuid].getData())
    const formData = new FormData(edit_main_algorithm);
    fetch('/drevo/edit_main_zn_in_constructor/', {
     method: 'POST',
     body: formData,
    })
    .then(response => response.json())
    .then(data => {
        const znId = $('#main_zn_id').val();
        const elementId = `znanie_id_${znId}`;
        $(`#${elementId}`).text(`${data.zn_name}`);
        $('#main_zn_edit_modal').modal('hide');
    });
})

$('#save_new_relation').click(function () {
    if (bz.val() && tr.val() && rz.val()) {
        let data = {
                bz_id: bz.val(), tr_id: tr.val(),
                rz_id: rz.val(), order: order.val(), action: current_action.val()
            };
        if (current_action.val() === 'edit') {
            data.last_tr_id = last_tr_id.val();
            data.last_rz_id = last_rz_id.val();
        }

        fetch('/drevo/save_rel_in_tree_constructor/', {
             method: 'POST',
             body: JSON.stringify(data),
             headers: {
                 'Content-Type': 'application/json',
                 'X-CSRFToken': csrftoken
             }
           })
            .then(response => response.json())
            .then(data => {
                window.location.href = data.redirect_url;
                $('#create_edit_relation_modal').modal("hide");
            });
    }
})
function questions_and_answers_for_zn(zn_pk){
  window.open(`/drevo/znanie/${zn_pk}/questions_and_check_answers`);
}