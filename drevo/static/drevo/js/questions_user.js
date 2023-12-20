document.addEventListener('DOMContentLoaded', () => {

    // скролл к последнему месту оправки формы
    if (window.localStorage.getItem('scroll_place')) {
        window.scrollTo(0,window.localStorage.getItem('scroll_place'))
        window.localStorage.removeItem('scroll_place')
    }

    // отбражение редактируемых ответов и прикрепленных к ним файлов
    if (document.querySelector('.edit')) {
        document.querySelectorAll('.edit').forEach( (e) => {
            e.parentElement.querySelector('.new_answer').remove()
            if (e.querySelector('.id_file')) {
                if (e.querySelector('.cross')) {
                    e.parentElement.querySelector('.id_file').style.display = 'none'
                }
                if (e.querySelector('.edit_answer').innerHTML === '-') {
                    e.querySelector('.edit_answer').innerHTML = ''
                }
            }
        })
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
            // e.querySelector('.new_form').style.display = 'block'
            e.querySelector('.plus').remove()
        }
    })

    
    document.addEventListener('click', event => {

        // кнопка отмены в попап
        if (event.target.id === 'cancel_delete' || event.target.className === 'popup_bg active') {
            close_popup()
        }
        
        // кнопка ДА удаления
        if (event.target.id === 'submit_delete') {
            const delete_info = document.querySelector('#submit_delete')
            let operation = delete_info.name
            let id_answer = delete_info.value
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
        if(event.target.value === 'cancel') {
            event.target.parentElement.parentElement.parentElement.querySelector('.answer_text').style.display = 'inline'
            event.target.parentElement.parentElement.innerHTML =''
        }

        // функционал кнопки +
        if (event.target.className === 'plus') {
            let block = event.target.parentElement
            block.querySelector('.new_form').style.display = 'block'
            block.querySelector('.plus').remove()
        }
        
        // функционал кнопки х
        // if (event.target.className === 'cross') {
            //     let block = event.target.parentElement
            //     if (block.parentElement.querySelector('.id_file').style.display === 'inline'){
                //         block.querySelector('.point').style.filter = 'blur(0px)'
                //         block.querySelector('.file').style.filter = 'blur(0px)'
                //         block.parentElement.querySelector('.id_file').style.display = 'none'
                //         block.parentElement.querySelector('.button').innerHTML = 'Сохранить'
                //         block.parentElement.querySelector('.button').style.backgroundColor = '#083E2F'
                //         block.parentElement.querySelector('.delete').style.display = 'inline'
                //         if (block.parentElement.delete_file) {
                    //             block.parentElement.delete_file.remove()       
                    //         }
                    //         block.parentElement.edit_file.value = ''
                    //     }
                    //     else {
                        //         block.querySelector('.point').style.filter = 'blur(3px)'
                        //         block.querySelector('.file').style.filter = 'blur(3px)'
                        //         block.parentElement.querySelector('.id_file').style.display = 'inline'
                        //         block.parentElement.querySelector('.button').innerHTML = 'Удалить'
        //         block.parentElement.querySelector('.button').style.backgroundColor = 'Red'
        //         block.parentElement.querySelector('.delete').style.display = 'none'
        //         let input = document.createElement('input')
        //         input.type = 'hidden'
        //         input.name = 'delete_file'
        //         input.value = 'ok'
        //         block.parentElement.querySelector('.file_inform').appendChild(input)
        //     }
        // }
        
        // // чекбокс "удалить ответ"
        // if (event.target.className === 'checkbox' && event.target.checked) {
            //     let del_element = (event.target.parentElement).parentElement
            //     if (del_element.querySelector('.point')) {
                //         del_element.querySelector('.point').style.filter = 'blur(3px)'
                //         del_element.querySelector('.file').style.filter = 'blur(3px)'
                //         del_element.querySelector('.cross').style.filter = 'blur(3px)'
                //         del_element.querySelector('.id_file').style.filter = 'blur(3px)'
                //     }
                //     del_element.parentElement.querySelector('textarea').style.filter = 'blur(3px)'
                //     del_element.parentElement.querySelector('.button').innerHTML = 'Удалить'
                //     del_element.parentElement.querySelector('.button').style.backgroundColor = 'red'
                
                // }
                // else if (event.target.className === 'checkbox' && !event.target.checked) {
                    //     let del_element = (event.target.parentElement).parentElement
                    //     del_element.parentElement.querySelector('textarea').style.filter = 'blur(0px)'
                    //     if (del_element.querySelector('.point')) {
                        //         del_element.querySelector('.point').style.filter = 'blur(0px)'
                        //         del_element.querySelector('.file').style.filter = 'blur(0px)'
                        //         del_element.querySelector('.cross').style.filter = 'blur(0px)'
                        //         del_element.querySelector('.id_file').style.filter = 'blur(0px)'
                        //     }
                        //     del_element.parentElement.querySelector('.button').innerHTML = 'Сохранить'
                        //     del_element.parentElement.querySelector('.button').style.backgroundColor = '#083E2F'
                        // }
                    })
                    
                    // отбражение кнопки при редактировании в зависимости от наличия файла
                    document.querySelectorAll('.id_file').forEach((e) => {
                        e.onchange = () => {
                            if (e.files[0] !== undefined &&  e.parentElement.delete_file) {
                                e.parentElement.querySelector('.button').innerHTML = 'Сохранить'
                e.parentElement.querySelector('.button').style.backgroundColor = '#083E2F'
                e.parentElement.delete_file.remove()
            }
        }
    })

    // запись скролла при отправке формы
    document.addEventListener('submit', () => {
        window.localStorage.setItem('scroll_place', window.scrollY)
    })

    function menu(option, id_answer) {
        if (option === 'edit_text') {
            document.getElementById(id_answer).style.display = 'none'
            let content = document.getElementById(id_answer).parentElement.parentElement.querySelector('.content')
            let new_content = document.getElementById(id_answer).parentElement.parentElement.querySelector('.new_content')
            const old_text = content.querySelector('.answer_text')
            old_text.style.display = 'none'
            new_content.innerHTML = 
            `<textarea name="answer" id="" cols="40" rows="10" class="edit_answer" placeholder="Ваш ответ">${old_text.innerHTML}</textarea>
            <div>
                <button class="button-cancel" value="cancel">Отмена</button>
                <button class="button" value="save">Сохранить</button>
                </div>`
                
            }
            
            if (option === 'delete_answer') {
                document.getElementById('label_for_popup').innerHTML = 'Удалить ответ?'
                popup_form(option, id_answer)
            }
            
            if (option === 'delete_file') {
                document.getElementById('label_for_popup').innerHTML = 'Удалить файл?'
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
            let popup = document.querySelector('.popup')
            popupBg.classList.remove('active')
            popup.classList.remove('active')
    }
})