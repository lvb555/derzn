function relationEdit() {
    const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
    if (isNew === 'true') {
        const rowSelect = window.opener.document.getElementById('id_row');
        const columnSelect = window.opener.document.getElementById('id_column');
        const rowElementSelect = window.opener.document.getElementById('id_element_row');
        const columnElementSelect = window.opener.document.getElementById('id_element_column');
        const changedZnanieName = document.querySelector('script[data-name]').getAttribute('data-name');
        const changedZnanieId = document.querySelector('script[data-id]').getAttribute('data-id');
        const relation = document.querySelector('script[data-relation]').getAttribute('data-relation');
        if (relation === 'row') {
            const optionToChange = [...rowSelect.options].find(option => option.value === changedZnanieId);
            if (optionToChange)
                optionToChange.text = changedZnanieName;
        } else if (relation === 'column') {
            const optionToChange = [...columnSelect.options].find(option => option.value === changedZnanieId);
            if (optionToChange)
                optionToChange.text = changedZnanieName;
        } else if (relation === 'element_row') {
            const optionToChange = [...rowElementSelect].find(option => option.value === changedZnanieId);
            if (optionToChange)
                optionToChange.text = changedZnanieName;
        } else if (relation === 'element_column') {
            const optionToChange = [...columnElementSelect].find(option => option.value === changedZnanieId);
            if (optionToChange)
                optionToChange.text = changedZnanieName;
        }
        window.close()
    }
}