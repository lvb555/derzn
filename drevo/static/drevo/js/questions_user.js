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
        if (e.querySelector('.new_answer') && !e.querySelector('.checked_answers')) {
            e.querySelector('.new_form').style.display = 'block'
            e.querySelector('.plus').remove()
        }
    })

    
    document.addEventListener('click', () => {

        // функционал кнопки +
        if (event.target.className === 'plus') {
            let block = event.target.parentElement
            block.querySelector('.new_form').style.display = 'block'
            block.querySelector('.plus').remove()
        }
        
        // функционал кнопки х
        if (event.target.className === 'cross') {
            let block = event.target.parentElement
            if (block.parentElement.querySelector('.id_file').style.display === 'inline'){
                block.querySelector('.point').style.filter = 'blur(0px)'
                block.querySelector('.file').style.filter = 'blur(0px)'
                block.parentElement.querySelector('.id_file').style.display = 'none'
                block.parentElement.querySelector('.button').innerHTML = 'Сохранить'
                block.parentElement.querySelector('.button').style.backgroundColor = '#083E2F'
                block.parentElement.querySelector('.delete').style.display = 'inline'
                if (block.parentElement.delete_file) {
                    block.parentElement.delete_file.remove()       
                }
                block.parentElement.edit_file.value = ''
            }
            else {
                block.querySelector('.point').style.filter = 'blur(3px)'
                block.querySelector('.file').style.filter = 'blur(3px)'
                block.parentElement.querySelector('.id_file').style.display = 'inline'
                block.parentElement.querySelector('.button').innerHTML = 'Удалить'
                block.parentElement.querySelector('.button').style.backgroundColor = 'Red'
                block.parentElement.querySelector('.delete').style.display = 'none'
                let input = document.createElement('input')
                input.type = 'hidden'
                input.name = 'delete_file'
                input.value = 'ok'
                block.parentElement.querySelector('.file_inform').appendChild(input)
            }
        }

        // чекбокс "удалить ответ"
        if (event.target.className === 'checkbox' && event.target.checked) {
            let del_element = (event.target.parentElement).parentElement
            if (del_element.querySelector('.point')) {
                del_element.querySelector('.point').style.filter = 'blur(3px)'
                del_element.querySelector('.file').style.filter = 'blur(3px)'
                del_element.querySelector('.cross').style.filter = 'blur(3px)'
                del_element.querySelector('.id_file').style.filter = 'blur(3px)'
            }
            del_element.parentElement.querySelector('textarea').style.filter = 'blur(3px)'
            del_element.parentElement.querySelector('.button').innerHTML = 'Удалить'
            del_element.parentElement.querySelector('.button').style.backgroundColor = 'red'
            
        }
        else if (event.target.className === 'checkbox' && !event.target.checked) {
            let del_element = (event.target.parentElement).parentElement
            del_element.parentElement.querySelector('textarea').style.filter = 'blur(0px)'
            if (del_element.querySelector('.point')) {
                del_element.querySelector('.point').style.filter = 'blur(0px)'
                del_element.querySelector('.file').style.filter = 'blur(0px)'
                del_element.querySelector('.cross').style.filter = 'blur(0px)'
                del_element.querySelector('.id_file').style.filter = 'blur(0px)'
            }
            del_element.parentElement.querySelector('.button').innerHTML = 'Сохранить'
            del_element.parentElement.querySelector('.button').style.backgroundColor = '#083E2F'
        }
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
})