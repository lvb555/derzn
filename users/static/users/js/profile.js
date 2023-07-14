function ShowFirst(){
    let section_title = document.querySelectorAll('.section_title')
    let all_checkboxes = document.querySelectorAll('.section:checked');
    let previous_checkboxes = document.querySelector('#previous');
    for(let i = 0; i < all_checkboxes.length; i++){
        if(!(previous_checkboxes.textContent.includes(all_checkboxes[i].name))){
            all_checkboxes[i].checked = false;
        }
    }
    for(let c = 0; c < section_title.length; c++){
        let block = document.querySelector('.'+section_title[c].id);
        let block_checkboxes_checked = block.querySelectorAll('.section:checked');
        let block_checkboxes = block.querySelectorAll('.section');
        if(block_checkboxes.length == block_checkboxes_checked.length){
            document.querySelector('#'+section_title[c].id).checked = true;
        }
    }
}

ShowFirst()

function appendingNewClass(){
    redio_bottoms = document.querySelectorAll('input[type="radio"]');
    for(i=0;i < redio_bottoms.length; i++){
        redio_bottoms[i].classList.add("form-check-input");
    }
}

appendingNewClass()

function ShowPassword(elem){
    const input = elem.parentNode.querySelector('input');
    const icon = elem.parentNode.querySelector('i');

    if (input.getAttribute('type') === 'text') {
      input.setAttribute('type', 'password');
      icon.classList.add('bi-eye-slash');
      icon.classList.remove('bi-eye');
    } else if (input.getAttribute('type') === 'password') {
      input.setAttribute('type', 'text');
      icon.classList.add('bi-eye');
      icon.classList.remove('bi-eye-slash');
    }
}

const agreementCheckbox = document.getElementById('agreement-checkbox');
const agreementButton = document.getElementById('agreement-button');
const deleteCheckbox = document.getElementById('delete-checkbox');
const deleteButton = document.getElementById('delete-button');

agreementCheckbox.addEventListener('change', function() {
    if (agreementCheckbox.checked) {
      agreementButton.removeAttribute('disabled');
    } else {
      agreementButton.setAttribute('disabled', 'disabled');
    }
});

deleteCheckbox.addEventListener('change', function() {
    if (deleteCheckbox.checked) {
      deleteButton.removeAttribute('disabled');
    } else {
      deleteButton.setAttribute('disabled', 'disabled');
    }
});

function IsAllChecked(name){
    element = document.querySelector("input[name='"+name+"']")
    parent = element.parentElement.parentElement
    if(parent.querySelectorAll('.section').length == parent.querySelectorAll('.section:checked').length){
        parent.parentElement.querySelector('.section_title').checked = true;
    }else if(parent.querySelectorAll('.section:checked').length == 0){
        parent.parentElement.querySelector('.section_title').checked = false;
    }
}

function CleanAll(){
    var checkboxes = document.querySelectorAll('#sections input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = false;
    });
    document.querySelector('input[name="is_public"]').checked = false;
}

function SelectAll(id){
    a = document.querySelector('.'+id);
    b = a.querySelectorAll('input[type="checkbox"]');
    if(document.querySelector('#'+id).checked == true){
        for(let i = 0; i < b.length; i++){
            b[i].checked = true;
        }
    }else{
        for(let i = 0; i < b.length; i++){
            b[i].checked = false;
        }
    }
}

//Функция для генерации аватара по инициалам фамилии и имени, если они не указаны - по первой букве логина
function createImage(text) {
    var background = '#083E2F';
    var text = text[0]

    if(document.querySelector('#id_first_name').value && document.querySelector('#id_last_name').value){
    text = document.querySelector('#id_first_name').value[0] + document.querySelector('#id_last_name').value[0];
    }

    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');

    canvas.width = 200;
    canvas.height = 200;

    context.fillStyle = background;
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#FFFFFF';
    context.font = 'bold 96px Rubik';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, canvas.width / 2, canvas.height / 2);

    var dataURL = canvas.toDataURL('image/png');
    var avatarImage = document.getElementById('avatar');
    avatarImage.src = dataURL;
    document.getElementById('id_generated_image').value = dataURL;
    document.getElementById('id_image').value = '';
}

function deleteAvatar(){
    var avatarImage = document.getElementById('avatar');
    avatarImage.src = '/static/src/default_avatar.jpg';
    document.getElementById('id_generated_image').value = '/static/src/default_avatar.jpg';
    document.getElementById('id_image').value = '';
}

//Функция для предпросмотра фото, которое загрузил пользователь
document.querySelector('#id_image').addEventListener('change', function(event) {
    var input = event.target;
    var preview = document.getElementById('avatar');

    if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      preview.src = e.target.result;
    };

    reader.readAsDataURL(input.files[0]);
    }
});

function showForm(element){
    block_with_form = element.parentNode;
    block_with_form.querySelector('div').style.display = 'none';
    block_with_form.querySelector('input').style.display = 'none';
    block_with_form.querySelector('form').style.display = 'grid';
}

function cleanForm(element){
    if(element == 'new_password'){
        document.querySelector('input#id_'+element+'1').value = '';
        document.querySelector('input#id_'+element+'2').value = '';
        document.querySelector('input#id_old_password').value = '';
    }else{
        document.querySelector('input#'+element+'').value = '';
    }
}


// обработка открытия и закрытия модального окна
var popupBg = document.querySelector('.popup__bg');
var popup = document.querySelector('.popup');
var openPopupButton = document.querySelector('.open-popup');
var closePopupButton = document.querySelector('.close-popup');


openPopupButton.addEventListener('click', (e) => {
    e.preventDefault();
    popupBg.classList.add('active');
    popup.classList.add('active');
    document.body.classList.add("stop-scrolling");
})

closePopupButton.addEventListener('click', (e) => {
    popupBg.classList.remove('active');
    popup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
})

function SendUserMenu(){
    let added_sections = [];
    let all_checkboxes = document.querySelectorAll('.section:checked');
    let publicity = document.querySelector('input[name="is_public"]').checked;

    for(let i = 0; i < all_checkboxes.length; i++){
        added_sections.push(all_checkboxes[i].name);
    }
    $.ajax({
        data: { 'sections' : JSON.stringify(added_sections), 'publicity': publicity },
        url: '/users/user_menu/',
        success: function (response) {
        }
    });
}