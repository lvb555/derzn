show_last_submited_question()

document.getElementById('not_checked').onclick = () => {
    if (document.querySelector('.one_question')) {
        show_unchecked_answers()
    }
    else {               
        document.querySelectorAll('.question_title').forEach(() => {
            show_unchecked_answers()
        })
    }
}

document.addEventListener('click', (e) => {
    show_refuse_reason(e)
})

let selected;
if (document.querySelector('.one_question')) {
    selected = document.querySelector('.one_question').getAttribute('name')
}
else {               
    selected = document.querySelector('.question_title').value
}
let block = document.getElementById(selected)
let form = block.querySelector(`.${selected}`)
if (form.querySelector('.answers') === null) {
    block.innerHTML = '<h4>Ответы отсутствуют</h4>'
}
document.getElementById(selected).style.display = 'block'

if (document.querySelector('.question_title')) {
    document.querySelector('.question_title').addEventListener('change', function() {
        document.querySelectorAll('.block_answers').forEach((block)=> {
            block.style.display = 'none'
            document.getElementById(this.value).style.display = 'block'
        })  
        let block = document.getElementById(this.value)
        let form = block.querySelector(`.${this.value}`)
        if (form.querySelector('.answers') === null) {
            block.innerHTML = '<h4>Ответы отсутствуют</h4>'
        }
    })
}

document.addEventListener('submit', () => {
        let title_question = document.querySelector('.question_title').value
        window.localStorage.setItem('title', title_question)
    })


function show_refuse_reason(e) {
    if (e.target.className === 'acceptance' && e.target.value === 'not_accepted') {
        document.getElementById(e.target.name).style.visibility = 'visible'  
        if (document.getElementById(`text_reason${e.target.name}`)) {
            
            document.getElementById(`text_reason${e.target.name}`).style.visibility = 'hidden'  
        }
    }
    else if (e.target.className === 'acceptance' && e.target.value !== 'not_accepted') {
        document.getElementById(e.target.name).style.visibility = 'hidden'  
        if (document.getElementById(`text_reason${e.target.name}`)) {

            document.getElementById(`text_reason${e.target.name}`).style.visibility = 'visible'
        }     
    }
}


function show_last_submited_question() {
    if (window.localStorage.getItem('title')) {
        let saved = window.localStorage.getItem('title')
        let menu_select = document.querySelectorAll('.question_value')
        menu_select.forEach((element) => {
            if (saved === element.value) {
                element.setAttribute('selected', '')
                window.localStorage.removeItem('title')
            }
        })
    }
    else {
        let menu_select = document.querySelectorAll('.question_value')
        menu_select.forEach((element) => {
                element.removeAttribute('selected')                           
        })
    }
}


function show_unchecked_answers() {
    let list_answers =  document.querySelectorAll('.answers')
        if (document.getElementById('not_checked').checked === true) {
                
            list_answers.forEach((answer) => {
                let expert = answer.querySelector('.expert')
                if (expert) {
                    answer.style.display = 'none'
                }
            })

            document.querySelectorAll('.block_answers').forEach((e) => {
                let answers = e.querySelectorAll('.answers')
                let counter = 0;
                answers.forEach((answer) => {
                    if (answer.style.display === 'none') {
                        counter++
                    }
                    if (counter === answers.length) {
                        e.querySelector('.not_checked_div').style.display = 'block'
                        answer.parentElement.style.display ='none'                        
                    }
                })

                
            })
        }
        else {
            document.querySelectorAll('.block_answers').forEach((e) => {
                let answers = e.querySelectorAll('.answers')
                answers.forEach((answer) => {
                    answer.parentElement.style.display ='block'                        
                })                            
            })
            document.querySelectorAll('.not_checked_div').forEach((e) => {
                e.style.display = 'none'
            })
            list_answers.forEach((answer) => {
                let expert = answer.querySelector('.expert')
                answer.removeAttribute('style')
                if (list_answers.length === 1) {
                    document.querySelector('.block_answers').style.display = 'block'                                
                }       
            })
        }
}