var element = $('#page').detach();
$('body').children().children('div.row').append(element);

let id_table = $("#id_table")
let id_row = $("#id_row")
let id_column = $("#id_column")
let id_znanie = $("#id_znanie")
let btn_show = $("#btn_show")
let add_znanie = $("#add_znanie")


 function checkSelection() {
    if (document.form.row.value !== "" && document.form.column.value !== "") {
        id_znanie.prop('disabled', false);
        add_znanie.prop('disabled', false);
        id_znanie.selectpicker('refresh')
    }
}

id_row.change( function () {
    checkSelection();
});

id_column.change( function () {
    checkSelection();
});

function winOpen() {
    tab = window.open('/admin/drevo/znanie/add/', 'tab', 'Width=1280,Height=650')

    $(tab).ready(function () {
        $(tab.window).on('click', (event) => {
            if (event.target.getAttribute("name") == "_save"){
                setTimeout(function New() {
                    $('#div-param').css('display', 'flex')
                    newZnanie();
                    tab.close()
                }, 2000)
            }
        });
    }, true);
}

function newZnanie() {
    const data = {};
    let url = document.querySelector('script[data-show-znanie]').getAttribute('data-show-znanie')
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
        $('#id_znanie').append(`<option value="${data[0]}" id="${data[0]}" selected> ${data[1]} </option>`)
        $('#id_znanie').selectpicker('refresh')
        $('#id_znanie option:last').prop('selected', true)
        $('#id_znanie').selectpicker('refresh')
    })
    .catch((error) => {
    console.log('Error:', error);
    });
}

 btn_show.on('click', function(){
  window.open(`/drevo/znanie/${id_table.val()}`);
 });

$(document).ready(function () {
    $('#form').submit(function () {
        // Если какое-либо поле не заполнено, форма не отправляется
        if (document.form.table.value === '' || document.form.row.value === '' ||
            document.form.column.value === '' || document.form.znanie.value === ''){
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

$(document).mouseup(function (e) {
    var popup = $('.popup');
    if (e.target !== popup[0] && popup.has(e.target).length === 0) {
        $('.js-successful').fadeOut();
    }
})
