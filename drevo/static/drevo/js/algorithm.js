current_condition = document.querySelector('.basic input[value="Условие"]');
blocks_out = new Set();
is_last_node = false;
all_blocks = Array.from(document.querySelectorAll('.basic input[value="Блок"]'));
all_conditions = Array.from(document.querySelectorAll('.basic input[value="Условие"]'));
lists_of_variants = Array.from(document.querySelectorAll('.basic input[value="Выбор"]'));
inside_algorithms = Array.from(document.querySelectorAll('.basic input[value="Алгоритм"]'));
chapter = Array.from(document.querySelectorAll('.basic input[value="Раздел"]'));
blocks_and_lists_of_variants = all_blocks.concat(lists_of_variants);
algorithms_and_chapters = inside_algorithms.concat(chapter);
var popupBg = document.querySelector('.popup__bg');
var popup = document.querySelector('.popup');
var closePopupButton = document.querySelector('.close-popup');
var notificationPopup = document.querySelector('.notification');
var closeNotificationButton = notificationPopup.querySelector('i');
var saveBg = document.querySelector('.save-data-form.popup__bg');
var savePopup = saveBg.querySelector('.popup');
var saveClosePopupButton = saveBg.querySelector('.close-popup');
var iconElement = document.createElement("i");
iconElement.className = "bi bi-play-circle-close";
iconElement.setAttribute("onclick", "toggleHiddenElement(this);");
let selectHeader = document.querySelectorAll('.select__header');
var urlParams = new URLSearchParams(window.location.search);
var addBg = document.querySelector('.add-form.popup__bg');
var addPopup = document.querySelector('.add-form.popup__bg .popup');
var addClosePopupButton = document.querySelector('.add-form.popup__bg .close-popup');
var redactBg = document.querySelector('.redact-form.popup__bg');
var redactPopup = document.querySelector('.redact-form.popup__bg .popup');
var redactClosePopupButton = document.querySelector('.redact-form.popup__bg .close-popup');
var deleteBg = document.querySelector('.delete-form.popup__bg');
var deletePopup = document.querySelector('.delete-form.popup__bg .popup');
var deleteClosePopupButton = document.querySelector('.delete-form.popup__bg .close-popup');
var additionalElement = '';
var elementInProcess = '';
var users_elements = [];
var inputElement = document.createElement('input');
inputElement.setAttribute('type', 'checkbox');
inputElement.setAttribute('class', 'simple-elements');
inputElement.setAttribute("onclick", "nextAction(this);");
var new_work = '';
var redacted_elements = [];
var deleteElementIcon = document.createElement("i");
deleteElementIcon.setAttribute('class', 'bi bi-x-lg text-danger p-2');
deleteElementIcon.setAttribute("onclick", "redactOrDelete(this, 'new', 'delete');");
var redactElementIcon = document.createElement("i");
redactElementIcon.setAttribute('class', 'bi bi-pencil-fill text-warning p-2');
redactElementIcon.setAttribute("onclick", "redactOrDelete(this, 'new', 'redact');");
var addElementIcon = document.createElement("i");
addElementIcon.setAttribute('class', 'bi bi-plus-lg text-success p-2');
addElementIcon.setAttribute("onclick", "addNewElement(this);");


function openNext(type){
    if(type == 'block' && (addBg.querySelector('#transformation').style.display == 'none' || document.getElementById('change-checkbox').checked)){
        document.querySelector('#conditionalChoice').style.display = 'block';
    }else{
        document.querySelector('#conditionalChoice').style.display = 'none';
    }
}


// Открывает форму для создания нового элемента
function addNewElement(elem){
    if(elem.previousSibling.previousSibling.getAttribute('value') == 'Блок'){
        addBg.querySelector('#transformation').style.display = 'none';
        if(/Можно сделать|Нужно сделать/.test(elem.parentNode.getAttribute('value'))){
            addBg.querySelector('#block-questions div').style.display = 'none';
            addBg.querySelector('#conditionalChoice').style.display = 'block';
            document.getElementById('blockRadio').checked = true;
        }else{
            addBg.querySelector('#block-questions div').style.display = 'flex';
        }
    }else{
        addBg.querySelector('#block-questions div').style.display = 'none';
        if(elem.parentNode.querySelector('input').value == 'Действие' && !(elem.nextSibling)){
            addBg.querySelector('#transformation').style.display = 'block';
            addBg.querySelector('#transformation label').textContent = 'Преобразовать элемент "'+elem.parentNode.querySelector('a').textContent+'" в "Блок"?';
        }else{
            addBg.querySelector('#transformation').style.display = 'none';
        }
    }
    if(new_work && document.querySelector('#new_work_name')){
        document.querySelector('#new_work_name').parentNode.style.display = 'none';
    }
    addBg.classList.add('active');
    addPopup.classList.add('active');
    document.body.classList.add("stop-scrolling");
    additionalElement = elem.parentNode;
}


function redactOrDelete(elem, status, action){
    document.body.classList.add("stop-scrolling");
    elementInProcess = elem.parentNode;
    if(action == 'delete'){
        deleteBg.classList.add('active');
        deletePopup.classList.add('active');
        deleteBg.querySelector('h5.title').textContent = 'Вы уверены, что хотите удалить элемент "'+elementInProcess.querySelector('a').textContent+'" ?';
    }else{
        redactBg.classList.add('active');
        redactPopup.classList.add('active');
        redactBg.querySelector('#rename').value = elementInProcess.querySelector('a').textContent;
    }
}


// Удаляет элемент из базы и со страницы
function deleteElement(){
    users_elements.forEach((elem) => {
        if(elementInProcess.querySelector('a').textContent == elem.querySelector('a').textContent && elem != elementInProcess){
            elem.parentNode.removeChild(elem);
        }
    });
    if(redacted_elements.includes(elementInProcess.querySelector('a').textContent)){
        changed_element = redacted_elements.indexOf(elementInProcess.querySelector('a').textContent);
            if(changed_element > -1){
                redacted_elements.splice(changed_element, 2);
            }
    }
    if(/Можно сделать|Нужно сделать/.test(elementInProcess.getAttribute('value')) && elementInProcess.parentNode.childNodes.length == 1){
        elementInProcess.parentNode.parentNode.firstChild.nextSibling.value = 'Действие';
        previousAElement = elementInProcess.parentNode.parentNode.firstChild.nextSibling.nextSibling.firstChild;
        elementInProcess.parentNode.parentNode.firstChild.nextSibling.nextSibling.innerHTML = previousAElement.outerHTML + ' (Действие)';
        elementInProcess.parentNode.parentNode.removeChild(elementInProcess.parentNode);
    }else{
        elementInProcess.parentNode.removeChild(elementInProcess);
    }
    deleteBg.classList.remove('active');
    deletePopup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
    if(!new_work){
        new_work = 'Данные по алгоритму';
    }
    $.ajax({
        data: { 'work' : new_work, 'deleted': elementInProcess.querySelector('a').textContent },
        url: document.location.pathname + '/edit_algorithm/',
        success: function (response) {
            showNotification('Элемент удален','success_comment');
        }
    });
}


