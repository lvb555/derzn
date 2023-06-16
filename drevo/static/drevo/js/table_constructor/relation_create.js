function relationCreate() {
    const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
    if (isNew === 'true') {
        const rowSelect = window.opener.document.getElementById('id_row');
        const columnSelect = window.opener.document.getElementById('id_column');
        const elementRowSelect = window.opener.document.getElementById('id_element_row');
        const elementColumnSelect = window.opener.document.getElementById('id_element_column');
        const addRow = window.opener.document.getElementById('add_row');
        const addColumn = window.opener.document.getElementById('add_column');
        const editRow = window.opener.document.getElementById('edit_row');
        const editColumn = window.opener.document.getElementById('edit_column');
        const editElementRow = window.opener.document.getElementById('edit_element_row');
        const editElementColumn = window.opener.document.getElementById('edit_element_column');
        const deleteRow = window.opener.document.getElementById('delete_row');
        const deleteColumn = window.opener.document.getElementById('delete_column');
        const deleteElementRow = window.opener.document.getElementById('delete_element_row');
        const deleteElementColumn = window.opener.document.getElementById('delete_element_column');
        const newZnanieName = document.querySelector('script[data-name]').getAttribute('data-name');
        const newZnanieId = document.querySelector('script[data-id]').getAttribute('data-id');
        const newZnanieKind = document.querySelector('script[data-tz-name]').getAttribute('data-tz-name');
        const relation = window.opener.document.getElementById('relation_type');
        const rowElements = window.opener.document.getElementById('row_elements');
        const columnElements = window.opener.document.getElementById('column_elements');

        if (relation.value === 'row') {
           rowSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`
           deleteRow.removeAttribute('hidden');
           editRow.removeAttribute('hidden');
           if (newZnanieKind === 'Группа') {
               rowElements.removeAttribute('hidden');
               addRow.hidden = true;
               rowSelect.css('background-image', 'none');
               rowSelect.css('appearance', 'none');
               rowSelect.css('pointer-events', 'none');
               deleteRow.css('padding-left', 'auto');
           }
        }
        else if (relation.value === 'column') {
               columnSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`
               deleteColumn.removeAttribute('hidden');
               editColumn.removeAttribute('hidden');
               if (newZnanieKind === 'Группа') {
                   columnElements.removeAttribute('hidden');
                   addColumn.hidden = true;
                   columnSelect.css('background-image', 'none');
                   columnSelect.css('appearance', 'none');
                   columnSelect.css('pointer-events', 'none');
                   deleteColumn.css('padding-left', 'auto');
               }
        }
        else if (relation.value === 'element_row') {
                elementRowSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`
                deleteElementRow.removeAttribute('hidden');
                editElementRow.removeAttribute('hidden')
        }
        else {
                elementColumnSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`
                deleteElementColumn.removeAttribute('hidden');
                editElementColumn.removeAttribute('hidden');
        }
         window.close();
        }

}
