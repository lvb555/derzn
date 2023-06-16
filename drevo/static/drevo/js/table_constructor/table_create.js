function tableCreate() {
    const tableSelect = window.opener.document.getElementById('id_table');
    const tableAdd = window.opener.document.getElementById('add_table');
    const tableDelete = window.opener.document.getElementById('delete_table');
    const tableEdit = window.opener.document.getElementById('edit_table');
    const rowSelect = window.opener.document.getElementById('id_row');
    const columnSelect = window.opener.document.getElementById('id_column');
    const rowAdd = window.opener.document.getElementById('add_row');
    const columnAdd = window.opener.document.getElementById('add_column');
    const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
    
    if (isNew === "true") {
        const newZnanieName = document.querySelector('script[data-new-znanie-name]').getAttribute('data-new-znanie-name');
        const newZnanieId = document.querySelector('script[data-new-znanie-id]').getAttribute('data-new-znanie-id');
        tableSelect.innerHTML = `<option value="${newZnanieId}" selected> ${newZnanieName}</option>`;
        rowSelect.disabled = false;
        columnSelect.disabled = false;
        rowAdd.disabled = false;
        columnAdd.disabled = false;
        tableAdd.style.display = "none";
        tableDelete.removeAttribute('hidden');
        tableEdit.removeAttribute('hidden');
        window.close()
    }

}
