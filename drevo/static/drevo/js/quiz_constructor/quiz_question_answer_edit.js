const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
if (isNew === 'true') {
    const testSelect = window.opener.document.getElementById('id_test');
    const questionSelect = window.opener.document.getElementById('id_question');
    const changedZnanieName = document.querySelector('script[data-changed-name]').getAttribute('data-changed-name');
    const changedZnanieId = document.querySelector('script[data-changed-id]').getAttribute('data-changed-id');
    const typeOfZnanie = document.querySelector('script[data-type-of-zn]').getAttribute('data-type-of-zn');
    let optionToChange = null;
    if (typeOfZnanie === 'test')
        optionToChange = [...testSelect.options].find(option => option.value === changedZnanieId);
    else if (typeOfZnanie === 'question')
        optionToChange = [...questionSelect.options].find(option => option.value === changedZnanieId);
    else if (typeOfZnanie === 'answer')
        optionToChange = window.opener.document.querySelector(`[value="${changedZnanieId}"]`);
    if (optionToChange)
        optionToChange.text = changedZnanieName;
    window.close()
}
