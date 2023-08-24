const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
if (isNew === 'true') {
    const tableSelect = window.opener.document.getElementById('id_table');
    const rowSelect = window.opener.document.getElementById('id_row');
    const columnSelect = window.opener.document.getElementById('id_column');
    const rowElementSelect = window.opener.document.getElementById('id_element_row');
    const columnElementSelect = window.opener.document.getElementById('id_element_column');
    const changedZnanieName = document.querySelector('script[data-changed-name]').getAttribute('data-changed-name');
    const changedZnanieId = document.querySelector('script[data-changed-id]').getAttribute('data-changed-id');
    const relation = document.querySelector('script[data-relation]').getAttribute('data-relation');
    if (relation === 'table') {
        tableSelect.innerHTML = `<option value="${changedZnanieId}" selected> ${changedZnanieName}</option>`;
        window.close();
    }
    else if (relation === 'row') {
        const optionToChange = [...rowSelect.options].find(option => option.value === changedZnanieId);
        if (optionToChange)
            optionToChange.text = changedZnanieName;
    }
    else if (relation === 'column') {
        const optionToChange = [...columnSelect.options].find(option => option.value === changedZnanieId);
        if (optionToChange)
            optionToChange.text = changedZnanieName;
    }
    else if (relation === 'element_row') {
        const optionToChange = [...rowElementSelect].find(option => option.value === changedZnanieId);
        if (optionToChange)
            optionToChange.text = changedZnanieName;
    }
    else if (relation === 'element_column') {
        const optionToChange = [...columnElementSelect].find(option => option.value === changedZnanieId);
        if (optionToChange)
            optionToChange.text = changedZnanieName;
    }
    window.close()

}