// Меняет название элемента в базе и на странице
function saveNewName(){
    var elementName = document.getElementById('rename').value;
    if(elementName == '' || users_elements.filter(item => item.querySelector('a').textContent.trim() == elementName).length > 0){
        document.querySelector('.redact-form .warning').textContent = 'Недопустимое название';
    }else{
        if(!(redacted_elements.includes(elementInProcess.querySelector('a').textContent))){
            redacted_elements.push(elementName);
            redacted_elements.push([elementInProcess.querySelector('a').textContent, elementName]);
        }else{
            changed_element = redacted_elements.indexOf(elementInProcess.querySelector('a').textContent);
            if(changed_element > -1){
                redacted_elements[changed_element] = elementName;
                redacted_elements[changed_element+1][1] = elementName;
            }
        }
        users_elements.forEach((elem) => {
            if(elementInProcess.querySelector('a').textContent == elem.querySelector('a').textContent && elem != elementInProcess){
                elem.querySelector('a').textContent = elementName;
            }
        });
        elementInProcess.querySelector('a').textContent = elementName;
        redactBg.classList.remove('active');
        redactPopup.classList.remove('active');
        document.body.classList.remove("stop-scrolling");
        document.getElementById('rename').value = '';
        document.querySelector('.redact-form .warning').textContent = '';
        if(!new_work){
            new_work = 'Данные по алгоритму';
        }
        $.ajax({
            data: { 'work' : new_work, 'redacted': JSON.stringify(redacted_elements[redacted_elements.length - 1]) },
            url: document.location.pathname + '/edit_algorithm/',
            success: function (response) {
                showNotification('Элемент изменен','success_comment');
            }
        });
    }
}


function saveNewElement(){
    var elementName = document.getElementById('elem').value;
    var insertionType = document.querySelector('input[name="insertion_type"]:checked');
    var connectionType = document.querySelector('input[name="connection"]:checked');
    // Проверяем заполнены ли поля и повторяется ли название пользовательских элементов
    if(elementName == '' || users_elements.filter(item => item.querySelector('a').textContent.trim() == elementName).length > 0){
        document.querySelector('.add-form .warning').textContent = 'Недопустимое название элемента';
    }else if(addBg.querySelector('#block-questions').style.display == 'block' && !connectionType){
        if(!insertionType){
            document.querySelector('.add-form .warning').textContent = 'Выберите вид вставки';
        }else{
            document.querySelector('.add-form .warning').textContent = 'Выберите вид связи';
        }
    }else if(document.querySelector('#new_work_name') && (Array.from(document.querySelectorAll('.select__item')).filter(item => item.textContent.trim() ==
    document.querySelector('#new_work_name').value).length > 0 || document.querySelector('#new_work_name').value == '')){
            document.querySelector('.add-form .warning').textContent = 'Недопустимое название работы';
    }else{
        // Создаем новый элемент
        var newLi = document.createElement('li');
        var spanText = document.createElement('span');
        spanText.setAttribute('class', 'text-secondary d-flex');
        var checkbox = inputElement.cloneNode(true);
        checkbox.setAttribute("disabled", "true");
        var aElement = document.createElement('a');
        var spanAlgorithm = document.createElement('span');
        var relation = 'necessary';
        var insertion = true;
        if((insertionType && insertionType.value === "Block") || document.getElementById('change-checkbox').checked){
            document.getElementById('blockRadio').checked = false;
            document.getElementById('actionRadio').checked = false;
            insertion = false;
            if(!connectionType){
                document.querySelector('.add-form .warning').textContent = 'Выберите тип состава';
            }else{
                newLi.setAttribute('value', connectionType.value);
                spanText.appendChild(document.createTextNode(connectionType.value));
                if(connectionType.value === "Можно сделать"){
                    relation = 'unnecessary';
                }
            }
        }else{
            newLi.setAttribute('value', 'Далее');
            spanText.appendChild(document.createTextNode('Далее'));
        }
        inputElement.setAttribute('value', 'Действие');
        var textNode = document.createTextNode(' (Действие)');
        aElement.appendChild(document.createTextNode(elementName));
        spanAlgorithm.setAttribute('class', 'algorithm-element ms-2');
        spanAlgorithm.appendChild(aElement);
        spanAlgorithm.appendChild(textNode);
        newLi.appendChild(spanText);
        newLi.appendChild(checkbox);
        newLi.appendChild(spanAlgorithm);
        newLi.appendChild(redactElementIcon.cloneNode(true));
        newLi.appendChild(deleteElementIcon.cloneNode(true));
        if(document.getElementById('change-checkbox').checked){
            var newUl = document.createElement('ul');
            newUl.appendChild(newLi);
            additionalElement.lastChild.after(newUl);
            additionalElement.firstChild.nextSibling.value = 'Блок';
            previousAElement = additionalElement.firstChild.nextSibling.nextSibling.firstChild
            additionalElement.firstChild.nextSibling.nextSibling.innerHTML = previousAElement.outerHTML + ' (Блок)';
        }
        if((insertionType && insertionType.value === "Block") || document.getElementById('change-checkbox').checked){
            if(!document.getElementById('change-checkbox').checked){
                if(relation == 'necessary'){
                    additionalElement.lastChild.firstChild.before(newLi);
                }else{
                    additionalElement.lastChild.lastChild.after(newLi);
                }
            }
        }else{
            newLi.lastChild.previousSibling.before(addElementIcon.cloneNode(true));
            additionalElement.after(newLi);
        }
        addBg.classList.remove('active');
        addPopup.classList.remove('active');
        document.body.classList.remove("stop-scrolling");
        document.querySelector('#conditionalChoice').style.display = 'none';
        document.getElementById('elem').value = '';
        document.getElementById('change-checkbox').checked = false;
        document.querySelector('.add-form .warning').textContent = '';
        parent_element = additionalElement
        while(parent_element.lastChild.previousSibling.classList.contains('text-warning') ||
        parent_element.lastChild.previousSibling.classList.contains('text-danger')){
            parent_element = parent_element.previousSibling;
        }
        if(!new_work){
            if(document.querySelector('#new_work_name')){
                new_work = document.querySelector('#new_work_name').value
            }else{
                new_work = 'Данные по алгоритму';
            }
        }
        users_elements.push(newLi);
        $.ajax({
            data: { 'work' : new_work, 'new_element': JSON.stringify({ 'element_name': elementName, 'parent_element':
            parent_element.firstChild.nextSibling.nextSibling.firstChild.textContent, 'relation_type': relation,
            'insertion_type': insertion})},
            url: document.location.pathname + '/edit_algorithm/',
            success: function (response) {
                showNotification('Элемент добавлен','success_comment');
            }
        });
    }
}


function ShowFirst(){
    dict_to_send = {};
    let list_to_change_status = [];
    document.querySelector('.basic input[type="checkbox"]').nextSibling.style.color = 'red';
    if(!(document.querySelector('.basic div#algorithm_tree span').classList.contains('text-secondary'))){
        showNotification(document.querySelector('.basic div#algorithm_tree span'), 'comment');
    }
    if(document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
        list_to_change_status = list_to_change_status.concat(recurseOpening(document.querySelector('.basic input[type="checkbox"]')));
    }else{
        document.querySelector('.basic input[type="checkbox"]').disabled = false;
        list_to_change_status.push([document.querySelector('.basic span.algorithm-element.ms-2 a').textContent, 'available']);
    }
    document.querySelectorAll('#algorithm_tree li[value="Далее"]').forEach((elem) => {
        elem.style.display = 'none';
    });
    if(list_to_change_status){
        for(prop = 0, len = list_to_change_status.length; prop < len; ++prop){
            dict_to_send[list_to_change_status[prop][0]] = list_to_change_status[prop][1]
        }
    }
    if(isAuthenticated){
        setTimeout(()=>{
            $.ajax({
                data: { 'values' : JSON.stringify(dict_to_send), 'for_deletion': JSON.stringify(''), 'work' : new_work},
                url: document.location.pathname + '/algorithm_result/',
                success: function (response) {}
            });
        }, 1500);
    }
}


