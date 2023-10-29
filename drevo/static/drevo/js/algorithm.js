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
var saveBg = document.querySelector('.save-form.popup__bg');
var savePopup = saveBg.querySelector('.popup');
var saveClosePopupButton = saveBg.querySelector('.close-popup');
var iconElement = document.createElement("i");
iconElement.className = "bi bi-play-circle-close";
iconElement.setAttribute("onclick", "toggleHiddenElement(this);");
var openPopupButton = document.querySelector('#save-button');
let selectHeader = document.querySelectorAll('.select__header');
var urlParams = new URLSearchParams(window.location.search);


function ShowFirst(){
    if (typeof getPreviousProgress() === 'undefined') {
        document.querySelector('.basic input[type="checkbox"]').nextSibling.style.color = 'red';
        if(!(document.querySelector('.basic div#algorithm_tree span').classList.contains('text-secondary'))){
            showNotification(document.querySelector('.basic div#algorithm_tree span'), 'comment');
        }
        if(document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
            recurseOpening(document.querySelector('.basic input[type="checkbox"]'));
        }else{
            document.querySelector('.basic input[type="checkbox"]').disabled = false;
        }
        document.querySelectorAll('#algorithm_tree li[value="Далее"]').forEach((elem) => {
            elem.style.display = 'none';
        });
    }else{
        rebuildResult(getPreviousProgress())
    }
}

ShowFirst();


openPopupButton.addEventListener('click', (e) => {
    if (!isAuthenticated) {
    // Если пользователь не авторизован, перенаправляем его на страницу авторизации
        window.location.href = window.location.origin + '/users/login/?next=/drevo/algorithm/'
        + window.location.href.split('/').pop();
    }
    saveBg.classList.add('active');
    savePopup.classList.add('active');
    document.body.classList.add("stop-scrolling");
});


saveClosePopupButton.addEventListener('click', (e) => {
    saveBg.classList.remove('active');
    savePopup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
});


selectHeader.forEach(item => {
    item.addEventListener('click', selectToggle);
});


function selectToggle() {
    this.parentElement.classList.toggle('is-active');
}


// Перебор всех сохраненных элементов
function rebuildResult(list_of_elements){
    changeCondition(document.querySelector('.basic input[type="checkbox"]'),list_of_elements[0]['element_type'])
    delete list_of_elements[0];
    if(document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
        level = document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.childNodes
    }else{
        level = document.querySelector('.basic ul').childNodes
    }
    previous_element = document.querySelector('.basic input[type="checkbox"]')
    for(let pair in list_of_elements){
        let [new_level, founded_checkbox] = findCheckbox(level,list_of_elements[pair]['element__name'], previous_element)
        level = new_level;
        previous_element = founded_checkbox;
        changeCondition(founded_checkbox,list_of_elements[pair]['element_type'])
    }
    document.querySelectorAll('#algorithm_tree li[value="Далее"]').forEach((elem) => {
        if(elem.firstChild.nextSibling && !(elem.firstChild.nextSibling.nextSibling.style.color)){
            elem.style.display = 'none';
        }
    });
}


// Ищем чекбокс, соответствующий названию
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
            if(!(child.style.display == 'none') && !(child.firstChild && child.firstChild.style.display == 'none') && child.querySelector('.algorithm-element a').innerText == name){
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
    findIsExceptionType(previous_element, founded_checkbox);
    return[lay, founded_checkbox]
}


// Смотрим, является ли чекбокс дочерним "Условия" или "Выбора"
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
                    extra_text.innerText = 'Выбран ответ "Да"'
                    flag = 0;
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
    }else if(previous_item.getAttribute('value') == 'Выбор'){
        if(current_item.parentNode.getAttribute('value') == 'Вариант' && current_item.parentNode.parentNode == previous_item.parentNode.lastChild
        && previous_item.checked == true){
            makeDisableOrAvailableAllSiblings(current_item.parentNode, true);
        }
    }
}


