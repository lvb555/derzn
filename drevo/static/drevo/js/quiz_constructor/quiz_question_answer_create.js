const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
if (isNew === "true") {
    const testSelect = window.opener.document.getElementById('id_test');
    const addTest = window.opener.document.getElementById('add_test');
    const editTest = window.opener.document.getElementById('edit_test');
    const deleteTest = window.opener.document.getElementById('delete_test');
    const questionSelect = window.opener.document.getElementById('id_question');
    const addQuestion = window.opener.document.getElementById('add_question');
    const editQuestion = window.opener.document.getElementById('edit_question');
    const deleteQuestion = window.opener.document.getElementById('delete_question');
    const answerSelect = window.opener.document.getElementById('id_answer');
    const addAnswer = window.opener.document.getElementById('add_answer');
    const editAnswer = window.opener.document.getElementById('edit_answer');
    const deleteAnswer = window.opener.document.getElementById('delete_answer');

    const newZnanieId = document.querySelector('script[data-new-znanie-id]').getAttribute('data-new-znanie-id');
    const newZnanieName = document.querySelector('script[data-new-znanie-name]').getAttribute('data-new-znanie-name');
    const typeOfZn = document.querySelector('script[data-type-of-zn]').getAttribute('data-type-of-zn');
    if (typeOfZn === 'test') {
        testSelect.innerHTML = `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        questionSelect.disabled = false;
        addQuestion.disabled = false;
        addTest.style.display = 'none';
        editTest.removeAttribute('hidden');
        deleteTest.removeAttribute('hidden');
    }
    else if (typeOfZn === 'question') {
        questionSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        editQuestion.disabled = false;
        deleteQuestion.disabled = false;
        addAnswer.disabled = false;
        answerSelect.disabled = false;
        answerSelect.innerHTML = "";
        answerSelect.innerHTML += `<option value="" selected disabled>Создайте ответ</option>`;
    }
    else if (typeOfZn === 'answer') {
        answerSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        editAnswer.disabled = false;
        deleteAnswer.disabled = false;
    }
    window.close()
}