if((!urlParams.has('mode') || urlParams.get('mode') == '') && document.querySelector('#algorithm_tree')){
    if(!isManyWorks && (typeof getPreviousProgress() === 'undefined' || getPreviousProgress().length === 0)){
        setTimeout(()=>{new_work = 'Данные по алгоритму';}, 1000);
        ShowFirst();
    }else if(document.getElementById('choose_other') && document.querySelectorAll('.select__item a').length > 2){
        if(typeof getPreviousProgress() === 'object' && getPreviousProgress().length > 0){
            rebuildResult(getPreviousProgress());
        }else{
            ShowFirst();
        }
    }else{
        saveBg.classList.add('active');
        savePopup.classList.add('active');
        document.body.classList.add("stop-scrolling");
        if(document.querySelector('#work_name')){
            defolt_name = 1;
            while(Array.from(document.querySelectorAll('.select__item')).filter(item => item.textContent.trim() == 'Работа по алгоритму '+String(defolt_name)).length
            > 0){
                defolt_name += 1;
            }
            document.querySelector('#work_name').value = 'Работа по алгоритму '+String(defolt_name);
        }
    }
    if(urlParams.has('previous_works') || urlParams.get('previous_works') != ''){
        new_work = urlParams.get('previous_works');
    }
}else if(document.querySelector('#algorithm_tree')){
    document.querySelectorAll('i[onclick="redactOrDelete(this, \'same\', \'redact\');"').forEach((elem) => {
        users_elements.push(elem.parentNode);
        if(elem.parentNode.getAttribute('value') == 'Нужно сделать'){
            elem.parentNode.parentNode.firstChild.before(elem.parentNode);
        }
    });
    if(urlParams.has('previous_works') || urlParams.get('previous_works') != ''){
        new_work = urlParams.get('previous_works');
    }
}


function closePopup(condition){
        flag = true;
        if(document.querySelector('#work_name')){
            current_name = document.querySelector('#work_name').value
            if(Array.from(document.querySelectorAll('.select__item')).filter(item => item.textContent.trim() == current_name).length
            > 0 && !(previous_result == current_name)){
                document.querySelector('.warning').style.display = 'block';
                document.querySelector('.warning').textContent = 'Недопустимое название';
                flag = false;
            }else{
                document.querySelector('.warning').style.display = 'none';
                flag = true;
            }
            new_work = current_name;
        }
        if(!isManyWorks){
            setTimeout(()=>{new_work = 'Данные по алгоритму';}, 1000);
        }
        if(condition == 'continue' && (typeof getPreviousProgress() === 'object' && getPreviousProgress().length > 0)){
            rebuildResult(getPreviousProgress());
            if(document.getElementById('continue')){
                new_work = document.querySelectorAll('.select__item a')[1].textContent
            }
        }else if(condition == 'choose_other'){
            flag = false;
            document.getElementById('continue').style.display = 'none';
            document.getElementById('choose_other').style.display = 'block';
        }else if( condition == 'confirm'){
            flag = false;
            document.getElementById('continue_work').style.display = 'none';
            document.getElementById('confirm').style.display = 'block';
        }else{
            if(isAuthenticated && (typeof getPreviousProgress() === 'object' && getPreviousProgress().length > 0)){
                $.ajax({
                    data: { 'values' : JSON.stringify(''), 'for_deletion': JSON.stringify('delete old results'), 'work' : new_work},
                    url: document.location.pathname + '/algorithm_result/',
                    success: function (response) {}
                });
            }
            ShowFirst();
        }
        if(flag == true){
            saveBg.classList.remove('active');
            savePopup.classList.remove('active');
            document.body.classList.remove("stop-scrolling");
        }
}


if(addClosePopupButton){
    function closePopup(elem) {
        elem.parentNode.parentNode.classList.remove('active');
        elem.parentNode.parentNode.classList.remove('active');
        document.body.classList.remove("stop-scrolling");
    }
    addClosePopupButton.addEventListener('click', () => closePopup(addClosePopupButton));
    deleteClosePopupButton.addEventListener('click', () => closePopup(deleteClosePopupButton));
    redactClosePopupButton.addEventListener('click', () => closePopup(redactClosePopupButton));
    document.getElementsByName("rejection")[0].addEventListener('click', () => closePopup(deleteClosePopupButton));
}


selectHeader.forEach(item => {
    item.addEventListener('click', selectToggle);
});


function selectToggle() {
    this.parentElement.classList.toggle('is-active');
}


// Перебор всех сохраненных элементов
function rebuildResult(list_of_elements){
    end_elem = '';
    changeCondition(document.querySelector('.basic input[type="checkbox"]'),list_of_elements[0]['element_type'])
    delete list_of_elements[0];
    if(document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
        level = document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.childNodes
    }else{
        level = document.querySelector('.basic ul').childNodes
    }
    previous_element = document.querySelector('.basic input[type="checkbox"]');
    for(let pair in list_of_elements){
        let [new_level, founded_checkbox] = findCheckbox(level,list_of_elements[pair]['element'], previous_element)
        level = new_level;
        changeCondition(founded_checkbox,list_of_elements[pair]['element_type'])
        findIsExceptionType(previous_element, founded_checkbox);
        previous_element = founded_checkbox;
    }
    document.querySelectorAll('#algorithm_tree li[value="Далее"]').forEach((elem) => {
        if(elem.firstChild.nextSibling && !(elem.firstChild.nextSibling.nextSibling.style.color)){
            elem.style.display = 'none';
        }
    });
}


// Ищет чекбокс, соответствующий названию
function findCheckbox(lay, name, previous_element){
    founded_checkbox = '';
    if(previous_element.parentNode.lastChild.tagName == 'UL'){
        previous_element.parentNode.lastChild.childNodes.forEach((child) => {
            if(!(child.firstChild && child.firstChild.style.display == 'none') && child.querySelector('.algorithm-element a').innerText == name){
                if(child.lastChild.tagName == 'UL' && child.lastChild.getElementsByTagName('li').length > 0){
                    lay = child.lastChild.childNodes;
                }
                founded_checkbox = child.querySelector('.algorithm-element').previousSibling
            }
        });
    }
    if(founded_checkbox == ''){
        while(founded_checkbox == ''){
            lay[0].parentNode.childNodes.forEach((child) => {
            if(((!(child.style.display == 'none') && !(child.firstChild && child.firstChild.style.display == 'none')) || child.getAttribute('value') == 'Вариант') && child.querySelector('.algorithm-element a').innerText == name){
                    if(child.lastChild.tagName == 'UL' && child.lastChild.getElementsByTagName('li').length > 0){
                        lay = child.lastChild.childNodes;
                    }
                    founded_checkbox = child.querySelector('.algorithm-element').previousSibling
                }
            });
            if(!(lay[0].parentNode.parentNode.parentNode.tagName == 'UL')) break;
            if(!(founded_checkbox == '')) break;
            lay = lay[0].parentNode.parentNode.parentNode.childNodes
        }
    }
    return[lay, founded_checkbox]
}