// Раскрывает подэлемент и окрашивает знание в зависимости от его состояния
function changeCondition(element, condition){
    if(condition == 'active'){
        element.nextSibling.style.color = 'green';
        if(element.getAttribute('value') == 'Действие'){
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


function recurseOpening(element){
    element.parentNode.style.display = 'block';
    element.nextSibling.style.color = 'green';
    if(blocks_and_lists_of_variants.includes(element)){
        element.parentNode.lastChild.style.display = 'block';
        element.parentNode.lastChild.childNodes.forEach((elem) => {
            elem.querySelector('input[type="checkbox"]').disabled = false;
            elem.firstChild.nextSibling.nextSibling.style.color = 'red';
            elem.firstChild.nextSibling.nextSibling.style.fontWeight  = 'bold';
        });
        findAncestors(element);
    }else if(algorithms_and_chapters.includes(element)){
        first_sub_elem = element.parentNode.lastChild.querySelector('input[type="checkbox"]');
        element.parentNode.lastChild.style.display = 'block';
        if(!(element.parentNode.lastChild.querySelector('span').classList.contains('text-secondary'))){
            findNextAction(element.parentNode.lastChild.firstChild)
        }else{
            first_sub_elem.nextSibling.style.color = 'green';
            if(first_sub_elem.parentNode.lastChild.tagName == 'UL' && first_sub_elem.parentNode.lastChild.getElementsByTagName('li').length > 0){
                recurseOpening(first_sub_elem);
                if(!(all_conditions.includes(first_sub_elem))){
                    first_sub_elem.parentNode.lastChild.style.display = 'block';
                }
            }else{
                first_sub_elem.disabled = false;
                first_sub_elem.nextSibling.style.color = 'red';
                first_sub_elem.nextSibling.style.fontWeight  = 'bold';
                if(first_sub_elem.value == 'Конец алгоритма'){
                    first_sub_elem.checked = true;
                    first_sub_elem.disabled = true;
                    nextAction(first_sub_elem);
                }
            }
        }
        findAncestors(element);
    }else if(all_conditions.includes(element)){
        document.querySelector('#condition').textContent = element.nextSibling.firstChild.innerText;
        current_condition = element;
        setTimeout(()=>{
            popupBg.classList.add('active');
            popup.classList.add('active');
            document.body.classList.add("stop-scrolling");
        }, 1500);
    }
}


function startAction(action){
    if(action.checked == true){
        action.nextSibling.style.color = 'green';
        action.nextSibling.style.fontWeight = 'normal';
        if(action.parentNode.getAttribute('value').includes('Вариант')){
            makeDisableOrAvailableAllSiblings(action.parentNode, true);
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
            recurseOpening(action.parentNode.querySelector('input[type="checkbox"].simple-elements'));
        }else{
            action.nextSibling.style.color = 'blue';
            if(!(action.parentNode.getAttribute('value').includes('Можно сделать') &&
            action.parentNode.parentNode.parentNode.firstChild.nextSibling.checked == true)){
                findAncestors(action);
            }
            if(action.nextSibling.value == 'Конец алгоритма'){
                action.nextSibling.checked = true;
                action.nextSibling.disabled = true;
                nextAction(action.nextSibling);
            }
        }
    }else{
        if(action.parentNode.getAttribute('value').includes('Вариант')){
            makeDisableOrAvailableAllSiblings(action.parentNode, false);
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
        uncheckAncestors(action);
        action.nextSibling.style.color = 'red';
        action.nextSibling.style.fontWeight  = 'bold';
        action.disabled = false;
    }
}


// Обработка закрытия модального окна
closePopupButton.addEventListener('click', (e) => {
    popupBg.classList.remove('active');
    popup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
})


// Делаем неактивными или активными ветки рядом
function makeDisableOrAvailableAllSiblings(elem, ability){
    if(elem.nextSibling){
        next_one = elem.nextSibling
        while(next_one) {
            if(ability == true){
                next_one.style.display = 'none';
                next_one.firstChild.nextSibling.nextSibling.style.color = 'grey';
                next_one.firstChild.nextSibling.nextSibling.style.fontWeight  = 'normal';
            }else{
                next_one.style.display = 'block';
                next_one.firstChild.nextSibling.nextSibling.style.color = 'red';
                next_one.firstChild.nextSibling.nextSibling.style.fontWeight  = 'bold';
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
                next_one.firstChild.nextSibling.nextSibling.style.color = 'grey';
                next_one.firstChild.nextSibling.nextSibling.style.fontWeight  = 'normal';
            }else{
                next_one.style.display = 'block';
                next_one.firstChild.nextSibling.nextSibling.style.color = 'red';
                next_one.firstChild.nextSibling.nextSibling.style.fontWeight  = 'bold';
            }
            if(!next_one.previousSibling) break;
            next_one = next_one.previousSibling
        }
    }
}


function nextAction(action){
    if(/Можно сделать|Нужно сделать|Вариант/.test(action.parentNode.getAttribute('value'))){
        startAction(action);
    }else{
        if(action.checked == true){
            action.nextSibling.style.color = 'blue';
            action.nextSibling.style.fontWeight  = 'normal';
            if(action.parentNode.nextSibling && action.parentNode.nextSibling.getAttribute('value') == 'Далее' && !(action.parentNode.getAttribute('value').includes('Вариант'))){
                if(action.parentNode.nextSibling.lastChild.tagName == 'UL' && action.parentNode.nextSibling.lastChild.getElementsByTagName('li').length > 0){
                    recurseOpening(action.parentNode.nextSibling.firstChild.nextSibling);
                }else{
                    if(action.parentNode.parentNode.parentNode.tagName == 'LI'){
                        action.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"]').nextSibling.style.color = 'green';
                    }
                    if(!(/Можно сделать|Нужно сделать/.test(action.parentNode.getAttribute('value')))){
                        findNextAction(action.parentNode.nextSibling);
                    }
                }
            }else if(action.parentNode.nextSibling && !(action.parentNode.nextSibling.querySelector('span').classList.contains('text-secondary'))
            && !(action.parentNode.nextSibling.getAttribute('value') == 'Иначе')){
                showNotification(action.parentNode.nextSibling.querySelector('span'), 'comment');
            }else{
                findAncestors(action);
            }
            if(action.value == 'Конец алгоритма'){
                showNotification(action, 'ending');
            }
            if(blocks_out.size > 0){
                actionInBlock([...blocks_out].pop(), 'block');
            }
        }else{
            removeNotification(notificationPopup.querySelector('i'));
            action.nextSibling.style.fontWeight = 'normal';
            uncheckAncestors(action);
            if(!(action.value == 'Действие')){
                action.disabled = true;
                recurseOpening(action);
            }else{
                action.nextSibling.style.color = 'red';
                action.nextSibling.style.fontWeight  = 'bold';
                action.disabled = false;
            }
        }
    }
}


// Скрывает альтернативный ответ на условие и делает активным первый чекбокс, соответствующий ответу
function answerCondition(answer){
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
             findNextAction(condition_element);
             if(condition_element.firstChild.nextSibling){
                findAncestors(condition_element.firstChild.nextSibling);
             }else{
                findAncestors(condition_element.firstChild);
             }
        }else{
            if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
            == "Тогда").length > 0){
                Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Тогда")[0].style.display = 'none';
            }
            findNextAction(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
            == "Иначе")[0])
            if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Иначе")[0].firstChild.nextSibling){
                findAncestors(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Иначе")[0].firstChild.nextSibling);
            }else{
                findAncestors(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value')
                == "Иначе")[0].firstChild);
            }
        }
        condition_element.parentNode.style.display = 'block';
    }else{
        current_condition.checked = true;
        current_condition.disabled = false;
        current_condition.nextSibling.style.color = 'blue';
        findAncestors(current_condition);
    }
}


