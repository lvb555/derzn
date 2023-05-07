const rowSelect = window.opener.document.getElementById('id_row');
const columnSelect = window.opener.document.getElementById('id_column');
const deleteRow = window.opener.document.getElementById('delete_row');
const deleteColumn = window.opener.document.getElementById('delete_column');
const editRow = window.opener.document.getElementById('edit_row');
const editColumn = window.opener.document.getElementById('edit_column');
const selectZnanie = document.getElementById("id_table")
function newZnanie() {
    if ($('.new-znanie').is(':hidden')) {
        $('.new-znanie').removeAttr('hidden');
    }
    else {
        $('.new-znanie').prop('hidden', true)
    }
 }
 window.addEventListener('load', function() {
    const chooseButton = document.getElementById('zn_choose');
    const relation = window.opener.document.getElementById('relation_type');
    chooseButton.addEventListener('click', function() {
        const selectedOptionIndex = selectZnanie.selectedIndex;
       const selectedOptionValue = selectZnanie.options[selectedOptionIndex].value;
       const selectedOptionText = selectZnanie.options[selectedOptionIndex].textContent;
       if (selectedOptionValue != ''){
           if (relation.value === 'row') {
               rowSelect.innerHTML += `<option value="${selectedOptionValue}" selected> ${selectedOptionText}</option>`
               deleteRow.removeAttribute('hidden');
               editRow.removeAttribute('hidden');
            }
           else {
               columnSelect.innerHTML += `<option value="${selectedOptionValue}" selected> ${selectedOptionText}</option>`
               deleteColumn.removeAttribute('hidden');
               editColumn.removeAttribute('hidden');
            }
           window.close();
       }
    });
  });