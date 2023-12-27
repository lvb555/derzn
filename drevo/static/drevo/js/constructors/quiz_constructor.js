let test = $("#test")
let question = $("#question")
let answer = $("#answer")

let create_edit_zn_form = $('#create_edit_zn_form');
let edit_main_zn_form = $('#main_zn_edit_form');
let type_of_tr = $('#type_of_tr');
let action = $('#action');
let edited_zn_id = $('#edited_zn_id');

question.change(function () { allow_actions($('#edit_question'), $('#delete_question')); });
answer.change(function () { allow_actions($('#edit_answer'), $('#delete_answer')); });

// При выборе вопроса в список ответов помещаются все связанные ответы
question.change(getAnswersToQuestion)
function getAnswersToQuestion(e) {
    const question_id = e.target.value;
    fetch(`/drevo/get_answers_to_selected_question_of_quiz/?id=${question_id}`)
    .then(response => response.json())
    .then(data => {
        answer.prop('disabled', false);
        $('#add_answer').css('pointer-events', 'auto').css('cursor', 'pointer').attr("class", "text-success");
        answer.empty();
        if (data.length === 0) answer.append(`<option value="" selected disabled>Создайте ответ</option>`);
        else answer.append(`<option value="" selected disabled>Выберите ответ</option>`);
        for (let i = 0; i < data.length; i++) {
            answer.prop('disabled', false);
            answer.append(`<option value="${data[i]['rz_id']}" id="${data[i]['rz_id']}">${data[i]['rz__name']}</option>`)
        }
    })
    .catch((error) => {
    console.log('Error:', error);
    });
}

// Добавление в модальное окно формы для создания знания
function addZnanie(type_of_current_tr) {
    type_of_tr.val(type_of_current_tr);
    action.val('create');
    if (type_of_current_tr === 'question') {
        fetch(`/drevo/question_create_update_in_quiz/?action=create`)
            .then(response => response.json())
            .then(data => {
                $('#info_about_question').prop('hidden', true);
                $('#create_edit_zn_title').text(`Создание вопроса теста`);
                $('#zn_form').empty().html(`${data.zn_form}`);
                $('#order_of_rel_form').html(`${data.order_of_rel_form}`);
                $('#answer_attrs_form').empty();
                $('#create_edit_zn_modal').modal('show');
             })
    }
    else if (type_of_current_tr === 'answer') {
        $('#question_id').val(question.val())
        fetch(`/drevo/answer_create_update_in_quiz/?action=create`)
            .then(response => response.json())
            .then(data => {
                $('#create_edit_zn_title').text(`Создание ответа теста`);
                $('#info_about_question').removeAttr('hidden');
                $('#name_of_question').text($('#question option:selected').text());
                $('#zn_form').html(`${data.zn_form}`);
                $('#order_of_rel_form').html(`${data.order_of_rel_form}`);
                $('#answer_attrs_form').html(`${data.answer_correct_form}`);
                $('#create_edit_zn_modal').modal('show');
             })
    }
}

// Отправка созданного/модифицированного знания
create_edit_zn_form.on('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(create_edit_zn_form[0]);
    if (type_of_tr.val() === 'question') {
        fetch('/drevo/question_create_update_in_quiz/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (action.val() === 'create') {
                answer.empty().append(`<option value="" selected disabled>Создайте ответ</option>`).prop('disabled', false);
                question.append(`<option id="${data.zn_id}" value="${data.zn_id}" selected>${data.zn_name}</option>`);
            }
            else {
                $(`#question option[id="${data.zn_id}"]`).text(data.zn_name);
            }
            $('#add_answer').css('cursor', 'pointer').attr("class", "text-success");
            allow_actions($('#edit_question'), $('#delete_question'));
            $('#create_edit_zn_modal').modal('hide');
        });
    }
    else if (type_of_tr.val() === 'answer') {
        fetch('/drevo/answer_create_update_in_quiz/', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (action.val() === 'create')
                    answer.append(`<option id="${data.zn_id}" value="${data.zn_id}" selected>${data.zn_name}</option>`);
                else
                    $(`#answer option[id="${data.zn_id}"]`).text(data.zn_name);
                allow_actions($('#edit_answer'), $('#delete_answer'));
                $('#create_edit_zn_modal').modal('hide');
            });
    }
})


