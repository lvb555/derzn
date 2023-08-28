const isNew = document.querySelector('script[data-new]').getAttribute('data-new');

if (isNew === "true") {
    const tableSelect = window.opener.document.getElementById('id_table');
    const tableAdd = window.opener.document.getElementById('add_table');
    const tableDelete = window.opener.document.getElementById('delete_table');
    const tableEdit = window.opener.document.getElementById('edit_table');
    const rowSelect = window.opener.document.getElementById('id_row');
    const rowAdd = window.opener.document.getElementById('add_row');
    const editRow = window.opener.document.getElementById('edit_row');
    const deleteRow = window.opener.document.getElementById('delete_row');
    const columnSelect = window.opener.document.getElementById('id_column');
    const columnAdd = window.opener.document.getElementById('add_column');
    const editColumn = window.opener.document.getElementById('edit_column');
    const deleteColumn = window.opener.document.getElementById('delete_column');
    const elementRowSelect = window.opener.document.getElementById('id_element_row');
    const elementColumnSelect = window.opener.document.getElementById('id_element_column');
    const editElementRow = window.opener.document.getElementById('edit_element_row');
    const editElementColumn = window.opener.document.getElementById('edit_element_column');
    const deleteElementRow = window.opener.document.getElementById('delete_element_row');
    const deleteElementColumn = window.opener.document.getElementById('delete_element_column');
    const relation = window.opener.document.getElementById('relation_type');
    const rowElements = window.opener.document.getElementById('row_elements');
    const columnElements = window.opener.document.getElementById('column_elements');
    const newZnanieName = document.querySelector('script[data-new-znanie-name]').getAttribute('data-new-znanie-name');
    const newZnanieId = document.querySelector('script[data-new-znanie-id]').getAttribute('data-new-znanie-id');
    const newZnanieKind = document.querySelector('script[data-tz-name]').getAttribute('data-tz-name');

    if (relation.value === 'table') {
        tableSelect.innerHTML = `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        rowSelect.disabled = false;
        columnSelect.disabled = false;
        rowAdd.disabled = false;
        columnAdd.disabled = false;
        tableAdd.style.display = "none";
        tableDelete.removeAttribute('hidden');
        tableEdit.removeAttribute('hidden');
    }
    else if (relation.value === 'row') {
       rowSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`
       deleteRow.removeAttribute('hidden');
       editRow.removeAttribute('hidden');
       if (newZnanieKind === 'Группа') {
           rowElements.removeAttribute('hidden');
           addRow.hidden = true;
           rowSelect.style.backgroundImage = 'none';
           rowSelect.style.appearance = 'none';
           rowSelect.style.pointerEvents = 'none';
           deleteRow.style.paddingLeft = 'auto';
       }
    }
    else if (relation.value === 'column') {
           columnSelect.innerHTML += `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`
           deleteColumn.removeAttribute('hidden');
           editColumn.removeAttribute('hidden');
           if (newZnanieKind === 'Группа') {
               columnElements.removeAttribute('hidden');
               columnSelect.style.display = 'block';
               addColumn.hidden = true;
               columnSelect.style.backgroundImage = 'none';
               columnSelect.style.appearance = 'none';
               columnSelect.style.pointerEvents = 'none';
               deleteColumn.style.paddingLeft = 'auto';
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