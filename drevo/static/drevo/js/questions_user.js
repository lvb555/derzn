document.addEventListener('DOMContentLoaded', () => {

    if (document.querySelector('.edit')) {
        console.log(document.querySelectorAll('.edit'))
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

    const block_of_ans = document.querySelectorAll('.block')
    block_of_ans.forEach((e) => {
        if (e.querySelector('.new_answer') && !e.querySelector('.checked_answers')) {
            e.querySelector('.new_form').style.display = 'block'
            e.querySelector('.plus').remove()
        }
    })

    document.addEventListener('click', () => {
        if (event.target.className === 'plus') {
            let block = event.target.parentElement
            block.querySelector('.new_form').style.display = 'block'
            block.querySelector('.plus').remove()
        }
        
        if (event.target.className === 'cross') {
            let block = event.target.parentElement
            block.style.display = 'none'
            block.parentElement.querySelector('.id_file').style.display = 'block'
        }

        if (event.target.className === 'checkbox' && event.target.checked) {
            let del_element = (event.target.parentElement).parentElement
            console.log(del_element)
            del_element.parentElement.querySelector('textarea').style.filter = 'blur(3px)'
            del_element.querySelector('.point').style.filter = 'blur(3px)'
            del_element.querySelector('.file').style.filter = 'blur(3px)'
            del_element.querySelector('.cross').style.filter = 'blur(3px)'
            del_element.parentElement.querySelector('.button').innerHTML = 'Удалить'
            del_element.parentElement.querySelector('.button').style.backgroundColor = 'red'
            
        }
        else if (event.target.className === 'checkbox' && !event.target.checked) {
            let del_element = (event.target.parentElement).parentElement
            del_element.parentElement.querySelector('textarea').style.filter = 'blur(0px)'
            del_element.querySelector('.point').style.filter = 'blur(0px)'
            del_element.querySelector('.file').style.filter = 'blur(0px)'
            del_element.querySelector('.cross').style.filter = 'blur(0px)'
            del_element.parentElement.querySelector('.button').innerHTML = 'Сохранить'
            del_element.parentElement.querySelector('.button').style.backgroundColor = '#083E2F'
        }
    })
})