const authors = "user";

function fakeSelect() {
    let selectHeader = document.querySelectorAll('.select__header');
    let selectItem = document.querySelectorAll('.select__item');

    selectHeader.forEach(item => {
        item.addEventListener('click', selectToggle);
    });

    selectItem.forEach(item => {
        item.addEventListener('click', selectChoose)
    });

    function selectToggle() {
        this.parentElement.classList.toggle('is-active');
    }

    function selectChoose() {
        selectedValue = this.getAttribute('value')
        let text = this.innerText,
            select = this.closest('.select'),
            currentText = select.querySelector('.select__current');
        currentText.innerText = text;
        spanElement = document.getElementById('select');
        spanElement.setAttribute('value',selectedValue);
        elements = document.querySelectorAll(`[name="${authors}"]`);
        elements.forEach((element) => {
            if (selectedValue === 'all' || element.id === selectedValue) {
            element.style.display = 'block';
            } else {
            element.style.display = 'none';
            }
        });
        select.classList.remove('is-active');
    }
};

fakeSelect();

var textareas = document.querySelectorAll('textarea[name="message"]');
var sendButtons = document.querySelectorAll('#sendAnswer');

textareas.forEach(function(textarea, index) {
    textarea.addEventListener('input', function() {
      if (textarea.value.trim() !== '') {
        sendButtons[index].disabled = false;
      } else {
        sendButtons[index].disabled = true;
      }
    });
});

function TSendClick(ticketId){
    var message = document.getElementById(''+ticketId+'').querySelector('textarea[name="message"]').value;

    $.ajax({
        data: {'message':message, 'ticket_id': ticketId},
        url: '/drevo/appeal/',
        success: function (response) {
        location.reload();
        }
     });
}