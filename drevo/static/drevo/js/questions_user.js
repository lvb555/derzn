document.addEventListener('DOMContentLoaded', () => {

    // скролл к последнему месту отправки формы
    if (window.localStorage.getItem('scroll_place')) {
        window.scrollTo(0,window.localStorage.getItem('scroll_place'))
        window.localStorage.removeItem('scroll_place')
    }
    
    // отображение имени файла
    if (document.querySelector('.file')) {
        document.querySelectorAll('.file').forEach((e) => {
            const part = 'proof/'
            let name_file = e.innerHTML
            name_file = name_file.replace(part, '')
            e.innerHTML = name_file
        })
    }

    // отображение кнопки +
    const block_of_ans = document.querySelectorAll('.block')
    block_of_ans.forEach((e) => {
        if (e.querySelector('.edit_menu')) {
            e.querySelector('.plus').remove()
        }
    })

    
    document.addEventListener('click', event => {

        // кнопка отмены в попап
        if (event.target.id === 'cancel_delete' || event.target.className === 'popup_bg active') {
            close_popup()
        }
        
        // кнопка ДА в попап
        if (event.target.id === 'submit_delete') {
            const delete_info = document.querySelector('#submit_delete');
            let operation = delete_info.name;
            let id_answer = delete_info.value;
            async_edit(operation, id_answer)
        }
        
        // кнопка ...
        if (event.target.className === 'dots') {
            let menu = event.target.parentElement.querySelector('.menu')
            if (menu.style.display === 'block') {
                event.target.parentElement.querySelector('.menu').style.display = 'none'
            }
            else{
                menu.style.display = 'block'
            }
        }
        else if (event.target.className !== 'dots') {
            document.querySelectorAll('.menu').forEach((e) => {
                e.style.display = 'none'
            })
        }

        // разделы меню
        if (event.target.parentElement.className === 'menu') {
            let id_ans = event.target.parentElement.id
            let option = event.target.className
            menu(option, id_ans)
        }
        
        // функция кнопки отмена
        if (event.target.value === 'cancel') {
            let content_block = event.target.parentElement.parentElement.parentElement
            if (content_block.parentElement.querySelector('.answer_text')) {
                event.target.parentElement.parentElement.parentElement.querySelector('.answer_text').style.display = 'inline'
            }
            event.target.parentElement.parentElement.innerHTML =''
        }

        // функция кнопки сохранить
        if (event.target.name === 'save') {
            let operation;
            let new_content_block = event.target.parentElement.parentElement;
            let id_answer = event.target.value;
            if (new_content_block.querySelector('textarea')) {
                operation = new_content_block.querySelector('textarea').name
            }
            else if (new_content_block.querySelector('input[type="file"]')) {
                operation = new_content_block.querySelector('input[type="file"]').name
            }
            async_edit(operation, id_answer)
        }

        // кнопка сохранить в новом ответе 
        if (event.target.name === 'save_new_answer') {
            id_question = event.target.value
            async_answer(id_question)
        }

        // функционал кнопки +
        if (event.target.className === 'plus') {
            let block = event.target.parentElement
            block.querySelector('.new_form').style.display = 'block'
            block.querySelector('.plus').remove()
        }
    })

    // запись скролла при отправке формы
    document.addEventListener('submit', () => {
        window.localStorage.setItem('scroll_place', window.scrollY)
    })   
})


function menu(option, id_answer) {
    if (option === 'edit_text' || option === 'add_file' || option === 'add_text') {

        document.getElementById(id_answer).style.display = 'none'
        let content = document.getElementById(id_answer).parentElement.parentElement.querySelector('.content')
        let new_content = document.getElementById(id_answer).parentElement.parentElement.querySelector('.new_content')

        if (option === 'edit_text') {
            const old_text = content.querySelector('.answer_text')
            old_text.style.display = 'none'
            new_content.innerHTML = `
            <textarea name="edit_text" id="" cols="40" rows="10" class="edit_answer" placeholder="Ваш ответ">${old_text.innerHTML}</textarea>
            <div>
                <button class="button-cancel" value="cancel">Отмена</button>
                <button class="button" name="save" value="${id_answer}">Сохранить</button>
            </div>
            `
        }
        
        else if (option === 'add_file') {
            new_content.innerHTML = `
            <input type="file" name="add_file" class="id_file" multiple>
            <div>
                <button class="button-cancel" value="cancel">Отмена</button>
                <button class="button" name="save" value="${id_answer}">Сохранить</button>
            </div>
            `
        }  
        
        else {
            new_content.innerHTML = `
            <textarea name="add_text" id="" cols="40" rows="10" class="edit_answer" placeholder="Ваш ответ"></textarea>
            <div>
                <button class="button-cancel" value="cancel">Отмена</button>
                <button class="button" name="save" value="${id_answer}">Сохранить</button>
            </div>
            `
        }
    }
        
    else if (option === 'delete_answer') {
        document.getElementById('label_for_popup').innerHTML = 'Удалить ответ?'
        popup_form(option, id_answer)
    }
    
    else if (option === 'delete_file') {
        document.getElementById('label_for_popup').innerHTML = 'Удалить файл?'
        popup_form(option, id_answer)
    }
    
    else if (option === 'delete_text') {
        document.getElementById('label_for_popup').innerHTML = 'Удалить текст?'
        popup_form(option, id_answer)
    }
}


