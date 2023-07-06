const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
if (isNew === "true") {
    const testSelect = window.opener.document.getElementById('id_test');
    const addTest = window.opener.document.getElementById('add_test');
    const editTest = window.opener.document.getElementById('edit_test');
    const deleteTest = window.opener.document.getElementById('delete_test');
    const questionSelect = window.opener.document.getElementById('id_question');
    const addNewQuestion = window.opener.document.getElementById('add_question');
    const editQuestion = window.opener.document.getElementById('edit_question');
    const deleteQuestion = window.opener.document.getElementById('delete_question');
    const createNewAnswer = window.opener.document.getElementById('create_new_answer');
    const addNewAnswer = window.opener.document.getElementById('add_new_answer');
    const deleteNewAnswer = window.opener.document.getElementById('delete_new_answer');
    const editNewAnswer = window.opener.document.getElementById('edit_new_answer');
    const relatedAnswers = window.opener.document.getElementById('related_answers');
    const addNewAnswers = window.opener.document.getElementById('add_new_answers');
    const newZnanieId = document.querySelector('script[data-new-znanie-id]').getAttribute('data-new-znanie-id');
    const newZnanieName = document.querySelector('script[data-new-znanie-name]').getAttribute('data-new-znanie-name');
    const typeOfZn = document.querySelector('script[data-type-of-zn]').getAttribute('data-type-of-zn');
    if (typeOfZn === 'test') {
        testSelect.innerHTML = `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        questionSelect.disabled = false;
        addNewQuestion.disabled = false;
        addTest.style.display = 'none';
        editTest.removeAttribute('hidden');
        deleteTest.removeAttribute('hidden');
    }
    else if (typeOfZn === 'question') {
        questionSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        createNewAnswer.removeAttribute('hidden');
        editQuestion.removeAttribute('hidden');
        deleteQuestion.removeAttribute('hidden');
        while (relatedAnswers.firstChild) relatedAnswers.removeChild(relatedAnswers.firstChild);
        while (relatedAnswers.firstChild) relatedAnswers.removeChild(relatedAnswers.firstChild);
    }
    else if (typeOfZn === 'answer') {
        createNewAnswer.style.visibility = 'visible';
        let selectToChange = window.opener.document.querySelector(`[name="new_answer"]`);
        selectToChange.innerHTML = `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        selectToChange.value = newZnanieId
        selectToChange.name = `created_answer_${newZnanieId}`;
        let divToChange = window.opener.document.querySelector(`[id="new_answer_div"]`);
        divToChange.id = `answer_${newZnanieId}`
        addNewAnswer.style.display = "none";
        deleteNewAnswer.id = `delete_answer_${newZnanieId}`
        editNewAnswer.id = `edit_answer_${newZnanieId}`
        window.opener.addEditListener(newZnanieId);
        window.opener.addDeleteListener(newZnanieId);
        deleteNewAnswer.removeAttribute('hidden');
        editNewAnswer.removeAttribute('hidden');
        let isCorrectNewAnswer = window.opener.document.querySelector(`[name="is_correct_answer_new"]`);
        isCorrectNewAnswer.name = `is_correct_created_answer_${newZnanieId}`
    }
    window.close()
}
