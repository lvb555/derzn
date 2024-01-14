// Открытие алгоритма
$('#open_zn').click(function () {
    let main_zn_id = $('#main_zn_id').val()
    // Проверка корректности алгоритма
    fetch(`/drevo/check_algorithm_correctness_from_request/?id=${main_zn_id}`)
       .then(response => response.json())
       .then(data => {
           if (Object.entries(data).length !== 0) {
               $('#less_than_min_block').prop('hidden', true)
               if (data.less_than_min.length > 0) {
                   $('#less_than_min_block').prop('hidden', false)
                   $('#less_than_min').empty()
                   data.less_than_min.forEach(item => {
                        $('#less_than_min').append(`<ul>${item}</ul>`)
                   })
               }
               $('#algorithm_errors_modal').modal("show");
           }
           else {
               window.open(`/drevo/znanie/${main_zn_id}`);
           }
       });
})

// Открытие модального окна для копирования алгоритма
$('#btn_create_copy').click(function () {
    $('#algorithm-error').hide();
    $('#algorithm_create_copy_modal').modal("show");
})

// Фокусировка на поле ввода названия нового алгоритма
$('#algorithm_create_copy_modal').on('shown.bs.modal', function () {
    $('#name_for_copy').focus();
});

// Функция для полного копирования алгоритма
function copy(zn_id) {
    fetch('/drevo/make_copy_of_algorithm/', {
     method: 'POST',
     headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
     },
     body: JSON.stringify({
        id: zn_id,
        name: $('#name_for_copy').val(),
     }),
    })
    .then(response =>  response.json().then(data => ({status: response.status, ...data})))
    .then(data => {
        if (data.status === 409) { 
            $('#algorithm-error').show();
            return;
        }
        if (data.id)
            window.open(`/drevo/tree_constructor/algorithm/${data.id}`)
    })
}
$('#open_algorithm_with_errors').click(function () {
    let main_zn_id = $('#main_zn_id').val()
    window.open(`/drevo/znanie/${main_zn_id}`);
})