function popup_form(option, id_answer) {
    let popupBg = document.querySelector('.popup_bg');
    let popup = document.querySelector('.popup');
    document.getElementById('submit_delete').setAttribute('name', option)
    document.getElementById('submit_delete').setAttribute('value', id_answer)
    popupBg.classList.add('active')
    popup.classList.add('active')
}

function close_popup() {
    let popupBg = document.querySelector('.popup_bg');
    let popup = document.querySelector('.popup');
    popupBg.classList.remove('active');
    popup.classList.remove('active');
}

function async_edit(operation, id_answer) {

    let znanie = document.getElementsByName('knowledge')[0].value;
    let csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    
    if (operation === 'delete_file' || operation === 'delete_answer' || operation === 'delete_text') {
    
        fetch(`/drevo/znanie/${znanie}/questions_user`, {
            method: 'PUT',
            headers: {
                'X-CSRFTOKEN': csrf
            },
            body: JSON.stringify({
                'operation': operation,
                'answer': id_answer
            })
        })
        .then (response => response.status)
        .then (status => {
            if (status === 200) {
                location.reload()
            }
        })
    }
    
    else if (operation === 'edit_text') {

        let answer = document.getElementById(id_answer).parentElement.parentElement
        let old_text = answer.querySelector('.answer_text').innerHTML
        let new_text = answer.querySelector('textarea[name="edit_text"]').value
        
        if (old_text !== new_text && new_text !== '') {
            
            fetch(`/drevo/znanie/${znanie}/questions_user`, {
                method: 'PUT',
                headers: {
                    'X-CSRFTOKEN': csrf
                },
                body: JSON.stringify({
                    'operation': operation,
                    'answer': id_answer,
                    'new_text': new_text
                    
                })
            })
            .then (response => response.status)
            .then (status => {
                if (status === 200) {
                    location.reload()
                }
            })
        }
    }
    
    else if (operation === 'add_file') {

        const formData = new FormData();
        let file_block = document.getElementById(id_answer).parentElement.parentElement;
        let file_field = file_block.querySelector('input[type="file"]');
        
        if (file_field.files[0]) {
            
            formData.append('operation', operation);
            formData.append('answer_id', id_answer);
            formData.append('new_file', file_field.files[0]);
            
            fetch(`/drevo/znanie/${znanie}/questions_user`, {
                method: 'POST',
                headers: {
                    'X-CSRFTOKEN': csrf
                },
                body: formData          
            })
            .then (response => response.status)
            .then (status => {
                if (status === 200) {
                    location.reload()
                }
            })
        }
    }
    
    else if (operation === 'add_text'){
        
        let answer = document.getElementById(id_answer).parentElement.parentElement
        let text_answer = answer.querySelector('textarea[name="add_text"]').value
        
        if (text_answer !== '') {
            
            fetch(`/drevo/znanie/${znanie}/questions_user`, {
                method: 'PUT',
                headers: {
                    'X-CSRFTOKEN': csrf
                },
                body: JSON.stringify({
                    'operation': operation,
                    'answer': id_answer,
                    'text_answer': text_answer
                    
                })
            })
            .then (response => response.status)
            .then (status => {
                if (status === 200) {
                    location.reload()
                }
            })
        }       
    }   
}

function async_answer(id_question) {

    let znanie = document.getElementsByName('knowledge')[0].value;
    let csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let new_form = document.querySelector(`button[value="${id_question}"]`).parentElement.parentElement;
    
    let formData = new FormData();

    if (new_form.querySelector('textarea').value !== '') {
        let text = new_form.querySelector('textarea').value
        formData.append('text', text)
    }
    if (new_form.querySelector('input[type="file"]')) {
        let file = new_form.querySelector('input[type="file"]')
        if (file.files[0]) {
            formData.append('file', file.files[0])
        }
    }
    
    
    if (formData.get('file') || formData.get('text')) {

        formData.append('question_id', id_question)           
        fetch(`/drevo/znanie/${znanie}/questions_user`, {
            method: 'POST',
            headers: {
                'X-CSRFTOKEN': csrf
            },
            body: formData          
        })
        .then (response => response.status)
        .then (status => {
            if (status === 200) {
                location.reload()
            }
        })
    }    
}