// Проверяет, является ли чекбокс дочерним "Условия" или "Выбора"
function findIsExceptionType(previous_item, current_item){
    if(previous_item.getAttribute('value') == 'Условие'){
        if(previous_item.nextSibling.style.color == 'blue' || current_item.parentNode.parentNode == previous_item.parentNode.lastChild){
            if(!(previous_item.nextSibling.style.color == 'blue')){
                previous_item.parentNode.lastChild.style.display = 'block';
            }
            extra_text = document.createElement("i");
            condition_element = current_item.parentNode;
            if(current_item.parentNode.getAttribute('value') == 'Тогда' || current_item.parentNode.getAttribute('value') == 'Иначе'){
                if(current_item.parentNode.getAttribute('value') == 'Тогда'){
                    extra_text.innerText = 'Выбран ответ "Да"';
                    if(Array.from(current_item.parentNode.parentNode.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Иначе").length > 0){
                        Array.from(current_item.parentNode.parentNode.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Иначе")[0].style.display = 'none';
                    }
                }else{
                    extra_text.innerText = 'Выбран ответ "Нет"'
                    if(Array.from(current_item.parentNode.parentNode.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Тогда").length > 0){
                        Array.from(current_item.parentNode.parentNode.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Тогда")[0].style.display = 'none';
                    }
                }
            }else{
                if(previous_item.parentNode.lastChild.firstChild.getAttribute('value') == 'Тогда'){
                    extra_text.innerText = 'Выбран ответ "Нет"';
                    if(Array.from(previous_item.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Тогда").length > 0){
                        Array.from(previous_item.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Тогда")[0].style.display = 'none';
                    }
                }else{
                    extra_text.innerText = 'Выбран ответ "Да"';
                    if(Array.from(previous_item.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Иначе").length > 0){
                        Array.from(previous_item.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Иначе")[0].style.display = 'none';
                    }
                }
                if(previous_item.parentNode.lastChild.previousSibling.tagName == 'I'){
                    previous_item.parentNode.lastChild.previousSibling.remove();
                }
            }
            previous_item.nextSibling.after(extra_text);
        }else{
            document.querySelector('#condition').textContent = previous_item.nextSibling.firstChild.innerText;
            current_condition = previous_item;
            setTimeout(()=>{
                popupBg.classList.add('active');
                popup.classList.add('active');
                document.body.classList.add("stop-scrolling");
            }, 1500);
        }
    }else if(previous_item.getAttribute('value') == 'Выбор' || previous_item.parentNode.getAttribute('value') == 'Вариант'){
        if(current_item.parentNode.getAttribute('value') == 'Вариант' && ((current_item.parentNode.parentNode == previous_item.parentNode.lastChild
        && previous_item.checked == true) || (current_item.parentNode.parentNode == previous_item.parentNode.parentNode && previous_item.checked == false)) && current_item.checked == true ){
            makeDisableOrAvailableAllSiblings(current_item.parentNode, true);
        }
    }
    if(current_item.getAttribute('value') == 'Конец алгоритма'){
        endTheAlgorithm(current_item.parentNode);
    }
}


// Раскрывает подэлемент и окрашивает знание в зависимости от его состояния
function changeCondition(element, condition){
    if(condition == 'active'){
        element.nextSibling.style.color = 'green';
        if(element.getAttribute('value') == 'Действие'){
            element.disabled = false;
        }
        if(/Можно сделать|Нужно сделать|Вариант/.test(element.parentNode.getAttribute('value'))){
            element.checked = true;
            element.disabled = false;
        }
        if(element.parentNode.lastChild.tagName == 'UL' && (!(element.getAttribute('value') == 'Условие'))){
            element.parentNode.lastChild.style.display = 'block';
        }
        element.nextSibling.style.fontWeight  = 'normal';
    }else if(condition == 'available'){
        element.nextSibling.style.color = 'red';
        element.disabled = false;
        element.nextSibling.style.fontWeight  = 'bold';
    }else{
        if(element.parentNode.lastChild.tagName == 'UL'){
            element.parentNode.lastChild.previousSibling.after(iconElement.cloneNode(true));
        }
        element.nextSibling.style.color = 'blue';
        element.nextSibling.style.fontWeight  = 'normal';
        element.checked = true;
        element.disabled = false;
    }
}


// Рекурсивно открывает вложенные элементы до тех пор, пока не будет элемента, который пользователь сможет отметить
function recurseOpening(element){
    let list_to_change_status = [];
    element.parentNode.style.display = 'block';
    element.nextSibling.style.color = 'green';
    list_to_change_status.push([element.parentNode.querySelector('a').textContent, 'active']);
    if(blocks_and_lists_of_variants.includes(element)){
        element.parentNode.lastChild.style.display = 'block';
        element.parentNode.lastChild.childNodes.forEach((elem) => {
            elem.querySelector('input[type="checkbox"]').disabled = false;
            list_to_change_status.push([elem.querySelector('a').textContent, 'available']);
            elem.firstChild.nextSibling.nextSibling.style.color = 'red';
            elem.firstChild.nextSibling.nextSibling.style.fontWeight  = 'bold';
        });
        if(!(element.parentNode.getAttribute('value').includes('Можно сделать') &&
            element.parentNode.parentNode.parentNode.firstChild.nextSibling.checked == true)){
            list_to_change_status = list_to_change_status.concat(findAncestors(element));
        }
    }else if(algorithms_and_chapters.includes(element)){
        first_sub_elem = element.parentNode.lastChild.querySelector('input[type="checkbox"]');
        element.parentNode.lastChild.style.display = 'block';
        if(!(element.parentNode.lastChild.querySelector('span').classList.contains('text-secondary'))){
            list_to_change_status = list_to_change_status.concat(findNextAction(element.parentNode.lastChild.firstChild));
        }else{
            first_sub_elem.nextSibling.style.color = 'green';
            if(first_sub_elem.parentNode.lastChild.tagName == 'UL' && first_sub_elem.parentNode.lastChild.getElementsByTagName('li').length > 0){
                if(!(all_conditions.includes(first_sub_elem))){
                    first_sub_elem.parentNode.lastChild.style.display = 'block';
                }
                list_to_change_status = list_to_change_status.concat(recurseOpening(first_sub_elem));
                list_to_change_status.push([first_sub_elem.parentNode.querySelector('a').textContent, 'active']);
            }else{
                first_sub_elem.disabled = false;
                first_sub_elem.nextSibling.style.color = 'red';
                first_sub_elem.nextSibling.style.fontWeight  = 'bold';
                if(first_sub_elem.value == 'Конец алгоритма'){
                    first_sub_elem.checked = true;
                    first_sub_elem.disabled = true;
                    first_sub_elem.nextSibling.style.color = 'blue';
                    list_to_change_status.push([first_sub_elem.parentNode.querySelector('a').textContent, 'completed']);
                    first_sub_elem.nextSibling.style.fontWeight = 'normal';
                    showNotification(first_sub_elem, 'ending');
                }else{
                    list_to_change_status.push([first_sub_elem.parentNode.querySelector('a').textContent, 'available']);
                }
            }
        }
        if(!(element.parentNode.getAttribute('value').includes('Можно сделать') &&
            element.parentNode.parentNode.parentNode.firstChild.nextSibling.checked == true)){
            list_to_change_status = list_to_change_status.concat(findAncestors(element));
        }
    }else if(all_conditions.includes(element)){
        document.querySelector('#condition').textContent = element.nextSibling.firstChild.innerText;
        current_condition = element;
        setTimeout(()=>{
            popupBg.classList.add('active');
            popup.classList.add('active');
            document.body.classList.add("stop-scrolling");
        }, 1500);
    }
    return list_to_change_status
}


function startAction(action){
    let list_to_change_status = [];
    let list_to_remove_elements = [];
    if(action.checked == true){
        action.nextSibling.style.color = 'green';
        action.nextSibling.style.fontWeight = 'normal';
        if(action.parentNode.getAttribute('value').includes('Вариант')){
            list_to_change_status = list_to_change_status.concat(makeDisableOrAvailableAllSiblings(action.parentNode, true));
        }else if(/Можно сделать|Нужно сделать/.test(action.parentNode.getAttribute('value'))){
            if(!(action.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements') in blocks_out )){
                if(!(action.parentNode.getAttribute('value').includes('Можно сделать') &&
                action.parentNode.parentNode.parentNode.firstChild.nextSibling.checked == true)){
                    blocks_out.add(action.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements'))
                }
            }
        }
        if(action.parentNode.lastChild.tagName == 'UL' && action.parentNode.lastChild.getElementsByTagName('li').length > 0){
            if(!all_conditions.includes(action.parentNode.querySelector('input[type="checkbox"].simple-elements'))){
                action.parentNode.lastChild.style.display = 'block';
            }
            list_to_change_status = list_to_change_status.concat(recurseOpening(action.parentNode.querySelector('input[type="checkbox"].simple-elements')));
        }else{
            action.nextSibling.style.color = 'blue';
            list_to_change_status.push([action.parentNode.querySelector('a').textContent, 'completed']);
            if(!(action.parentNode.getAttribute('value').includes('Можно сделать') &&
            action.parentNode.parentNode.parentNode.firstChild.nextSibling.checked == true)){
                list_to_change_status = list_to_change_status.concat(findAncestors(action));
            }
            if(action.nextSibling.value == 'Конец алгоритма'){
                action.nextSibling.checked = true;
                action.nextSibling.disabled = true;
                action.nextSibling.style.color = 'blue';
                action.nextSibling.style.fontWeight = 'normal';
                showNotification(action, 'ending');
            }
        }
    }else{
        if(action.parentNode.getAttribute('value').includes('Вариант')){
            list_to_change_status = list_to_change_status.concat(makeDisableOrAvailableAllSiblings(action.parentNode, false));
        }
        if(action.parentNode.lastChild.tagName == 'UL' && action.parentNode.lastChild.getElementsByTagName('li').length > 0){
            action.parentNode.lastChild.style.display = 'none';
            action.parentNode.lastChild.childNodes.forEach((elem) => {
                if(elem.getAttribute('value') == 'Далее'){
                    elem.style.display = 'none';
                }
            });
        }
        action.parentNode.querySelector('input[type="checkbox"].simple-elements').checked = false;
        let [list_to_change, list_to_remove] = uncheckAncestors(action);
        list_to_change_status = list_to_change_status.concat(list_to_change);
        list_to_remove_elements = list_to_remove_elements.concat(list_to_remove);
        action.nextSibling.style.color = 'red';
        list_to_change_status.push([action.parentNode.querySelector('a').textContent, 'available']);
        action.nextSibling.style.fontWeight  = 'bold';
        action.disabled = false;
    }
    return [list_to_change_status, list_to_remove_elements]
}


// Обработка закрытия модального окна
closePopupButton.addEventListener('click', (e) => {
    popupBg.classList.remove('active');
    popup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
})


// Делаем неактивными или активными ветки рядом
function makeDisableOrAvailableAllSiblings(elem, ability){
    list_to_change_status = [];
    if(elem.nextSibling){
        next_one = elem.nextSibling
        while(next_one){
            if(ability == true){
                next_one.style.display = 'none';
            }else{
                next_one.style.display = 'block';
                if(next_one.firstChild.nextSibling.checked == false){
                    next_one.firstChild.nextSibling.nextSibling.style.color = 'red';
                    list_to_change_status.push([next_one.querySelector('a').textContent, 'available']);
                    next_one.firstChild.nextSibling.nextSibling.style.fontWeight  = 'bold';
                }
                next_one.firstChild.nextSibling.disabled = false;
            }
            if(!next_one.nextSibling) break;
            next_one = next_one.nextSibling
        }
    }
    if(elem.previousSibling){
        next_one = elem.previousSibling
        while(next_one) {
            if(ability == true){
                next_one.style.display = 'none';
            }else{
                next_one.style.display = 'block';
                if(next_one.firstChild.nextSibling.checked == false){
                    next_one.firstChild.nextSibling.nextSibling.style.color = 'red';
                    list_to_change_status.push([next_one.querySelector('a').textContent, 'available']);
                    next_one.firstChild.nextSibling.nextSibling.style.fontWeight  = 'bold';
                }
                next_one.firstChild.nextSibling.disabled = false;
            }
            if(!next_one.previousSibling) break;
            next_one = next_one.previousSibling
        }
    }
    return list_to_change_status
}


// Меняет элемент в соответствии с видом связи, измененные данные отправляет в бд
function nextAction(action){
    let list_to_change_status = [];
    let list_to_remove_elements = [];
    if(/Можно сделать|Нужно сделать|Вариант/.test(action.parentNode.getAttribute('value'))){
        let [list_to_change, list_to_remove] = startAction(action);
        list_to_change_status = list_to_change_status.concat(list_to_change);
        list_to_remove_elements = list_to_remove_elements.concat(list_to_remove);
    }else{
        if(action.checked == true){
            action.nextSibling.style.color = 'blue';
            list_to_change_status.push([action.parentNode.querySelector('a').textContent, 'completed']);
            action.nextSibling.style.fontWeight  = 'normal';
            if(action.parentNode.nextSibling && action.parentNode.nextSibling.getAttribute('value') == 'Далее' && !(action.parentNode.getAttribute('value').includes('Вариант'))){
                if(action.parentNode.nextSibling.lastChild.tagName == 'UL' && action.parentNode.nextSibling.lastChild.getElementsByTagName('li').length > 0){
                    list_to_change_status = list_to_change_status.concat(recurseOpening(action.parentNode.nextSibling.firstChild.nextSibling));
                }else{
                    if(action.parentNode.parentNode.parentNode.tagName == 'LI'){
                        action.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"]').nextSibling.style.color = 'green';
                    }
                    if(!(/Можно сделать|Нужно сделать/.test(action.parentNode.getAttribute('value')))){
                        list_to_change_status = list_to_change_status.concat(findNextAction(action.parentNode.nextSibling));
                    }
                }
            }else if(action.parentNode.nextSibling && !(action.parentNode.nextSibling.querySelector('span').classList.contains('text-secondary'))
            && !(action.parentNode.nextSibling.getAttribute('value') == 'Иначе')){
                showNotification(action.parentNode.nextSibling.querySelector('span'), 'comment');
            }else{
                list_to_change_status = list_to_change_status.concat(findAncestors(action));
            }
        }else{
            removeNotification(notificationPopup.querySelector('i'));
            action.nextSibling.style.fontWeight = 'normal';
            let [list_to_change, list_to_remove] = uncheckAncestors(action);
            list_to_change_status = list_to_change_status.concat(list_to_change);
            list_to_remove_elements = list_to_remove_elements.concat(list_to_remove);
            if(!(action.value == 'Действие')){
                action.disabled = true;
                list_to_change_status = list_to_change_status.concat(recurseOpening(action));
            }else{
                action.nextSibling.style.color = 'red';
                list_to_change_status.push([action.parentNode.querySelector('a').textContent, 'available']);
                action.nextSibling.style.fontWeight  = 'bold';
                action.disabled = false;
            }
        }
    }
    dict_to_send = {};
    if(list_to_change_status){
        for(prop = 0, len = list_to_change_status.length; prop < len; ++prop){
            dict_to_send[list_to_change_status[prop][0]] = list_to_change_status[prop][1]
        }
    }
    if(list_to_remove_elements){
        list_to_remove_elements = list_to_remove_elements.filter(function(item, position) {
            return list_to_remove_elements.indexOf(item) == position && !dict_to_send.hasOwnProperty(item)
        })
    }
    $.ajax({
        data: { 'values' : JSON.stringify(dict_to_send), 'for_deletion': JSON.stringify(list_to_remove_elements), 'work' : new_work},
        url: document.location.pathname + '/algorithm_result/',
        success: function (response) {}
    });
}


// Скрывает альтернативный ответ на условие и делает активным первый чекбокс, соответствующий ответу
function answerCondition(answer){
    let list_to_change_status = [];
    popupBg.classList.remove('active');
    popup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
    extra_text = document.createElement("i");
    if(answer == 'Тогда'){
        extra_text.innerText = 'Выбран ответ "Да"'
    }else{
        extra_text.innerText = 'Выбран ответ "Нет"'
    }
    current_condition.nextSibling.after(extra_text);
    if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == ''+answer+'').length > 0){
        condition_element = current_condition.parentNode.lastChild.firstChild;
        if(answer == 'Тогда'){
            if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
             == "Иначе").length > 0){
                 Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                 == "Иначе")[0].style.display = 'none';
             }
             list_to_change_status = list_to_change_status.concat(findNextAction(condition_element));
             if(condition_element.firstChild.nextSibling){
                list_to_change_status = list_to_change_status.concat(findAncestors(condition_element.firstChild.nextSibling));
             }else{
                list_to_change_status = list_to_change_status.concat(findAncestors(condition_element.firstChild));
             }
        }else{
            if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
            == "Тогда").length > 0){
                Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Тогда")[0].style.display = 'none';
            }
            list_to_change_status = list_to_change_status.concat(findNextAction(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
            == "Иначе")[0]));
            if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Иначе")[0].firstChild.nextSibling){
                list_to_change_status = list_to_change_status.concat(findAncestors(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Иначе")[0].firstChild.nextSibling));
            }else{
                list_to_change_status = list_to_change_status.concat(findAncestors(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Иначе")[0].firstChild));
            }
        }
        condition_element.parentNode.style.display = 'block';
    }else{
        current_condition.checked = true;
        current_condition.disabled = false;
        current_condition.nextSibling.style.color = 'blue';
        list_to_change_status.push([current_condition.parentNode.querySelector('a').textContent, 'completed'])
        list_to_change_status = list_to_change_status.concat(findAncestors(current_condition));
    }
    dict_to_send = {};
    if(list_to_change_status){
        for(prop = 0, len = list_to_change_status.length; prop < len; ++prop){
            dict_to_send[list_to_change_status[prop][0]] = list_to_change_status[prop][1]
        }
    }
    $.ajax({
        data: { 'values' : JSON.stringify(dict_to_send), 'for_deletion': JSON.stringify(''), 'work' : new_work},
        url: document.location.pathname + '/algorithm_result/',
        success: function (response) {}
    });
}


// Проверяет все ли элементы в блоке отмечены
function actionInBlock(examined_block, type){
    let list_to_change_status = [];
    examined_block.nextSibling.style.color = 'green';
    list_to_change_status.push([examined_block.parentNode.querySelector('a').textContent, 'active']);
    is_all = 0;
    add_comment = 0;
    if(type == 'block'){
        examined_block.parentNode.lastChild.childNodes.forEach((elem) => {
            if(elem.firstChild.nextSibling.nextSibling.style.color !== 'blue' && elem.style.display !== 'none'){
                if(elem.getAttribute('value').includes('Можно сделать')){
                    add_comment += 1;
                }else if(elem.getAttribute('value').includes('Нужно сделать')){
                    is_all = 1;
                }
            }
        });
    }else{
        examined_block.parentNode.lastChild.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
            if(elem.nextSibling.style.color != 'blue' && elem.parentNode.style.display != 'none' && elem.parentNode.parentNode.style.display != 'none'){
                is_all = 1;
            }
        });
    }
    if(is_all == 0){
        examined_block.nextSibling.style.color = 'blue';
        list_to_change_status.push([examined_block.parentNode.querySelector('a').textContent, 'completed']);
        examined_block.checked = true;
        examined_block.disabled = false;
        if(add_comment > 0){
            if(add_comment > 1){
                showNotification(String('В блоке '+examined_block.nextSibling.firstChild.textContent+' остались невыполненные необязательные элементы'), 'block_notification');
            }else{
                showNotification(String('В блоке '+examined_block.nextSibling.firstChild.textContent+' остался невыполненный необязательный элемент'), 'block_notification');
            }
        }
        if(!(examined_block.parentNode.getAttribute('value').includes('Можно сделать'))){
            list_to_change_status = list_to_change_status.concat(findAncestors(examined_block));
        }
        if(!(examined_block.parentNode.lastChild.previousSibling.classList.contains('bi'))){
            examined_block.parentNode.lastChild.previousSibling.after(iconElement.cloneNode(true));
            examined_block.parentNode.lastChild.style.display = 'none';
        }else{
            toggleHiddenElement(examined_block.parentNode.lastChild.previousSibling);
        }
        if(type == 'block'){
            blocks_out.delete(examined_block);
        }
    }
    return list_to_change_status
}


function toggleHiddenElement(element) {
    if(element.classList.contains("bi-play-circle-open")){
        element.classList.remove("bi-play-circle-open")
        element.classList.add("bi-play-circle-close");
        element.parentNode.lastElementChild.style.display = 'none';
    }else{
        element.classList.remove("bi-play-circle-close")
        element.classList.add("bi-play-circle-open");
        element.parentNode.lastElementChild.style.display = 'block';
    }
}


function tree_showAll() {
    document.querySelectorAll('.bi-play-circle-close, .bi-play-circle-open').forEach((elem) => {
        elem.classList.remove("bi-play-circle-close")
        elem.classList.add("bi-play-circle-open");
        elem.parentNode.lastElementChild.style.display = 'block';
    })
}


function tree_hiddenAll() {
    document.querySelectorAll('.bi-play-circle-close, .bi-play-circle-open').forEach((elem) => {
        elem.classList.remove("bi-play-circle-open")
        elem.classList.add("bi-play-circle-close");
        elem.parentNode.lastElementChild.style.display = 'none';
    })
}


// Смотрит внутри чего был элемент
function findAncestors(child){
    let list_to_change_status = [];
    ancestor = child.parentNode
    if(ancestor.parentNode.parentNode.tagName == 'LI'){
        ancestor = ancestor.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements')
        if(ancestor.value == 'Блок'){
        list_to_change_status = list_to_change_status.concat(actionInBlock(ancestor, 'block'));
        }else if(ancestor.value == 'Алгоритм' || ancestor.value == 'Раздел' || ancestor.value == 'Условие'){
            if(child.checked == true || child.tagName == 'SPAN'){
                if(child.parentNode.nextSibling && child.parentNode.nextSibling.getAttribute('value') == 'Далее'){
                    list_to_change_status = list_to_change_status.concat(findNextAction(child.parentNode.nextSibling));
                }else if(child.parentNode.nextSibling && !(child.parentNode.nextSibling.querySelector('span').classList.contains('text-secondary'))
                && !(child.parentNode.nextSibling.getAttribute('value') == 'Иначе')){
                    showNotification(child.parentNode.nextSibling.querySelector('span'), 'comment');
                }else{
                    ancestor.checked = true;
                    ancestor.disabled = false;
                    ancestor.nextSibling.style.color = 'blue';
                    list_to_change_status.push([ancestor.parentNode.querySelector('a').textContent, 'completed']);
                    list_to_change_status = list_to_change_status.concat(actionInBlock(ancestor, 'notblock'));
                    if(!(ancestor.parentNode.getAttribute('value') == 'Можно сделать')){
                        list_to_change_status = list_to_change_status.concat(findAncestors(ancestor));
                    }
                }
            }
        }else if(ancestor.value == 'Выбор'){
            list_to_change_status = list_to_change_status.concat(actionInBlock(ancestor, 'notblock'));
        }else if(!ancestor.value){
            if(child.parentNode.nextSibling){
                list_to_change_status = list_to_change_status.concat(findNextAction(child.parentNode.nextSibling));
            }
        }
    }else{
    // Если в главном блоке
        if(child.checked == true){
            if(child.parentNode.nextSibling && child.parentNode.nextSibling.getAttribute('value') == 'Далее'){
                list_to_change_status = list_to_change_status.concat(findNextAction(child.parentNode.nextSibling));
            }
        }
    }
    return list_to_change_status
}


// Находит следующий элемент с чекбоксом
function findNextAction(next_action){
    let list_to_change_status = [];
    if(next_action.querySelector('input[type="checkbox"]')){
        next_action.style.display = 'block';
        if(next_action.querySelector('input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && next_action.querySelector('input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
            list_to_change_status = list_to_change_status.concat(recurseOpening(next_action.querySelector('input[type="checkbox"].simple-elements')));
        }else{
            next_action.querySelector('input[type="checkbox"]').disabled = false;
            next_action.querySelector('input[type="checkbox"]').nextSibling.style.color = 'red';
            next_action.querySelector('input[type="checkbox"]').nextSibling.style.fontWeight  = 'bold';
            if(next_action.querySelector('input[type="checkbox"]').value == 'Конец алгоритма'){
                next_action.querySelector('input[type="checkbox"]').checked = true;
                next_action.querySelector('input[type="checkbox"]').disabled = true;
                next_action.querySelector('input[type="checkbox"]').nextSibling.style.color = 'blue';
                list_to_change_status.push([next_action.querySelector('a').textContent, 'completed']);
                next_action.querySelector('input[type="checkbox"]').nextSibling.style.fontWeight = 'normal';
                showNotification(next_action.querySelector('input[type="checkbox"]'), 'ending');
            }else{
                list_to_change_status.push([next_action.querySelector('a').textContent, 'available']);
            }
        }
    }else{
        if(!(next_action.querySelector('span').classList.contains('text-secondary'))){
            showNotification(next_action.querySelector('span'), 'comment');
            next_action.parentNode.parentNode.querySelector('.algorithm-element').style.color= 'blue';
            list_to_change_status.push([next_action.parentNode.parentNode.querySelector('a').textContent, 'completed']);
        }
        if(next_action.nextSibling && next_action.nextSibling.getAttribute('value') == 'Далее'){
            list_to_change_status = list_to_change_status.concat(findNextAction(next_action.nextSibling));
        }
    }
    return list_to_change_status
}


// Возвращает алгоритм в состояние, как будто пользователь не отмечал чекбокс
function uncheckAncestors(action){
    ancestor = action.parentNode;
    list_to_remove = [];
    list_to_change_status = [];
    if(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.getAttribute('value'))){
        list_to_change_status = list_to_change_status.concat(makeDisableOrAvailableAllSiblings(ancestor,false));
    }
    ancestor.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
        elem.checked = false;
        elem.disabled = true;
        if(/green|red|blue/.test(elem.nextSibling.style.color)){
            list_to_remove.push(elem.parentNode.querySelector('a').textContent);
            elem.nextSibling.style.color = 'black';
        }
        elem.nextSibling.style.fontWeight = 'normal';
        if(elem.parentNode.getAttribute('value') == 'Далее' && !(elem == action)){
            elem.parentNode.style.display = 'none';
        }else{
            elem.parentNode.style.display = 'block';
        }
    })
    ancestor.querySelectorAll('li > i').forEach((elem) => {
        elem.remove();
    })
    action.disabled = false;
    if(ancestor.parentNode.parentNode.tagName == 'LI'){
        ancestor = ancestor.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements');
        observed_checkbox = action;
        if(ancestor.checked == true){
            while(ancestor.checked == true && !(observed_checkbox.parentNode.getAttribute('value').includes('Можно сделать'))){
                ancestor.checked = false;
                ancestor.disabled = true;
                if(ancestor.parentNode.lastChild.tagName == 'UL' && !(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value')))
                && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                    ancestor.nextSibling.style.color = 'green';
                    list_to_change_status.push([ancestor.parentNode.querySelector('a').textContent, 'active']);
                }else if(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value'))){
                    ancestor.nextSibling.style.color = 'green';
                    list_to_change_status.push([ancestor.parentNode.querySelector('a').textContent, 'active']);
                    ancestor.nextSibling.style.fontWeight = 'normal';
                    ancestor.checked = true;
                    ancestor.disabled = false;
                    if(ancestor.parentNode.getAttribute('value') ==! 'Вариант'){
                        list_to_change_status = list_to_change_status.concat(makeDisableOrAvailableAllSiblings(ancestor.parentNode,false));
                    }
                }else{
                    ancestor.nextSibling.style.color = 'red';
                    list_to_change_status.push([ancestor.querySelector('a').textContent, 'available']);
                    ancestor.nextSibling.style.fontWeight = 'bold';
                }
                if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок') &&
                !(observed_checkbox.parentNode.getAttribute('value').includes('Можно сделать'))){
                    list_to_remove = list_to_remove.concat(uncheckSiblings(observed_checkbox.parentNode.nextSibling));
                }
                if(!(ancestor.parentNode.parentNode.parentNode.tagName == 'LI')){
                    list_to_remove = list_to_remove.concat(uncheckSiblings(ancestor.parentNode.nextSibling));
                    break;
                }
                observed_checkbox = ancestor;
                ancestor = ancestor.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements');
                if(ancestor.checked == false){
                    if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                        list_to_remove = list_to_remove.concat(uncheckSiblings(observed_checkbox.parentNode.nextSibling));
                    }
                    if(ancestor.parentNode.lastChild.tagName == 'UL' && !(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value')))
                    && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                        ancestor.nextSibling.style.color = 'green';
                        list_to_change_status.push([ancestor.querySelector('a').textContent, 'active']);
                        ancestor.nextSibling.style.fontWeight = 'normal';
                    }else{
                        ancestor.nextSibling.style.color = 'red';
                        list_to_change_status.push([ancestor.querySelector('a').textContent, 'available']);
                        ancestor.nextSibling.style.fontWeight = 'bold';
                    }
                }
            }
        }else{
            if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок') &&
            !(observed_checkbox.parentNode.getAttribute('value') == 'Можно сделать')){
                list_to_remove = list_to_remove.concat(uncheckSiblings(action.parentNode.nextSibling));
            }
            if(ancestor.parentNode.lastChild.tagName == 'UL' && !(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value')))
            && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                ancestor.nextSibling.style.color = 'green';
                list_to_change_status.push([ancestor.parentNode.querySelector('a').textContent, 'active']);
                ancestor.nextSibling.style.fontWeight = 'normal';
            }else{
                ancestor.nextSibling.style.color = 'red';
                list_to_change_status.push([ancestor.parentNode.querySelector('a').textContent, 'available']);
                ancestor.nextSibling.style.fontWeight = 'bold';
            }
        }
    }else{
        list_to_remove = list_to_remove.concat(uncheckSiblings(action.parentNode.nextSibling));
    }
    return [list_to_change_status, list_to_remove]
}


function uncheckSiblings(closest_sibling){
    list_to_remove = [];
    while(closest_sibling){
        if(!(closest_sibling.querySelector('input[type="checkbox"].simple-elements'))){
            closest_sibling = closest_sibling.nextSibling
        }else{
            if(closest_sibling.querySelector('input[type="checkbox"].simple-elements').nextSibling.style.color == 'black') break
            closest_sibling.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
                elem.checked = false;
                elem.disabled = true;
                elem.nextSibling.style.color = 'black';
                if(!(/Тогда|Иначе/.test(elem.parentNode.getAttribute('value')))){
                    list_to_remove.push(elem.parentNode.querySelector('a').textContent);
                }
                elem.nextSibling.style.fontWeight = 'normal';
                if(elem.parentNode.getAttribute('value') == 'Далее' || elem.parentNode.getAttribute('value') == 'Тогда'
                || elem.parentNode.getAttribute('value') == 'Иначе'){
                    elem.parentNode.style.display = 'none';
                }else{
                    elem.parentNode.style.display = 'block';
                }
            })
            closest_sibling.querySelectorAll('li > i').forEach((elem) => {
                elem.parentNode.lastChild.style.display = 'none';
                elem.remove()
            })
            if(closest_sibling.lastChild.tagName == 'UL'){
                closest_sibling.lastChild.style.display = 'none';
            }
            closest_sibling = closest_sibling.nextSibling
        }
    }
    return list_to_remove
}


