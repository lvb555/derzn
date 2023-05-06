var element = $('#page').detach();
$('body').children().children('div.row').append(element);

let id_table = $("#id_table")
let id_row = $("#id_row")
let id_column = $("#id_column")

let delete_table = $("#delete_table")
let delete_row = $("#delete_row")
let delete_column = $("#delete_column")
let btn_show = $("#btn_show")

const csrftoken = getCookie('csrftoken');
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function addTable() {
    window.open(`/drevo/table_create/`, 'modal', 'Width=1280,Height=650');
}
function addRelation(relation) {
    if (relation === 'row') $('#relation_type').val('row')
    else $('#relation_type').val('column')
    window.open(`/drevo/new_knowledge_for_relation/`, 'modal', 'Width=1280,Height=650');
}

function editZnanie(relation) {
    if (relation === 'row') {
        let row_id = id_row.val()
        if (row_id)
            window.open(`/drevo/edit_knowledge_for_relation/${row_id}/row`, 'modal', 'Width=1280,Height=650');
    }
    else if (relation === 'column') {
        let column_id = id_column.val()
        if (column_id)
            window.open(`/drevo/edit_knowledge_for_relation/${column_id}/column`, 'modal', 'Width=1280,Height=650');
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
        $('.js-table-delete').fadeIn();
        $('.js-okay-successful').click(function () {
            const data = { id: table_id};
           let url = document.querySelector('script[data-delete-table]').getAttribute('data-delete-table');
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
             })
            .catch((error) => {
            console.log('Error:', error);
            });
        })
    }
})

function deleteRelation(relation) {
    let relation_id = 0
    if (relation === 'row') relation_id = id_row.val()
    else relation_id = id_column.val()
    const data = { id: relation_id};
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
        if (relation === 'row') $('#id_row option:selected').remove();
        else $('#id_column option:selected').remove();
        $('.js-table-delete').fadeOut();
     })
    .catch((error) => {
        console.log('Error:', error);
    });

}

delete_row.on('click', function(){
    let relation_id = id_row.val()
    if (relation_id) {
        $('.js-table-delete').fadeIn();
        $('.js-okay-successful').click(function () {
            deleteRelation('row')
        })
    }
})

delete_column.on('click', function(){
    let column_id = id_column.val()
    if (column_id) {
        $('.js-table-delete').fadeIn();
        $('.js-okay-successful').click(function () {
            deleteRelation('column')
        })
    }
})

$(document).ready(function () {
    $('#form').submit(function () {
        // Если таблица еще не создана, форма не отправляется
        if ((document.form.table.value === '') || (document.form.row.value === '' && document.form.column.value === '' )){
            return false;
         }
        $.ajax({
            method: "POST",
            url: document.querySelector('script[data-get-form]').getAttribute('data-get-form'),
            data: $(this).serialize()
         }).done(function () {
            $('.js-successful').fadeIn();
         });
        return false;
     });
})

$('.js-close-successful').click(function () {
    $('.js-successful').fadeOut();
})

$('.js-cancel-successful').click(function () {
    $('.js-table-delete').fadeOut();
})

$(document).mouseup(function (e) {
    var popup = $('.popup');
    if (e.target !== popup[0] && popup.has(e.target).length === 0) {
        if ($('.js-successful').is(':visible'))
            $('.js-successful').fadeOut();
        else
            $('.js-table-delete').fadeOut();
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
