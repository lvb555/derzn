var element = $('#page').detach();
$('body').children().children('div.row').append(element);

let id_test = $("#id_test")
let id_question = $("#id_question")
let btn_show = $("#btn_show")
let create_new_answer = $('#create_new_answer')

$(document).ready(function () {
    $('#form').submit(function () {
        // Если пользователь не заполнил поле для нового ответа, всплывает модальное окно с предупреждением
        let unfilled_new_answers = $('#new_answer_div').length
        if (unfilled_new_answers !== 0) {
            $('.js-warning-create-answer').fadeIn();
            return false;
        }
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
    create_new_answer.removeAttr('hidden');
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
         $('#related_answers').empty()
         $('#add_new_answers').empty()
            for (let i = 0; i < data.length; i++) {
                let isCorrect = data[i]['tr__name'] === 'Ответ верный' ? 'checked' : '';
                $('#related_answers').append(
                    `<div id="answer_${data[i]['rz_id']}">
                        <label style="margin-left: 50px">Ответ:</label>
                        <div class="select-options" style="display: flex; align-items: center;">
                            <select class="select-without-choice" name="existing_answer_${data[i]['rz_id']}" id=""
                                    style="margin-left: 50px;">
                                <option value="${data[i]['rz_id']}" id="" selected>${data[i]['rz__name']}</option>
                            </select>
                            <span class="block-with-operations">
                                <input type="button" value="❌" class="quiet button-edit" id="delete_answer_${data[i]['rz_id']}"
                                       style="padding-left: 0px"
                                       onclick="deleteQuestionOrAnswer('answer', ${data[i]['rz_id']})">
                                <input type="button" value="✐" class="quiet button-edit" id="edit_answer_${data[i]['rz_id']}"
                                       style="padding-left: 0px" 
                                       onClick="editZnanie('answer', ${data[i]['rz_id']})">
                                <label class="is-correct-answer">
                                    <input type="checkbox" value="true" name="is_correct_answer_${data[i]['rz_id']}"
                                           style="width: 8mm; height: 8mm; margin-right: 5px" ${isCorrect}>
                                    Верно
                                </label>
                            </span>
                        </div>
                    </div>`
                )
            }

        // }
    })
    .catch((error) => {
    console.log('Error:', error);
    });
}

create_new_answer.click(function (e) {
    e.preventDefault();
    $('#add_new_answers').append(
        `<div id="new_answer_div">
            <label style="margin-left: 50px;">Новый ответ:</label>
            <div class="select-options">
                <select class="select-without-choice" name="new_answer" id=""
                        style="margin-left: 50px;">
                    <option value="" id="" selected disabled>Создайте ответ</option>
                </select>
                <span class="block-with-operations" style="margin-bottom: 14px">
                    <input type="button" value="➕" class="quiet button-edit" id="add_new_answer"
                           onClick="addZnanie('answer')" style="padding-left: 0px">
                    <input type="button" value="❌" class="quiet button-edit" id="delete_new_answer"
                           style="padding-left: 0px" hidden>
                    <input type="button" value="✐" class="quiet button-edit" id="edit_new_answer"
                           style="padding-left: 0px"
                           hidden>
                    <label class="is-correct-answer">
                        <input type="checkbox" name="is_correct_answer_new" style="width: 8mm; height: 8mm; margin-right: 5px">
                        Верно
                    </label>
                </span>
            </div>
        </div>`
    )
    create_new_answer.css('visibility', 'hidden');
})


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

function editZnanie(type_of_zn, id=null) {
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
        window.open(`/drevo/znanie_for_quiz_edit/${id}/answer/`, 'modal', 'Width=1280,Height=650');
    }
}

$('#delete_test').on('click', function () {
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
                    $('#related_answers').empty();
                    $('#add_new_answers').empty();
                    $('.row-column-question-block').hide();
                    $('#create_new_answer').hide();
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
})

function deleteQuestionOrAnswer(type_of_zn, id=null) {
    let znanie_id = null;
    if (type_of_zn === 'question') {
        znanie_id = id_question.val();
        $('.js-delete-question').fadeIn();
    } else {
        znanie_id = id;
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
                    $('#id_row option#create_question').prop('selected', true);
                    $('#related_answers').empty();
                    $('#add_new_answers').empty();
                    create_new_answer.css('visibility', 'hidden');
                }
                else {
                    $('.js-delete-answer').fadeOut();
                    $(`#answer_${id}`).hide();
                }
            })
            .catch((error) => {
                console.log('Error:', error);
            });
    })
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
    // Если тест выбран и в нем есть хотя бы один вопрос, то кнопка "Показать" активна
    if (test_id && (question_length > 1)) {
       window.open(`/drevo/quiz/${id_test.val()}`);
    }
});

function addEditListener(id) {
    $(`#edit_answer_${id}`).on('click', function() {
        editZnanie('answer', id);
    })
}

function addDeleteListener(id) {
    $(`#delete_answer_${id}`).on('click', function () {
        deleteQuestionOrAnswer('answer', id);
    })
}