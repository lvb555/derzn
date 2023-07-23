var element = $('#page').detach();
$('body').children().children('div.row').append(element);

let id_table = $("#id_table")
let id_row = $("#id_row")
let id_column = $("#id_column")
let id_element_row = $("#id_element_row")
let id_element_column = $("#id_element_column")
let row_is_group = $("#row_is_group")
let column_is_group = $("#column_is_group")

let delete_table = $("#delete_table")
let delete_row = $("#delete_row")
let delete_column = $("#delete_column")
let delete_element_row = $("#delete_element_row")
let delete_element_column = $("#delete_element_column")
let btn_show = $("#btn_show")

$(document).ready(function () {
    $('#form').submit(function () {
        // Если таблица еще не создана, форма не отправляется
        if ((document.form.table.value === '') || (document.form.row.value === '' && document.form.column.value === '' )){
            return false;
        }
        $('[name="row_element"]').val(null);
        $('[name="column_element"]').val(null);
        var formData = $(this).serialize();

        var selectedRowOptions = [];
       $('#id_element_row').find('option').each(function () {
            var optionValue = $(this).val();
            if (optionValue !== null && optionValue !== undefined && optionValue !== '') {
                selectedRowOptions.push(optionValue);
            }
        });
       if (selectedRowOptions.length > 0) {
            var selectedOptionsStringRow = selectedRowOptions.join(',');
            // console.log(selectedOptionsStringColumn)
            formData += '&' + 'row_element' + '=' + selectedOptionsStringRow;
       }

       var selectedColumnOptions = [];
       $('#id_element_column').find('option').each(function () {
            var optionValue = $(this).val();
            if (optionValue !== null && optionValue !== undefined && optionValue !== '') {
                selectedColumnOptions.push(optionValue);
            }
        });
       if (selectedColumnOptions.length > 0) {
            var selectedOptionsStringColumn = selectedColumnOptions.join(',');
            console.log(selectedOptionsStringColumn)
            formData += '&' + 'column_element' + '=' + selectedOptionsStringColumn;
       }

        $.ajax({
            method: "POST",
            url: document.querySelector('script[data-get-form]').getAttribute('data-get-form'),
            data: formData
        }).done(function (response) {
         if (response.row_is_group) row_is_group.val(true);
         if (response.column_is_group) column_is_group.val(true);
         $('.js-successful').fadeIn();
        });
        return false;
     });
})

function addZnanie(relation) {
    let table_id = id_table.val()
    if (relation === 'row') {
        $('#relation_type').val('row');
        window.open(`/drevo/new_knowledge_for_relation/row/${table_id}/`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'column') {
        $('#relation_type').val('column');
        window.open(`/drevo/new_knowledge_for_relation/column/${table_id}/`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'element_row') {
        $('#relation_type').val('element_row');
        window.open(`/drevo/group_of_element_create/row/`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'element_column') {
        $('#relation_type').val('element_column');
        window.open(`/drevo/group_of_element_create/column/`, 'modal', 'Width=1280,Height=650');
    }
    // Если создается таблица
    else {
        window.open(`/drevo/table_create/`, 'modal', 'Width=1280,Height=650');
    }
}


function editZnanie(relation) {
    if (relation === 'row') {
        let row_id = id_row.val()
        if (row_id)
            window.open(`/drevo/edit_knowledge_for_relation/${row_id}/row/`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'column') {
        let column_id = id_column.val()
        if (column_id)
            window.open(`/drevo/edit_knowledge_for_relation/${column_id}/column/`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'element_row') {
        let element_row_id = id_element_row.val()
        if (element_row_id)
            window.open(`/drevo/edit_knowledge_for_relation/${element_row_id}/element_row/`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'element_column') {
        let element_column_id = id_element_column.val()
        if (element_column_id)
            window.open(`/drevo/edit_knowledge_for_relation/${element_column_id}/element_column/`, 'modal', 'Width=1280,Height=650');
    }
    else {
        let table_id = id_table.val()
        if (table_id)
            window.open(`/drevo/table_update/${table_id}`, 'modal', 'Width=1280,Height=650');
    }
}

delete_table.on('click', function(){
    let table_id = id_table.val()
    if (table_id) {
        const data = { id: table_id, table: true, is_group: false};
        let url = document.querySelector('script[data-cell-exists]').getAttribute('data-cell-exists');
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
                if (data)
                    $('.js-table-delete-if-cell').fadeIn();
                else
                    $('.js-table-delete').fadeIn();
             })
            .catch((error) => {
            console.log('Error:', error);
            });

        $('.js-okay-successful').click(function () {
            let group_in_table = false;

            if (row_is_group.val() || column_is_group.val()) group_in_table = true;
           let url = document.querySelector('script[data-delete-table]').getAttribute('data-delete-table');
           const data = {id: table_id, group_in_table: group_in_table};
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
                $('#delete_table').hide()
                $('#add_row').hide()
                $('#add_column').hide()
                $('#delete_row').hide()
                $('#delete_column').hide()
                $('#id_table option:selected').remove();
                id_row.prop('disabled', true);
                id_row.find('option').remove();
                id_column.prop('disabled', true);
                id_column.find('option').remove();
                $('#edit_table').hide()
                $('#edit_row').hide()
                $('#edit_column').hide()
                $('.js-table-delete').fadeOut();
                if (row_is_group)  $('#row_elements').hide();
                if (column_is_group)  $('#column_elements').hide();
             })
            .catch((error) => {
            console.log('Error:', error);
            });
        })
    }
})

function deleteRelation(relation, is_group) {
    let relation_id = 0
    if (relation === 'row') relation_id = id_row.val()
    else relation_id = id_column.val()
    const data = { id: relation_id, is_group: is_group};
    let url = document.querySelector('script[data-delete-relations]').getAttribute('data-delete-relations');
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
        if (relation === 'row') {
            $('#id_row option:selected').remove();
            $('.js-row-delete').fadeOut();
            if (is_group) {
                $('#add_row').removeAttr('hidden');
                $('#row_elements').hide();
                $('#id_row option#create_row').prop('selected', true);
                row_is_group.val(false);
            }
        }
        else {
            $('#id_column option:selected').remove();
            $('.js-column-delete').fadeOut();
            if (is_group) {
                 $('#add_column').removeAttr('hidden');
                $('#column_elements').hide();
                $('#id_column option#create_column').prop('selected', true);
                column_is_group.val(false);
            }
        }
     })
    .catch((error) => {
        console.log('Error:', error);
    });

}