// Добавление в модальное окно формы для редактирования знания
function editZnanie(type_of_current_tr) {
    let question_id = question.val();
    type_of_tr.val(type_of_current_tr);
    action.val('edit');
    if (type_of_current_tr ===  'test') {
        $('#main_zn_edit_modal').modal("show");
    }
    else if (type_of_current_tr === 'question') {
        edited_zn_id.val(question_id);
        fetch(`/drevo/question_create_update_in_quiz/?action=edit&zn_id=${question_id}`)
            .then(response => response.json())
            .then(data => {
                $('#info_about_question').prop('hidden', true);
                $('#create_edit_zn_title').text(`Редактирование вопроса теста`);
                $('#zn_form').empty().html(`${data.zn_form}`);
                $('#order_of_rel_form').empty().html(`${data.order_of_rel_form}`);
                $('#answer_attrs_form').empty();
                $('#type_of_tr').val('question');
                $('#create_edit_zn_modal').modal('show');
             })
    }
    else if (type_of_current_tr === 'answer') {
        let answer_id = answer.val();
        edited_zn_id.val(answer_id);
        $('#question_id').val(question_id)
        fetch(`/drevo/answer_create_update_in_quiz/?action=edit&zn_id=${answer_id}`)
            .then(response => response.json())
            .then(data => {
                $('#info_about_question').removeAttr('hidden');
                $('#name_of_question').text($('#question option:selected').text());
                $('#create_edit_zn_title').text(`Редактирование ответа на вопрос теста`);
                $('#zn_form').empty().html(`${data.zn_form}`);
                $('#order_of_rel_form').empty().html(`${data.order_of_rel_form}`);
                $('#answer_attrs_form').empty().html(`${data.answer_correct_form}`);
                $('#type_of_tr').val('answer');
                $('#create_edit_zn_modal').modal('show');
             })
    }
    
}

// Отправка модифицированного главного знания - теста
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
        $(`#test option[id="${data.zn_id}"]`).text(data.zn_name);
        $('#main_zn_edit_modal').modal('hide');
    })
})

// Удаление знания (при подтверждении пользователем)
function deleteZnanie(type_of_zn) {
    if (type_of_zn === 'test') {
        $('.delete-confirmation').text(`Вы действительно хотите удалить этот тест? Все связанные вопросы и ответы также удалятся!`)
        $('#delete_element_warning').modal("show");
        $('.js-okay-successful').click(function () {
            fetch(`/drevo/delete_quiz/?id=${test.val()}`)
                .then(response => {
                    $('.row-column-question-block').hide();
                    $('#open_quiz').hide();
                    let successful_quiz_delete = `Тест «${$('#test option:selected').text().trim()}» успешно удален!`;
                    $('.constructor-block').empty().append(
                        `<span>${successful_quiz_delete}</span>`
                    )
                    $('#delete_element_warning').modal("hide");
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
            })
    }
    else {
        let znanie_id = null;
        if (type_of_zn === 'question') {
            znanie_id = question.val();
            $('.delete-confirmation').text(`Вы действительно хотите удалить этот вопрос? Ответы вопроса также удалятся!`)
            $('#delete_element_warning').modal("show");
        } else {
            znanie_id = answer.val();
            $('.delete-confirmation').text(`Вы действительно хотите удалить этот ответ?`)
            $('#delete_element_warning').modal("show");
        }
        $('.js-okay-successful').click(function () {
            fetch(`/drevo/delete_answers_or_questions_to_quiz/?id=${znanie_id}&type_of_zn=${type_of_zn}`)
                .then(response => {
                    if (type_of_zn === 'question') {
                        $('#question option:selected').remove();
                        if (question.children().length === 1) {
                            disable_actions($('#edit_question'), $('#delete_question'));
                            question.empty().append(`<option selected disabled>Создайте вопрос</option>`)
                        }
                    } else {
                        $('#answer option:selected').remove();
                        if (answer.children().length === 1) {
                            disable_actions($('#edit_answer'), $('#delete_answer'));
                            answer.empty().append(`<option selected disabled>Создайте ответ</option>`)
                        }
                    }
                    $('#delete_element_warning').modal("hide");
                })
                .catch((error) => {
                    console.log('Error:', error);
                });
        })
    }
}

// Перед открытием теста происходит проверка корректности теста. Возможно выявление следующих ошибок: в тесте нет
// вопросов, есть вопросы без верного ответа, есть вопросы с менее чем двумя ответами. Если ошибка(и) возникает(ют),
// то открывается модальное окно с соответствующим сообщением. Если ошибок нет, открывается тест.
$("#open_quiz").on('click', function(){
    let test_id = test.val()
    let question_length = $('#question option').length
    $('#no_questions').prop('hidden', true);
    $('#questions_without_answer').prop('hidden', true);
    $('#questions_less_two_answers').prop('hidden', true);
    $('#questions_without_correct_answer').prop('hidden', true);
    if (question_length === 1) {
        $('#no_questions').removeAttr('hidden');
        $('#quiz_open_errors').modal("show");
    }
    else {
       fetch(`/drevo/answers_in_quiz_existence/?id=${test_id}`)
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
                    $('#questions_without_answer_list').empty();
                    $('#questions_less_two_answers_list').empty();
                    $('#questions_without_correct_answer_list').empty();

                    if (questions_less_two_answers_exist !== 0) {
                        $('#questions_less_two_answers').removeAttr('hidden');
                        data['questions_less_two_answers'].forEach((question) => {
                            $('#questions_less_two_answers_list').append($('<li>').text(question));
                        });
                    }

                    if (questions_without_correct_answer_exist !== 0) {
                        $('#questions_without_correct_answer').removeAttr('hidden');
                        data['questions_without_correct_answer'].forEach((question) => {
                            $('#questions_without_correct_answer_list').append($('<li>').text(question));
                        });
                    }

                    $('#quiz_open_errors').modal("show");
                }

            }
        })
        .catch((error) => {
            console.log('Error:', error);
        });
    }
});
