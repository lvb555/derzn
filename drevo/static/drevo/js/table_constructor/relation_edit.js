function relationEdit() {
    const rowSelect = window.opener.document.getElementById('id_row');
    const columnSelect = window.opener.document.getElementById('id_column');
    const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
    if (isNew === 'true') {
        const changedZnanieName = document.querySelector('script[data-name]').getAttribute('data-name');
        ;
        const changedZnanieId = document.querySelector('script[data-id]').getAttribute('data-id');
        ;
        const relation = document.querySelector('script[data-relation]').getAttribute('data-relation');
        ;
        if (relation === 'row') {
            const optionToChange = [...rowSelect.options].find(option => option.value === changedZnanieId);
            if (optionToChange) {
                optionToChange.text = changedZnanieName;
            }
        } else {
            const optionToChange = [...columnSelect.options].find(option => option.value === changedZnanieId);
            if (optionToChange) {
                optionToChange.text = changedZnanieName;
            }
        }
        window.close()
    }
}