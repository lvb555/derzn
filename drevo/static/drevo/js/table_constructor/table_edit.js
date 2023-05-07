function tableEdit() {
    const tableSelect = window.opener.document.getElementById('id_table');
    const isNew = document.querySelector('script[data-new]').getAttribute('data-new');
    if (isNew === 'true') {
        const changedZnanieName = document.querySelector('script[data-changed-name]').getAttribute('data-changed-name');
        const changedZnanieId = document.querySelector('script[data-changed-id]').getAttribute('data-changed-id');
        tableSelect.innerHTML = `<option value="${changedZnanieId}" selected> ${changedZnanieName}</option>`;
        window.close();
    }
}