// Показывает уведомление о завершении алгоритма или комментарий
function showNotification(elem, type){
    if(type == 'ending'){
        let name_of_completed_algorithm = 'Вы прошли алгоритм "';
        const algorithm_to_end = document.querySelector('.container.header_info h1');
        const current_elem = elem
        while(name_of_completed_algorithm == 'Вы прошли алгоритм "'){
            if(!(elem.parentNode.parentNode.parentNode.tagName == 'LI')){
                name_of_completed_algorithm += document.querySelector('.container.header_info h1').textContent + '"';
                break;
            }
            if(elem.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements').getAttribute('value') == 'Алгоритм'){
                full_name = elem.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements').nextSibling.firstChild.innerText
                name_of_completed_algorithm += full_name + '"';
            }else{
                elem = elem.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements')
            }
        }
        document.querySelector('#end_of_algorithm').innerHTML = name_of_completed_algorithm;
        notificationPopup.style.display = 'block';
        setTimeout(()=>{removeNotification(closeNotificationButton)}, 10000);
        endTheAlgorithm(current_elem.parentNode);
    }else{
        const comment = document.createElement("div");
        comment.classList.add('notification');
        const inner_title = document.createElement("h3");
        const closeIcon = document.createElement("i");
        closeIcon.className = "bi bi-x-lg";
        closeIcon.style.cssFloat = 'right';
        closeIcon.setAttribute("onclick", "removeNotification(this);");
        if(type == 'comment'){
            inner_title.innerText = elem.textContent.slice(0, elem.textContent.length-13);
        }else{
            inner_title.innerText = elem;
        }
        comment.append(closeIcon);
        comment.append(inner_title);
        document.querySelector('#end_of_algorithm').parentNode.before(comment);
        setTimeout(()=>{comment.remove()}, 20000);
    }
}


