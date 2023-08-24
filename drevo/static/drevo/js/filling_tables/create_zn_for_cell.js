const znSelect = window.opener.document.getElementById('id_znanie');
const znNewAdding = document.getElementById('select_zn')
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
    chooseButton.addEventListener('click', function() {
        const selectedOptionIndex = znNewAdding.selectedIndex;
       const selectedOptionValue = znNewAdding.options[selectedOptionIndex].value;
       const selectedOptionText = znNewAdding.options[selectedOptionIndex].textContent;
       if (selectedOptionValue !== ''){
           znSelect.innerHTML += `<option value="${selectedOptionValue}" selected> ${selectedOptionText}</option>`
           window.opener.saveZnToCell(selectedOptionValue);
           window.close();
       }
    });
});