let test = $("#id_test")
let question = $("#id_question")
let answer = $("#id_answer")

question.change(getAnswersToQuestion)

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
        $('#answer').prop('disabled', false);
        $('#answer_order').empty();
        $('#is_correct_answer').prop('checked', false);
        $('#add_answer').prop('disabled', false);
        $('#delete_question').prop('disabled', false);
        $('#edit_question').prop('disabled', false);
        answer.empty();
        if (data.length === 0) answer.append(`<option value="" selected disabled>Создайте ответ</option>`);
        else answer.append(`<option value="" selected disabled>Выберите ответ</option>`);
        for (let i = 0; i < data.length; i++) {
            answer.prop('disabled', false);
            answer.append(`<option value="${data[i]['rz_id']}" id="">${data[i]['rz__name']}</option>`)
        }
    })
    .catch((error) => {
    console.log('Error:', error);
    });
}

answer.change(getAnswerAttribute)

function getAnswerAttribute(e) {
    $('#delete_answer').prop('disabled', false);
    $('#edit_answer').prop('disabled', false);
}

function addZnanie(type_of_zn) {
    if (type_of_zn === 'test') {
        window.open(`/drevo/main_znanie_in_constructor_create/test/`, 'modal', 'Width=1280,Height=650');
    }
    else if (type_of_zn === 'question') {
        let id_test = test.val()
        window.open(`/drevo/znanie_for_quiz_create/question/${id_test}/`, 'modal', 'Width=1280,Height=650');
    }
    else {
        let id_question = question.val()
        window.open(`/drevo/znanie_for_quiz_create/answer/${id_question}/`, 'modal', 'Width=1280,Height=650');
    }
}

function editZnanie(type_of_zn) {
    let id_test = test.val()
    let id_question = question.val()
    if (type_of_zn ===  'test') {
        if (id_test) {
            window.open(`/drevo/main_znanie_in_constructor_edit/test/${id_test}/`, 'modal', 'Width=1280,Height=650');
        }
    }
    if (type_of_zn ===  'question') {
        if (edit_question) {
            window.open(`/drevo/znanie_for_quiz_edit/${id_question}/question/${id_test}/`, 'modal', 'Width=1280,Height=650');
        }
    }
    if (type_of_zn ===  'answer') {
        let id_answer = answer.val();
        if (id_answer) {
             window.open(`/drevo/znanie_for_quiz_edit/${id_answer}/answer/${id_question}/`, 'modal', 'Width=1280,Height=650');
        }
    }
}

function deleteZnanie(type_of_zn) {
    if (type_of_zn === 'test') {
        $('.delete-confirmation').text(`Вы действительно хотите удалить этот тест? Все связанные вопросы и ответы также удалятся!`)
        $('.js-delete-element').fadeIn();
        $('.js-okay-successful').click(function () {
            $('.js-delete-element').fadeOut();
            $('.delete-confirmation').text(`Вы уверены?`)
            $('.js-delete-element').fadeIn();
            $('.js-okay-delete-successful').click(function () {
                let url = document.querySelector('script[data-delete-quiz]').getAttribute('data-delete-quiz');
                const data = {id: test.val()};
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
                        let successful_quiz_delete = `Тест «${$('#test option:selected').text().trim()}» успешно удален!`;
                        $('.constructor-block').empty();
                        $('.constructor-block').append(
                            `<span>${successful_quiz_delete}</span>`
                        )
                        $('#div-param').hide();
                        $('.js-delete-element').fadeOut();
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
            znanie_id = question.val();
            $('.delete-confirmation').text(`Вы действительно хотите удалить этот вопрос? Ответы вопроса также удалятся!`)
            $('.js-delete-element').fadeIn();
        } else {
            znanie_id = answer.val();
            $('.delete-confirmation').text(`Вы действительно хотите удалить этот ответ?`)
            $('.js-delete-element').fadeIn();
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
                        $('.js-delete-element').fadeOut();
                        $('#question option:selected').remove();
                        if ($('option').is('#create_question'))
                            $('#question option#create_question').prop('selected', true);
                        else
                            $('#question option#choose_question').prop('selected', true);
                    } else {
                        $('.js-delete-element').fadeOut();
                        $('#answer option:selected').remove();
                        if ($('option').is('#create_answer'))
                            $('#answer option#create_answer').prop('selected', true);
                        else
                            $('#answer option#choose_answer').prop('selected', true);
                    }
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
        })
    }
}

$("#btn_show").on('click', function(){
    let test_id = test.val()
    let question_length = $('#question option').length
    if (question_length === 1) {
        $('#heading-error').hidden = true;
        $('.message-open-warning').text('В тесте нет вопросов!');
        $('.js-open-warning').fadeIn();
    }
    else {
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
                let questions_less_two_answers_exist = data['questions_less_two_answers'].length
                let questions_without_correct_answer_exist = data['questions_without_correct_answer'].length
                if ((questions_less_two_answers_exist === 0)
                    && (questions_without_correct_answer_exist=== 0)) {
                    window.open(`/drevo/quiz/${test.val()}`);
                }
                else {
                    $('#heading-error').removeAttr('hidden');
                    $('#heading_questions_less_two_answers_list').hidden = true;
                    $('#heading_questions_without_correct_answer_list').hidden = true;
                    $('#questions_without_answer_list').empty();
                    $('#questions_less_two_answers_list').empty();
                    $('#questions_without_correct_answer_list').empty();

                    if (questions_less_two_answers_exist !== 0) {
                        $('#heading_questions_less_two_answers_list').removeAttr('hidden');
                        data['questions_less_two_answers'].forEach((question) => {
                            $('#questions_less_two_answers_list').append($('<li>').text(question));
                        });
                    }

                    if (questions_without_correct_answer_exist !== 0) {
                        $('#heading_questions_without_correct_answer_list').removeAttr('hidden');
                        data['questions_without_correct_answer'].forEach((question) => {
                            $('#questions_without_correct_answer_list').append($('<li>').text(question));
                        });
                    }

                    $('.js-open-warning').fadeIn();
                }

            }
        })
        .catch((error) => {
            console.log('Error:', error);
        });
    }

});

$('.js-close-successful').click(function () {
    $('.overlay').fadeOut();
})