delete_row.on('click', function(){
    let row_id = id_row.val()
    if (row_id) {
        const data = { id: row_id, table: false, is_group: row_is_group};
        let url = document.querySelector('script[data-cell-exists]').getAttribute('data-cell-exists');
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
            if (data)
                $('.js-row-delete-if-cell').fadeIn();
            else
                $('.js-row-delete').fadeIn();
         })
        .catch((error) => {
        console.log('Error:', error);
        });

        $('.js-okay-successful').click(function () {
            deleteRelation('row', row_is_group);
        })
    }
})

delete_column.on('click', function(){
    let column_id = id_column.val()
    if (column_id) {
        const data = { id: column_id, table: false, is_group: column_is_group};
        let url = document.querySelector('script[data-cell-exists]').getAttribute('data-cell-exists');
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
            if (data)
                $('.js-column-delete-if-cell').fadeIn();
            else
                $('.js-column-delete').fadeIn();
         })
        .catch((error) => {
        console.log('Error:', error);
        });
        $('.js-okay-successful').click(function () {
            deleteRelation('column', column_is_group)
        })
    }
})

function deleteElement(relation) {
    let relation_id = 0
    if (relation === 'row') relation_id = id_element_row.val()
    else relation_id = id_element_column.val()
    const data = { id: relation_id };
    let url = document.querySelector('script[data-delete-element]').getAttribute('data-delete-element');
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
        if (relation === 'row') {
            $('#id_element_row option:selected').remove();
            $('#id_element_row option:first').prop('selected', true);
            $('.js-element-row-delete').fadeOut();
        }
        else {
            $('#id-element-column option:selected').remove();
            $('#id_element_column option:first').prop('selected', true);
            $('.js-element-column-delete').fadeOut();
        }
     })
    .catch((error) => {
        console.log('Error:', error);
    });

}

delete_element_row.on('click', function(){
    let element_row_id = id_element_row.val()
    if (element_row_id) {
        $('.js-element-row-delete').fadeIn();
        $('.js-okay-successful').click(function () {
            deleteElement('row')
        })
    }
})

delete_element_column.on('click', function(){
    let element_column_id = id_element_column.val()
    if (element_column_id) {
        $('.js-element-column-delete').fadeIn();
        $('.js-okay-successful').click(function () {
            deleteElement('column')
        })
    }
})

$('.js-close-successful').click(function () {
    $('.js-successful').fadeOut();
})

$('.js-cancel-successful').click(function () {
    $('.overlay').fadeOut();
})

$(document).mouseup(function (e) {
    var popup = $('.popup');
    if (e.target !== popup[0] && popup.has(e.target).length === 0) {
        $('.overlay').fadeOut();
    }
})

btn_show.on('click', function(){
    let table_id = id_table.val()
    if (table_id) {
       const data = { id: table_id};
        let url =  document.querySelector('script[data-relations-exists]').getAttribute('data-relations-exists');
        return fetch(url, {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json',
               'X-CSRFToken': csrftoken
           },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data) window.open(`/drevo/znanie/${id_table.val()}`);
        })
        .catch((error) => {
            console.log('Error:', error);
        });
        }
});
