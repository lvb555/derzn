
var itemForm = document.getElementById('checkbox_form'); // Берем родительский контейнер всех чекбоксов.
var checkBoxes = itemForm.querySelectorAll('.checkbox_1'); // Берем все чекбоксы
var checkBoxes_checked = itemForm.querySelectorAll('.checkbox_1:checked'); // Берем все чекбоксы
var checkbox_selectAll = document.querySelector(".selectAll"); // Берем чекбокс , который отвечает за "Выделить все"

var tr = itemForm.querySelectorAll('tr')

let serv_data = {}; // В этом словаре храним информацию об АКТИВНЫХ подписках с сервера. {'Грамматика': True, 'Литература': True}
let change_flag = {}; // В этом словаре будут хранится ИЗМЕНЕННЫЕ подписки на теги в процессе работы юзера на странице.
// {'Грамматика': False, 'Литература': False, 'Наука': True}


// При загрузке страницы заполняем словарь ser_data только активными флажками. {'Грамматика': True, 'Литература': True}
for (var i = 0; i < checkBoxes.length; i++) {
    if (checkBoxes[i].checked) {
        serv_data[checkBoxes[i].value] = checkBoxes[i].checked
    }
}

// При загрузке страницы сразу проверяем должен ли стоять флаг на чекбоксе "Выделить все"
check_selectAll()

allTag()

noSub()

function noSub() {
    if (document.getElementById('flexSwitchCheckDefault').checked === false && itemForm.querySelectorAll('.checkbox_1:checked').length === 0) {
        document.getElementById('noSubsText').style.display = '';
    } else {
        document.getElementById('noSubsText').style.display = 'none';
    }
}



function allTag() {
    var radio = document.getElementById('flexSwitchCheckDefault')


    if(radio.checked) {
        checkbox_selectAll.disabled = false;
        tr.forEach(item => {
            item.style.display = 'table-row';

        })
    } else {
        checkbox_selectAll.disabled = true;
        tr.forEach(item => {
            if (!(item.querySelector('.checkbox_1:checked'))) {
                item.style.display = 'none';
            }
        })
    }

    noSub()
}



// Функция для изменения состояния чекбокса "Выделить все". Если все чекбоксы тегов = True, то чекбокс "Выделить все" = True.
function check_selectAll() {
    if(document.querySelectorAll('.checkbox_1:checked').length === checkBoxes.length) {
        checkbox_selectAll.checked = true
    } else if (document.querySelectorAll(".checkbox_1:checked").length < checkBoxes.length) {
        checkbox_selectAll.checked = false
    }
}


// Данная функция вызывается, если нажат чекбокс "Выделить все".
function selectAll() {

    change_flag = {}; // Очищаем словарь change_flag

    // Если все флаги тегов активны, то снимаем их.
    if (document.querySelectorAll('.checkbox_1:checked').length === checkBoxes.length) {
        checkBoxes.forEach(item => {
            item.checked = false;

        })
        // Проходим по всем элементам в serv_data и добавляем их в change_flag со значением False.
        for (var i = 0; i < Object.keys(serv_data).length; i++) {
            change_flag[Object.keys(serv_data)[i]] = false
        }

        // Если хотя бы один флаг тегов неактивен, то меняем их на True и добавляем все чекбоксы в change_flag.
    } else {
        checkBoxes.forEach(item => {
            item.checked = true;
            change_flag[item.value] = item.checked;
        })

        // Чтобы не отправлять избыточные данные на сервер сразу удаляем из change_flag те чекбоксы, которые изначально
        // были активны (пользователь уже подписан на них), то есть все из словаря serv_data
        for (var i = 0; i < Object.keys(serv_data).length; i++) {
            delete change_flag[Object.keys(serv_data)[i]]
        }
    }
}



// Сбрасываем форму и очищаем словарь change_flag при нажатии на кнопку "Отменить"
document.getElementById('reset').onclick = function() {
    document.forms.tags.reset(); // сбрасываем форму
    change_flag = {};
}


// Функция вызывается при нажатии на флаг тега.
function changeFlag(item) {

    check_selectAll()

    // Если измененный флаг уже присутствует в change_flag, значит ранее его уже изменяли, соответствоенно необходимо
    // вернуть изначальное состояние (удалить его из change_flag)
    if (Object.keys(change_flag).includes(item.value)) {
        // удаляем данный item из change_flag
        delete change_flag[item.value]

        // Иначе добавляем в change_flag флаг тега.
    } else {
        change_flag[item.value] = item.checked

    }
}


// Функция для отправки POST запроса с измененными данными на сервер.
async function makeRequest(url, method, body) {
    console.log(url)
    let headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }

    if (method=='POST') {
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
        headers['X-CSRFToken'] = csrf
    }

    await fetch('/drevo/subscription_by_tag/1', {
        method: method,
        headers: headers,
        body: body

    })
}

// Функция выполняется при нажатии кнопки "Сохранить".
async function send_data(int) {
    await makeRequest('/drevo/subscription_by_tag/"+int+"', 'POST', JSON.stringify(change_flag))
}

async function send_data_to_author() {
    await makeRequest('/drevo/subscribe_to_author/', 'POST', JSON.stringify(change_flag))
}


// Функция для поиска тега по названию.
function tableSearch() {
    var phrase = document.getElementById('search-text');
    var table = document.getElementById('info-table');
    var regPhrase = new RegExp(phrase.value, 'i');
    var flag = false;

    document.getElementById('flexSwitchCheckDefault').checked =true;
    allTag()

    for (var i = 0; i < table.rows.length; i++) {
        flag = false;
        for (var j = table.rows[i].cells.length - 1; j >= 0; j--) {
            flag = regPhrase.test(table.rows[i].cells[j].innerHTML);
            if (flag) break;
        }
        if (flag) {
            table.rows[i].style.display = "";
        } else {
            table.rows[i].style.display = "none";
        }

    }
}