// Проверяет все ли элементы в блоке отмечены
function actionInBlock(examined_block, type){
    examined_block.nextSibling.style.color = 'green';
    is_all = 0;
    add_comment = 0;
    if(type == 'block'){
        examined_block.parentNode.lastChild.childNodes.forEach((elem) => {
            if(elem.firstChild.nextSibling.nextSibling.style.color !== 'blue'){
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
        examined_block.checked = true;
        examined_block.disabled = false;
        if(add_comment > 0){
            if(add_comment > 1){
                showNotification(String('В блоке '+examined_block.nextSibling.firstChild.textContent+' остались невыполненные необязательные элементы'), 'block_notification');
            }else{
                showNotification(String('В блоке '+examined_block.nextSibling.firstChild.textContent+' остался невыполненный необязательный элемент'), 'block_notification');
            }
        }
        findAncestors(examined_block);
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
}


function toggleHiddenElement(element) {
    if(element.classList.contains("bi-play-circle-open")){
        element.classList.remove("bi-play-circle-open")
        element.classList.add("bi-play-circle-close");
        element.parentNode.lastChild.style.display = 'none';
    }else{
        element.classList.remove("bi-play-circle-close")
        element.classList.add("bi-play-circle-open");
        element.parentNode.lastChild.style.display = 'block';
    }
}


// Смотрит внутри чего был элемент
function findAncestors(child){
    ancestor = child.parentNode
    if(ancestor.parentNode.parentNode.tagName == 'LI'){
        ancestor = ancestor.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements')
        if(ancestor.value == 'Блок'){
            actionInBlock(ancestor, 'block');
        }else if(ancestor.value == 'Алгоритм' || ancestor.value == 'Раздел' || ancestor.value == 'Условие'){
            if(child.checked == true || child.tagName == 'SPAN'){
                if(child.parentNode.nextSibling && child.parentNode.nextSibling.getAttribute('value') == 'Далее'){
                    findNextAction(child.parentNode.nextSibling)
                }else if(child.parentNode.nextSibling && !(child.parentNode.nextSibling.querySelector('span').classList.contains('text-secondary'))
                && !(child.parentNode.nextSibling.getAttribute('value') == 'Иначе')){
                    showNotification(child.parentNode.nextSibling.querySelector('span'), 'comment');
                }else{
                    ancestor.checked = true;
                    ancestor.disabled = false;
                    ancestor.nextSibling.style.color = 'blue';
                    actionInBlock(ancestor, 'notblock');
                    findAncestors(ancestor);
                }
            }
        }else if(ancestor.value == 'Выбор'){
            actionInBlock(ancestor, 'notblock');
        }else if(!ancestor.value){
            if(child.parentNode.nextSibling){
                findNextAction(child.parentNode.nextSibling);
            }
        }
    }else{
    // Если в главном блоке
        if(child.checked == true){
            if(child.parentNode.nextSibling && child.parentNode.nextSibling.getAttribute('value') == 'Далее'){
                findNextAction(child.parentNode.nextSibling);
            }
        }
    }
}


// Находит следующий элемент с чекбоксом
function findNextAction(next_action){
    if(next_action.querySelector('input[type="checkbox"]')){
        next_action.style.display = 'block';
        if(next_action.querySelector('input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && next_action.querySelector('input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
            recurseOpening(next_action.querySelector('input[type="checkbox"].simple-elements'));
        }else{
            next_action.querySelector('input[type="checkbox"]').disabled = false;
            next_action.querySelector('input[type="checkbox"]').nextSibling.style.color = 'red';
            next_action.querySelector('input[type="checkbox"]').nextSibling.style.fontWeight  = 'bold';
            if(next_action.querySelector('input[type="checkbox"]').value == 'Конец алгоритма'){
                next_action.querySelector('input[type="checkbox"]').checked = true;
                next_action.querySelector('input[type="checkbox"]').disabled = true;
                nextAction(next_action.querySelector('input[type="checkbox"]'));
            }
        }
    }else{
        if(!(next_action.querySelector('span').classList.contains('text-secondary'))){
            showNotification(next_action.querySelector('span'), 'comment');
        }
        if(next_action.nextSibling && next_action.nextSibling.getAttribute('value') == 'Далее'){
            findNextAction(next_action.nextSibling)
        }
    }
}


// Возвращает алгоритм в состояние, как будто пользователь не отмечал чекбокс
function uncheckAncestors(action){
    ancestor = action.parentNode
    ancestor.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
        elem.checked = false;
        elem.disabled = true;
        elem.nextSibling.style.color = 'black';
        elem.nextSibling.style.fontWeight = 'normal';
        if(elem.parentNode.getAttribute('value') == 'Далее' && !(elem == action)){
            elem.parentNode.style.display = 'none';
        }else{
            elem.parentNode.style.display = 'block';
        }
    })
    ancestor.querySelectorAll('li > i').forEach((elem) => {
        elem.remove()
    })
    action.disabled = false;
    if(ancestor.parentNode.parentNode.tagName == 'LI'){
        ancestor = ancestor.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements')
        observed_checkbox = action
        if(ancestor.checked == true){
            while(ancestor.checked == true){
                ancestor.checked = false;
                ancestor.disabled = true;
                if(ancestor.parentNode.lastChild.tagName == 'UL' && !(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value')))
                && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                    ancestor.nextSibling.style.color = 'green';
                }else if(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value'))){
                    ancestor.nextSibling.style.color = 'green';
                    ancestor.nextSibling.style.fontWeight = 'normal';
                    ancestor.checked = true;
                    ancestor.disabled = false;
                }else{
                    ancestor.nextSibling.style.color = 'red';
                    ancestor.nextSibling.style.fontWeight = 'bold';
                }
                if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                    uncheckSiblings(observed_checkbox.parentNode.nextSibling)
                }
                if(!(ancestor.parentNode.parentNode.parentNode.tagName == 'LI')){
                    uncheckSiblings(ancestor.parentNode.nextSibling)
                    break;
                }
                observed_checkbox = ancestor;
                ancestor = ancestor.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements');
                if(ancestor.checked == false){
                    if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                        uncheckSiblings(observed_checkbox.parentNode.nextSibling);
                    }
                    if(ancestor.parentNode.lastChild.tagName == 'UL' && !(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value')))
                    && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                        ancestor.nextSibling.style.color = 'green';
                        ancestor.nextSibling.style.fontWeight = 'normal';
                    }else{
                        ancestor.nextSibling.style.color = 'red';
                        ancestor.nextSibling.style.fontWeight = 'bold';
                    }
                }
            }
        }else{
            if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                uncheckSiblings(action.parentNode.nextSibling);
            }
            if(ancestor.parentNode.lastChild.tagName == 'UL' && !(/Можно сделать|Нужно сделать|Вариант/.test(ancestor.parentNode.getAttribute('value')))
            && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                ancestor.nextSibling.style.color = 'green';
                ancestor.nextSibling.style.fontWeight = 'normal';
            }else{
                ancestor.nextSibling.style.color = 'red';
                ancestor.nextSibling.style.fontWeight = 'bold';
            }
        }
    }else{
        uncheckSiblings(action.parentNode.nextSibling);
    }
}


function uncheckSiblings(closest_sibling){
    while(closest_sibling){
        if(!(closest_sibling.querySelector('input[type="checkbox"].simple-elements'))){
            closest_sibling = closest_sibling.nextSibling
        }else{
            if(closest_sibling.querySelector('input[type="checkbox"].simple-elements').nextSibling.style.color == 'black') break
            closest_sibling.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
                elem.checked = false;
                elem.disabled = true;
                elem.nextSibling.style.color = 'black';
                elem.nextSibling.style.fontWeight = 'normal';
                if(elem.parentNode.getAttribute('value') == 'Далее'){
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
}


// Показывает уведомление о завершении алгоритма или комментарий
function showNotification(elem, type){
    if(type == 'ending'){
        let name_of_completed_algorithm = 'Вы прошли алгоритм "';
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
    }else{
        comment = document.createElement("div");
        comment.classList.add('notification');
        inner_title = document.createElement("h3");
        closeIcon = document.createElement("i");
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
    }
}


function removeNotification(notification){
    if(notification.parentNode.classList.contains('end_of_algorithm')){
        notification.parentNode.style.display = 'none';
    }else{
        notification.parentNode.remove();
    }
}


function onButtonSendClick(status){
    previous_result = '';
    flag = true;
    if(status == 'same'){
        if (urlParams.has('previous_works')) {
            previous_result = urlParams.get('previous_works');
        }
        current_name = previous_result;
    }else{
        current_name = document.querySelector('#work_name').value
        if(current_name){
            if(Array.from(document.querySelectorAll('.select__item')).filter(item => item.textContent.trim() == current_name).length
            > 0 && !(previous_result == current_name)){
                document.querySelector('#warning').style.display = 'block';
                document.querySelector('#warning').textContent = 'Недопустимое название';
                flag = false;
            }else{
                document.querySelector('#warning').style.display = 'none';
                flag = true;
            }
        }
    }
    if(flag){
        list_to_send = [];
        all_elements = document.querySelectorAll('span.algorithm-element')
        all_elements.forEach((elem)=>{
            knowledge_name = elem.firstChild.innerText;
            if(elem.style.color == 'blue'){
                list_to_send.push([knowledge_name, 'completed'])
            }else if(elem.style.color == 'green'){
                list_to_send.push([knowledge_name, 'active'])
            }else if(elem.style.color == 'red'){
                list_to_send.push([knowledge_name, 'available'])
            }
        });
        $.ajax({
            data: { 'values' : JSON.stringify(list_to_send), 'work' : current_name, 'previous_result' : previous_result},
            url: document.location.pathname + '/algorithm_result/',
            success: function (response) {
                    saveBg.classList.add('active');
                    savePopup.classList.add('active');
                    document.body.classList.add("stop-scrolling");
                document.querySelector('#work_name').parentNode.innerHTML = 'Сохранение прошло успешно, через '+
                'несколько секунд вас перенаправит на страницу с сохраненным алгоритмом';
                setTimeout(()=>{
                    if(document.location.pathname.includes("previous_work")){
                        window.location.href = document.location.pathname.split('?')[0] + '?previous_works='+current_name;
                    }else{
                        window.location.href = document.location.pathname + '?previous_works='+current_name;
                    }
                }, 1500);
            }
        });
    }
}