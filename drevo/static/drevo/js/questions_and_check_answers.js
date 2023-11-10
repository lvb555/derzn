if(document.querySelector('#no_questions')) {
    document.querySelector('#not_checked').parentElement.remove()
}

else {

    show_last_submited_question()
    
    show_questions_and_answers()
    
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
    
    document.addEventListener('submit', () => {
            let title_question = document.querySelector('.question_title').value
            window.localStorage.setItem('title', title_question)
            let check_button = document.getElementById('not_checked').checked
            window.localStorage.setItem('checked', check_button)
        })
}


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
    if (window.localStorage.getItem('checked') === 'true') {
        document.querySelector('#not_checked').checked = true
        show_unchecked_answers()
        window.localStorage.removeItem('checked')
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
            let counter_hidden_blocks = 0
            document.querySelectorAll('.block_answers').forEach((e) => {
                let answers = e.querySelectorAll('.answers')
                let counter_hidden_answers = 0;
                answers.forEach((answer) => {
                    if (answer.style.display === 'none') {
                        counter_hidden_answers++
                    }
                    if (counter_hidden_answers === answers.length) {
                        if (document.querySelector('.question_title')) {
                            let title = document.getElementById(`option_${e.id}`)
                            title.style.display = 'none'
                        }
                        else if (document.querySelector('.one_question')) {
                            document.querySelector('#one_question').style.display ='none'
                        }                        
                        answer.parentElement.style.display ='none' 
                        counter_hidden_blocks++
                        e.style.display = 'none'                       
                    }
                })               
            })
            if (counter_hidden_blocks === document.querySelectorAll('.block_answers').length) {
                document.querySelector('.not_checked_div').style.display = 'block'
                if (document.querySelector('.question_title'))
                {
                    document.getElementById('select_question').style.display = 'none'
                }
            }
            else if (counter_hidden_blocks === (document.querySelectorAll('.block_answers').length - 1) && document.querySelector('.question_title')) {
                let menu = document.querySelector('.question_title')
                menu.querySelectorAll('option').forEach((e) => {
                    if (e.style.display !== 'none') {
                        document.querySelector('.question_title').value = e.value
                        let event_change = new Event('change')
                        document.querySelector('.question_title').dispatchEvent(event_change)
                        document.querySelector('#select_question').style.display ='none'
                        document.querySelector('#if_one_question').innerHTML = e.innerHTML
                        document.querySelector('#if_one_question_not_checked').style.display = 'block'

                    }
                })
            }
            else {
                if (document.querySelector('.question_title')) {

                    let menu_select = document.querySelector('.question_title')
                    if (document.getElementById(menu_select.value).style.display !== 'none') {
                        document.querySelector('.question_title').value = menu_select.value
                    }
                    else {
    
                        menu_select.querySelectorAll('option').forEach((e) => {
                            if (e.style.display !== 'none') {
                                document.querySelector('.question_title').value = e.value   
                            }
                        })
                    }
                    let event_change = new Event('change')
                    document.querySelector('.question_title').dispatchEvent(event_change)
                }
            }            
        }
        else {
            document.querySelector('#if_one_question_not_checked').style.display = 'none'
            if (document.querySelector('.question_title')) {
                document.getElementById('select_question').style.display = 'block'
                document.getElementById(document.querySelector('.question_title').value).style.display = 'block'
                document.querySelector('.not_checked_div').style.display = 'none'
                document.querySelectorAll('.block_answers').forEach((e) => {
                    let answers = e.querySelectorAll('.answers')
                    answers.forEach((answer) => {
                        let title = document.getElementById(`option_${e.id}`)
                        title.style.display = 'block'
                        answer.parentElement.style.display ='block'                        
                    })                            
                })
            }
            else if (document.querySelector('.one_question')) {
                document.querySelector('.not_checked_div').style.display = 'none'
                document.getElementById('one_question').style.display = 'block'
                let block = document.querySelector('.block_answers')
                block.querySelector('form').style.display ='block'
                document.querySelector('.block_answers').style.display = 'block'                          
            }
            list_answers.forEach((answer) => {
                answer.removeAttribute('style')
                if (list_answers.length === 1) {
                    document.querySelector('.block_answers').style.display = 'block'                                
                }       
            })
        }
}

function show_questions_and_answers() {
    let selected;
    if (document.querySelector('.one_question')) {
        selected = document.querySelector('.one_question').getAttribute('name')
    }
    else {               
        selected = document.querySelector('.question_title').value
    }
    document.getElementById(selected).style.display = 'block'

    if (document.querySelector('.question_title')) {
        document.querySelector('.question_title').addEventListener('change', function() {
            document.querySelectorAll('.block_answers').forEach((block)=> {
                block.style.display = 'none'
                document.getElementById(this.value).style.display = 'block'
            })  
        })
    }
}