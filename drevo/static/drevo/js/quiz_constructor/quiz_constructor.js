let id_test = $("#id_test")
let id_question = $("#id_question")
let id_answer = $("#id_answer")
let btn_show = $("#btn_show")

$(document).ready(function () {
    $('#form').submit(function () {
        // Если тест еще не создан или вопрос не выбран, форма не отправляется
        if (document.form.test.value === '' || document.form.question.value === '') return false;
        $.ajax({
            method: "POST",
            url: document.querySelector('script[data-get-form-data]').getAttribute('data-get-form-data'),
            data: $('#form').serialize()
         }).done(function () {
            $('.js-successful').fadeIn();
         });
        return false;
     });
})


id_question.change(getAnswersToQuestion)

function getAnswersToQuestion(e) {
    const question_id = e.target.value;
    const data = {id: question_id};
    const url = document.querySelector('script[data-get-existing-answers]').getAttribute('data-get-existing-answers');
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
        $('#id_answer').prop('disabled', false);
        $('#answer_order').empty();
        $('#is_correct_answer').prop('checked', false);
        $('#add_answer').prop('disabled', false);
        $('#delete_question').prop('disabled', false);
        $('#edit_question').prop('disabled', false);
        id_answer.empty();
        if (data.length === 0) id_answer.append(`<option value="" selected disabled>Создайте ответ</option>`);
        else id_answer.append(`<option value="" selected disabled>Выберите ответ</option>`);
        for (let i = 0; i < data.length; i++) {
            id_answer.prop('disabled', false);
            id_answer.append(`<option value="${data[i]['rz_id']}" id="">${data[i]['rz__name']}</option>`)
        }
    })
    .catch((error) => {
    console.log('Error:', error);
    });
    let path = document.querySelector('script[data-get-order-of-question]').getAttribute('data-get-order-of-question');
    const question_id_for_attr = {id: id_question.val()};
    fetch(path, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(question_id_for_attr),
    })
    .then(response => response.json())
    .then(data => {
        $('#question_order').val(data['order']);
    })
    .catch((error) => {
        console.log('Error:', error);
    });

}

id_answer.change(getAnswerAttribute)

function getAnswerAttribute(e) {
    $('#is_correct_answer').prop('disabled', false);
    $('#answer_order').prop('disabled', false);
    $('#delete_answer').prop('disabled', false);
    $('#edit_answer').prop('disabled', false);
    let url = document.querySelector('script[data-get-answer-in-quiz-attributes]').getAttribute('data-get-answer-in-quiz-attributes');
    const data = {id: id_answer.val()};
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
            $('#answer_order').val(data['order']);
            $('#is_correct_answer').prop('checked', data['is_correct']);
        })
        .catch((error) => {
            console.log('Error:', error);
        });
}

function addZnanie(type_of_zn) {
    if (type_of_zn === 'test') {
        window.open(`/drevo/quiz_create/`, 'modal', 'Width=1280,Height=650');
    }
    else if (type_of_zn === 'question') {
        window.open(`/drevo/znanie_for_quiz_create/question/`, 'modal', 'Width=1280,Height=650');
    }
    else {
        window.open(`/drevo/znanie_for_quiz_create/answer/`, 'modal', 'Width=1280,Height=650');
    }
}

function editZnanie(type_of_zn) {
    if (type_of_zn ===  'test') {
        let edit_test = id_test.val()
        if (edit_test) {
            window.open(`/drevo/quiz_edit/${edit_test}/`, 'modal', 'Width=1280,Height=650');
        }
    }
    if (type_of_zn ===  'question') {
        let edit_question = id_question.val()
        if (edit_question) {
            window.open(`/drevo/znanie_for_quiz_edit/${edit_question}/question/`, 'modal', 'Width=1280,Height=650');
        }
    }
    if (type_of_zn ===  'answer') {
        let edit_answer = id_answer.val();
        if (edit_answer) {
             window.open(`/drevo/znanie_for_quiz_edit/${edit_answer}/answer/`, 'modal', 'Width=1280,Height=650');
        }
    }
}

function deleteZnanie(type_of_zn) {
    if (type_of_zn === 'test') {
         $('.js-delete-test').fadeIn();
        $('.js-okay-successful').click(function () {
            $('.js-delete-test').fadeOut();
            $('.js-delete-test-warning').fadeIn();
            $('.js-okay-delete-successful').click(function () {
                let url = document.querySelector('script[data-delete-quiz]').getAttribute('data-delete-quiz');
                const data = {id: id_test.val()};
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(data),
                })
                    .then(response => response.json())
                    .then(() => {
                        $('.row-column-question-block').hide();
                        let successful_quiz_delete = `Тест «${$('#id_test option:selected').text().trim()}» успешно удален!`;
                        $('.constructor-block').empty();
                        $('.constructor-block').append(
                            `<span>${successful_quiz_delete}</span>`
                        )
                        $('#div-param').hide();
                        $('.js-delete-test-warning').fadeOut();
                    })
                    .catch((error) => {
                        console.log('Error:', error);
                    });
            })
        })
    }
    else {
        let znanie_id = null;
        if (type_of_zn === 'question') {
            znanie_id = id_question.val();
            $('.js-delete-question').fadeIn();
        } else {
            znanie_id = id_answer.val();
            $('.js-delete-answer').fadeIn();
        }
        $('.js-okay-successful').click(function () {
            let url = document.querySelector('script[data-delete-answer-or-question-to-quiz]').getAttribute('data-delete-answer-or-question-to-quiz');
            const data = {id: znanie_id, type_of_zn: type_of_zn};
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(data),
            })
                .then(response => response.json())
                .then(() => {
                    if (type_of_zn === 'question') {
                        $('.js-delete-question').fadeOut();
                        $('#id_question option:selected').remove();
                        if ($('option').is('#create_question'))
                            $('#id_question option#create_question').prop('selected', true);
                        else
                            $('#id_question option#choose_question').prop('selected', true);
                    } else {
                        $('.js-delete-answer').fadeOut();
                        $('#id_answer option:selected').remove();
                        if ($('option').is('#create_answer'))
                            $('#id_answer option#create_answer').prop('selected', true);
                        else
                            $('#id_answer option#choose_answer').prop('selected', true);
                    }
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
        })
    }
}

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
    let test_id = id_test.val()
    let question_length = $('#id_question option').length
    // Если в тесте нет ответов, то кнопка "Показать" неактивна
    const id_of_question = {id: test_id};
    const url = document.querySelector('script[data-answers-in-quiz-existence]').getAttribute('data-answers-in-quiz-existence');
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(id_of_question),
    })
    .then(response => response.json())
    .then((data) => {
        if (data) {
            // Если тест выбран и в нем есть хотя бы один вопрос и хотя бы один ответ, а также нет вопросов без ответов,
            // то кнопка "Показать" активна
            if (test_id && (question_length > 1)) {
                window.open(`/drevo/quiz/${id_test.val()}`);
            }
        }
    })
    .catch((error) => {
        console.log('Error:', error);
    });

});
