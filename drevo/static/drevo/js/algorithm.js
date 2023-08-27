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


function ShowFirst(){
    document.querySelector('.basic input[type="checkbox"]').nextSibling.style.color = 'red'
    if(document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && document.querySelector('.basic input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
        recurseOpening(document.querySelector('.basic input[type="checkbox"]'));
    }else{
        document.querySelector('.basic input[type="checkbox"]').disabled = false;
    }
}

ShowFirst();


function recurseOpening(element){
    findAncestors(element);
    if(blocks_and_lists_of_variants.includes(element)){
        element.nextSibling.style.color = 'green';
        element.parentNode.lastChild.style.display = 'block';
        element.parentNode.lastChild.childNodes.forEach((elem) => {
            elem.querySelector('input[type="checkbox"].start').disabled = false;
            elem.firstChild.nextSibling.nextSibling.nextSibling.style.color = 'red';
        });
    }else if(algorithms_and_chapters.includes(element)){
        first_sub_elem = element.parentNode.lastChild.querySelector('input[type="checkbox"]')
        element.parentNode.lastChild.style.display = 'block';
        first_sub_elem.nextSibling.style.color = 'green'
        if(first_sub_elem.parentNode.lastChild.tagName == 'UL' && first_sub_elem.parentNode.lastChild.getElementsByTagName('li').length > 0){
            recurseOpening(first_sub_elem);
            if(!(all_conditions.includes(first_sub_elem))){
                first_sub_elem.parentNode.lastChild.style.display = 'block';
            }
        }else{
            first_sub_elem.disabled = false;
        }
    }else if(all_conditions.includes(element)){
        element.nextSibling.style.color = 'green';
        document.querySelector('#condition').textContent = element.nextSibling.textContent;
        current_condition = element;
        popupBg.classList.add('active');
        popup.classList.add('active');
        document.body.classList.add("stop-scrolling");
    }
}


function startAction(action){
    if(action.checked == true){
        action.nextSibling.nextSibling.style.color = 'green';
        if(action.parentNode.getAttribute('value').includes('Вариант')){
            makeDisableOrAvailableAllSiblings(action.parentNode, true);
        }else if(action.parentNode.getAttribute('value').includes('Состав блока')){
            if(!(action.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements') in blocks_out)){
                blocks_out.add(action.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements'))
            }
        }
        if(action.parentNode.lastChild.tagName == 'UL' && action.parentNode.lastChild.getElementsByTagName('li').length > 0){
            if(!all_conditions.includes(action.parentNode.querySelector('input[type="checkbox"].simple-elements'))){
                action.parentNode.lastChild.style.display = 'block';
            }
            recurseOpening(action.parentNode.querySelector('input[type="checkbox"].simple-elements'));
        }else{
            action.parentNode.querySelector('input[type="checkbox"].simple-elements').disabled = false;
            findAncestors(action.parentNode.querySelector('input[type="checkbox"].simple-elements'));
        }
    }else{
        if(action.parentNode.getAttribute('value').includes('Вариант')){
            makeDisableOrAvailableAllSiblings(action.parentNode, false);
        }
        if(action.parentNode.lastChild.tagName == 'UL' && action.parentNode.lastChild.getElementsByTagName('li').length > 0){
            action.parentNode.lastChild.style.display = 'none';
        }
        action.parentNode.querySelector('input[type="checkbox"].simple-elements').checked = false;
        action.parentNode.querySelector('input[type="checkbox"].simple-elements').disabled = true;
        uncheckAncestors(action.parentNode.querySelector('input[type="checkbox"].simple-elements'));
        action.nextSibling.nextSibling.style.color = 'red';
        action.disabled = false;
    }
}


// обработка закрытия модального окна
closePopupButton.addEventListener('click', (e) => {
    popupBg.classList.remove('active');
    popup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
})


// делаем неактивными или активными ветки рядом
function makeDisableOrAvailableAllSiblings(elem, ability){
    if(elem.nextSibling){
        next_one = elem.nextSibling
        while(next_one) {
            if(ability == true){
                next_one.firstChild.nextSibling.nextSibling.nextSibling.style.color = 'grey';
            }else{
                next_one.firstChild.nextSibling.nextSibling.nextSibling.style.color = 'red';
            }
            next_one.querySelectorAll('input[type="checkbox"].start').forEach((elem) => {
                elem.disabled = ability;
            });
            if(!next_one.nextSibling) break;
            next_one = next_one.nextSibling
        }
    }
    if(elem.previousSibling){
        next_one = elem.previousSibling
        while(next_one) {
            if(ability == true){
                next_one.firstChild.nextSibling.nextSibling.nextSibling.style.color = 'grey';
            }else{
                next_one.firstChild.nextSibling.nextSibling.nextSibling.style.color = 'red';
            }
            next_one.querySelectorAll('input[type="checkbox"].start').forEach((elem) => {
                elem.disabled = ability;
            });
            if(!next_one.previousSibling) break;
            next_one = next_one.previousSibling
        }
    }
}


function nextAction(action){
    if(action.checked == true){
        action.nextSibling.style.color = 'blue';
        if(action.parentNode.nextSibling && action.parentNode.nextSibling.style.display != 'none' && !(action.parentNode.getAttribute('value').includes('Вариант'))){
            if(action.parentNode.nextSibling.lastChild.tagName == 'UL' && action.parentNode.nextSibling.lastChild.getElementsByTagName('li').length > 0){
                recurseOpening(action.parentNode.nextSibling.firstChild.nextSibling);
            }else{
                if(!(action.parentNode.getAttribute('value').includes('Состав блока'))){
                    findNextAction(action.parentNode.nextSibling);
                }
                if(action.parentNode.parentNode.parentNode.tagName == 'LI'){
                    action.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"]').nextSibling.style.color = 'green';
                }
            }
        }else{
            findAncestors(action);
        }
        if(action.value == 'Конец алгоритма'){
            document.getElementById('end').style.display = 'block';
        }
        if(blocks_out.size > 0){
            actionInBlock([...blocks_out].pop(), 'block');
        }
    }else{
        if(document.getElementById('end').style.display == 'block'){
            document.getElementById('end').style.display = 'none';
        }
        uncheckAncestors(action);
        if(action.previousSibling.classList.contains('start')){
            action.nextSibling.style.color = 'green';
            action.previousSibling.checked = true;
        }else{
            action.nextSibling.style.color = 'red';
            action.disabled = false;
        }
    }
}


// скрывает альтернативный ответ на условие и делает активным первый чекбокс, соответствующий ответу
function answerCondition(answer){
    popupBg.classList.remove('active');
    popup.classList.remove('active');
    document.body.classList.remove("stop-scrolling");
    if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == ''+answer+'').length > 0){
        flag = 0;
        if(answer == 'Тогда'){
            condition_element = current_condition.parentNode.lastChild.firstChild
            if(condition_element.parentNode.querySelector('input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && condition_element.parentNode.querySelector('input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
                recurseOpening(condition_element.querySelector('input[type="checkbox"]'));
            }else{
                condition_element.querySelector('input[type="checkbox"]').disabled = false;
                condition_element.querySelector('input[type="checkbox"].simple-elements').nextSibling.style.color = 'green';
            }
            if(Array.from(current_condition.parentNode.lastChild.childNodes).filter(item => item.getAttribute('value') == "Иначе").length > 0){
                while(condition_element){
                    if(condition_element.getAttribute('value').includes('Иначе')){
                        flag = 1;
                    }
                    if(flag == 1){
                        condition_element.style.display = 'none';
                    }else{
                        condition_element.style.display = 'block';
                    }
                    if(!condition_element.nextSibling) break;
                    condition_element = condition_element.nextSibling
                }
            }
            condition_element.parentNode.style.display = 'block';
        }else{
            first_checkbox_founded = false;
            condition_element = current_condition.parentNode.lastChild.firstChild
            while(condition_element){
                if(condition_element.getAttribute('value').includes('Иначе')){
                    flag = 1;
                }
                if(flag == 0){
                    condition_element.style.display = 'none';
                }else if(flag==1 && !first_checkbox_founded){
                    condition_element.style.display = 'block';
                    if(condition_element.querySelector('input[type="checkbox"]')){
                        if(condition_element.querySelector('input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && condition_element.querySelector('input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
                            recurseOpening(condition_element.querySelector('input[type="checkbox"]'));
                        }else{
                            condition_element.querySelector('input[type="checkbox"]').disabled = false;
                            condition_element.querySelector('input[type="checkbox"].simple-elements').nextSibling.style.color = 'green';
                        }
                        first_checkbox_founded = true;
                    }
                }else{
                    condition_element.style.display = 'block';
                }
                if(!condition_element.nextSibling) break;
                condition_element = condition_element.nextSibling
            }
            condition_element.parentNode.style.display = 'block';
        }
    }else{
        current_condition.checked = true;
        current_condition.nextSibling.style.color = 'blue';
        findAncestors(current_condition);
    }
}


var iconElement = document.createElement("i");
iconElement.className = "bi bi-play-circle-close";
iconElement.setAttribute("onclick", "toggleHiddenElement(this);");

// проверяет все ли элементы в блоке отмечены
function actionInBlock(examined_block, type){
    examined_block.nextSibling.style.color = 'green';
    is_all = 0
    examined_block.parentNode.lastChild.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
        if(popup.classList.contains('active') || (elem.previousSibling.checked == true && elem.checked == false)){
            is_all = 1;
        }
        if(elem.checked == false && elem.disabled == false && elem.parentNode.parentNode.style.display != 'none'
        && elem.parentNode.style.display != 'none'){
            is_all = 1;
        }
    });
    if(is_all == 0){
        examined_block.nextSibling.style.color = 'blue';
        examined_block.checked = true;
        findAncestors(examined_block);
        if(!(examined_block.nextSibling.nextSibling.tagName == 'I')){
            examined_block.nextSibling.after(iconElement.cloneNode(true));
            examined_block.parentNode.lastChild.style.display = 'none';
        }else{
            toggleHiddenElement(examined_block.nextSibling.nextSibling);
        }
        if(type == 'block'){
            blocks_out.delete(examined_block);
        }
    }
}


function toggleHiddenElement(element) {
    if (element.classList.contains("bi-play-circle-open")) {
        element.classList.remove("bi-play-circle-open")
        element.classList.add("bi-play-circle-close");
        element.parentNode.lastChild.style.display = 'none';
    } else {
        element.classList.remove("bi-play-circle-close")
        element.classList.add("bi-play-circle-open");
        element.parentNode.lastChild.style.display = 'block';
    }
}


// смотрит внутри чего был элемент
function findAncestors(child){
    ancestor = child.parentNode
    if(ancestor.parentNode.parentNode.tagName == 'LI'){
        ancestor = ancestor.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements')
        if(ancestor.value == 'Блок'){
            actionInBlock(ancestor, 'block');
        }else if(ancestor.value == 'Алгоритм' || ancestor.value == 'Раздел' || ancestor.value == 'Условие'){
            if(child.checked == true){
                if(child.parentNode.nextSibling && child.parentNode.nextSibling.style.display != 'none'){
                    findNextAction(child.parentNode.nextSibling)
                }else{
                    ancestor.checked = true;
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
    // если в главном блоке
        if(child.checked == true){
            if(child.parentNode.nextSibling && child.parentNode.nextSibling.style.display != 'none'){
                findNextAction(child.parentNode.nextSibling);
            }
        }
    }
}


// находит следующий элемент с чекбоксом
function findNextAction(next_action){
    if(next_action.querySelector('input[type="checkbox"]')){
        if(next_action.querySelector('input[type="checkbox"]').parentNode.lastChild.tagName == 'UL' && next_action.querySelector('input[type="checkbox"]').parentNode.lastChild.getElementsByTagName('li').length > 0){
            recurseOpening(next_action.querySelector('input[type="checkbox"].simple-elements'));
        }else{
            next_action.querySelector('input[type="checkbox"]').disabled = false;
            next_action.querySelector('input[type="checkbox"]').nextSibling.style.color = 'green';
        }
    }else{
        if(next_action.nextSibling && next_action.nextSibling.style.display != 'none'){
            findNextAction(next_action.nextSibling)
        }
    }
}


// возвращает алгоритм в состояние, как будто пользователь не отмечал чекбокс
function uncheckAncestors(action){
    ancestor = action.parentNode
    ancestor.querySelectorAll('input[type="checkbox"]').forEach((elem) => {
        elem.checked = false;
        elem.disabled = true;
        elem.nextSibling.style.color = 'black';
    })
    ancestor.querySelectorAll('i.bi').forEach((elem) => {
        elem.remove()
    })
    if(action.previousSibling.classList.contains('start')){
        action.previousSibling.disabled = false;
    }else{
        action.disabled = false;
    }
    if(ancestor.parentNode.parentNode.tagName == 'LI'){
        ancestor = ancestor.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements')
        observed_checkbox = action
        if(ancestor.checked == true){
            while(ancestor.checked == true){
                if(ancestor.parentNode.lastChild.tagName == 'UL' && !(ancestor.parentNode.getAttribute('value') in ['Вариант', 'Состав блока'])
                && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                    ancestor.nextSibling.style.color = 'green';
                }else if(ancestor.previousSibling.checked == true){
                    ancestor.nextSibling.style.color = 'green';
                }else{
                    ancestor.nextSibling.style.color = 'red';
                }
                if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                    uncheckSiblings(observed_checkbox.parentNode.nextSibling)
                }
                ancestor.checked = false;
                if(!(ancestor.parentNode.parentNode.parentNode.tagName == 'LI')){
                    uncheckSiblings(ancestor.parentNode.nextSibling)
                    break;
                }
                observed_checkbox = ancestor;
                ancestor = ancestor.parentNode.parentNode.parentNode.querySelector('input[type="checkbox"].simple-elements');
                if(ancestor.checked == false){
                    if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                        uncheckSiblings(observed_checkbox.parentNode.nextSibling)
                    }
                    if(ancestor.parentNode.lastChild.tagName == 'UL' && ancestor.parentNode.lastChild.querySelector('input[type="checkbox"]:checked')
                    && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                        ancestor.nextSibling.style.color = 'green';
                    }else{
                        ancestor.nextSibling.style.color = 'red';
                    }
                }
            }
        }else{
            if(!(ancestor.getAttribute('value') == 'Выбор') && !(ancestor.getAttribute('value') == 'Блок')){
                uncheckSiblings(action.parentNode.nextSibling);
            }
            if(ancestor.parentNode.lastChild.tagName == 'UL' && !(ancestor.parentNode.getAttribute('value') in ['Вариант', 'Состав блока'])
            && ancestor.parentNode.lastChild.getElementsByTagName('li').length > 0){
                ancestor.nextSibling.style.color = 'green';
            }else{
                ancestor.nextSibling.style.color = 'red';
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
            })
            closest_sibling.querySelectorAll('i.bi').forEach((elem) => {
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