function removeNotification(notification){
    if(notification.parentNode.classList.contains('end_of_algorithm')){
        notification.parentNode.style.display = 'none';
    }else{
        notification.parentNode.remove();
    }
}


// При элементе "Конец алгоритма" оставляем только путь элементов до него
function endTheAlgorithm(action){
    let list_to_change_status = [];
    action = action.parentNode.parentNode;
    while(!action.classList.contains('root')){
        action.firstChild.nextSibling.checked = true;
        action.firstChild.nextSibling.disabled = false;
        action.firstChild.nextSibling.nextSibling.style.color = 'blue';
        list_to_change_status.push([action.querySelector('a').textContent, 'completed']);
        if(action.firstChild.nextSibling.getAttribute('value') == 'Алгоритм') break;
        if(action.parentNode.parentNode.firstChild.nextSibling.getAttribute('value') != 'Блок'){
            while(action.nextSibling && action.nextSibling.tagName == 'LI'){
                action.nextSibling.style.display = 'none';
                action = action.nextSibling;
            }
        }else{
            list_to_change_status = list_to_change_status.concat(makeDisableOrAvailableAllSiblings(action, true));
        }
        if(action.parentNode.parentNode.tagName == 'LI'){
            if(!(action.parentNode.parentNode.lastChild.previousSibling.classList.contains('bi'))){
                action.parentNode.parentNode.lastChild.previousSibling.after(iconElement.cloneNode(true));
                action.parentNode.parentNode.lastChild.style.display = 'none';
            }else{
                toggleHiddenElement(action.parentNode.parentNode.lastChild.previousSibling);
            }
        }
        action = action.parentNode.parentNode
    }
    if(!action.classList.contains('root') && action.nextSibling){
        list_to_change_status = list_to_change_status.concat(findNextAction(action.nextSibling));
    }
    dict_to_send = {};
    if(list_to_change_status){
        for(prop = 0, len = list_to_change_status.length; prop < len; ++prop){
            dict_to_send[list_to_change_status[prop][0]] = list_to_change_status[prop][1]
        }
    }
    $.ajax({
        data: { 'values' : JSON.stringify(dict_to_send), 'for_deletion': JSON.stringify(''), 'work' : new_work},
        url: document.location.pathname + '/algorithm_result/',
        success: function (response) {}
    });
}