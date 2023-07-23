let b = document.getElementsByClassName('cont').length;
let res = document.getElementsByClassName('Allanswers');
let allQuestionNumber = document.querySelectorAll('#number_of_question');
let legend = document.querySelector('.legend');
let sum_of_answers_in_blocks = [];
let countanswers = 0;
let users_choice = 'Choice2';
let gradeA = '<path d="M24 12C24 18.64 18.64 24 12 24C5.36 24 0 18.64 0 12C0 5.36 5.36 0 12 0C18.64 0 24 5.36 24 12Z" fill="#FFDD67"/>'+
'<path d="M18.8002 14.4C18.8002 14.08 18.6002 13.68 18.0802 13.56C16.6802 13.28 14.6402 13.04 12.0002 13.04C9.3602 13.04 7.32019 13.32 5.9202 13.56C5.4002 13.68 5.2002 14.08 5.2002 14.4C5.2002 17.32 7.4402 20.24 12.0002 20.24C16.5602 20.24 18.8002 17.32 18.8002 14.4Z" fill="#664E27"/>'+
'<path d="M10.6003 9.96C9.84028 7.92 8.72028 6.88 7.60028 6.88C6.48028 6.88 5.36028 7.92 4.60028 9.96C4.52028 10.16 4.92028 10.52 5.12028 10.32C5.84028 9.56 6.72028 9.24001 7.60028 9.24001C8.48028 9.24001 9.36028 9.56 10.0803 10.32C10.3203 10.52 10.6803 10.16 10.6003 9.96Z" fill="#664E27"/>'+
'<path d="M19.36 9.96C18.6 7.92 17.48 6.88 16.36 6.88C15.24 6.88 14.12 7.92 13.36 9.96C13.28 10.16 13.68 10.52 13.88 10.32C14.6 9.56 15.48 9.24001 16.36 9.24001C17.28 9.24001 18.12 9.56 18.84 10.32C19.04 10.52 19.44 10.16 19.36 9.96Z" fill="#664E27"/>'+
'<path d="M17.0802 14.52C16.2002 14.36 14.3602 14.12 12.0002 14.12C9.64018 14.12 7.80018 14.36 6.92018 14.52C6.40018 14.6 6.36018 14.8 6.40018 15.12C6.44018 15.28 6.44018 15.52 6.52018 15.76C6.56018 16 6.64018 16.12 7.04018 16.08C7.80018 16 16.2402 16 17.0002 16.08C17.4002 16.12 17.4402 16 17.5202 15.76C17.5602 15.52 17.6002 15.32 17.6402 15.12C17.6402 14.8 17.6002 14.6 17.0802 14.52Z" fill="white"/>'+
'<path d="M24 12C24 18.64 18.64 24 12 24C5.36 24 0 18.64 0 12C0 5.36 5.36 0 12 0C18.64 0 24 5.36 24 12Z" fill="#FFDD67"/>'+
'<path d="M18.8002 14.4C18.8002 14.08 18.6002 13.68 18.0802 13.56C16.6802 13.28 14.6402 13.04 12.0002 13.04C9.3602 13.04 7.32019 13.32 5.9202 13.56C5.4002 13.68 5.2002 14.08 5.2002 14.4C5.2002 17.32 7.4402 20.24 12.0002 20.24C16.5602 20.24 18.8002 17.32 18.8002 14.4Z" fill="#664E27"/>'+
'<path d="M10.6003 9.96C9.84028 7.92 8.72028 6.88 7.60028 6.88C6.48028 6.88 5.36028 7.92 4.60028 9.96C4.52028 10.16 4.92028 10.52 5.12028 10.32C5.84028 9.56 6.72028 9.24001 7.60028 9.24001C8.48028 9.24001 9.36028 9.56 10.0803 10.32C10.3203 10.52 10.6803 10.16 10.6003 9.96Z" fill="#664E27"/>'+
'<path d="M19.36 9.96C18.6 7.92 17.48 6.88 16.36 6.88C15.24 6.88 14.12 7.92 13.36 9.96C13.28 10.16 13.68 10.52 13.88 10.32C14.6 9.56 15.48 9.24001 16.36 9.24001C17.28 9.24001 18.12 9.56 18.84 10.32C19.04 10.52 19.44 10.16 19.36 9.96Z" fill="#664E27"/>'+
'<path d="M17.0802 14.52C16.2002 14.36 14.3602 14.12 12.0002 14.12C9.64018 14.12 7.80018 14.36 6.92018 14.52C6.40018 14.6 6.36018 14.8 6.40018 15.12C6.44018 15.28 6.44018 15.52 6.52018 15.76C6.56018 16 6.64018 16.08 7.04018 16.08H17.0002C17.4002 16.08 17.4402 16 17.5202 15.76C17.5602 15.52 17.6002 15.32 17.6402 15.12C17.6402 14.8 17.6002 14.6 17.0802 14.52Z" fill="white"/>'
let gradeB = '<path d="M12 24C18.6274 24 24 18.6274 24 12C24 5.37258 18.6274 0 12 0C5.37258 0 0 5.37258 0 12C0 18.6274 5.37258 24 12 24Z" fill="#FFDD67"/>'+
'<path d="M7.39941 11.04C8.50398 11.04 9.39941 10.1446 9.39941 9.04C9.39941 7.93543 8.50398 7.04 7.39941 7.04C6.29484 7.04 5.39941 7.93543 5.39941 9.04C5.39941 10.1446 6.29484 11.04 7.39941 11.04Z" fill="#664E27"/>'+
'<path d="M16.5996 11.04C17.7042 11.04 18.5996 10.1446 18.5996 9.04C18.5996 7.93543 17.7042 7.04 16.5996 7.04C15.495 7.04 14.5996 7.93543 14.5996 9.04C14.5996 10.1446 15.495 11.04 16.5996 11.04Z" fill="#664E27"/>'+
'<path d="M18.4398 14C16.7198 16.44 14.6398 17.04 11.9998 17.04C9.35981 17.04 7.27981 16.44 5.55981 14C5.31981 13.68 4.67981 13.88 4.83981 14.36C5.75981 17.56 8.83981 19.44 12.0398 19.44C15.2398 19.44 18.3198 17.56 19.2398 14.36C19.3198 13.88 18.6798 13.68 18.4398 14Z" fill="#664E27"/>'
let gradeC = '<path d="M12 24C18.6274 24 24 18.6274 24 12C24 5.37258 18.6274 0 12 0C5.37258 0 0 5.37258 0 12C0 18.6274 5.37258 24 12 24Z" fill="#FFDD67"/>'+
'<path d="M7.39941 12.24C8.50398 12.24 9.39941 11.3446 9.39941 10.24C9.39941 9.13544 8.50398 8.24001 7.39941 8.24001C6.29484 8.24001 5.39941 9.13544 5.39941 10.24C5.39941 11.3446 6.29484 12.24 7.39941 12.24Z" fill="#664E27"/>'+
'<path d="M16.5996 12.24C17.7042 12.24 18.5996 11.3446 18.5996 10.24C18.5996 9.13544 17.7042 8.24001 16.5996 8.24001C15.495 8.24001 14.5996 9.13544 14.5996 10.24C14.5996 11.3446 15.495 12.24 16.5996 12.24Z" fill="#664E27"/>'+
'<path d="M14.7591 18.4H9.23906C8.63906 18.4 8.63906 16.8 9.23906 16.8H14.7191C15.3591 16.8 15.3591 18.4 14.7591 18.4Z" fill="#664E27"/>'

dict_to_send = new Object();

function showFirst() {
    document.getElementsByClassName('cont')[0].style.display = "block";
    document.querySelector('#progress').textContent = 'Вопрос 1 из '+b+'';
    document.querySelector('#progress-bar').style.width = 100/b+'%';
    document.getElementsByClassName('cont')[0].querySelector('.Choice2').checked = true;
    for(let v=1; v< allQuestionNumber.length+1; v++){
        allQuestionNumber[v-1].innerHTML = 'Вопрос '+v+''
    }
    for(let f=0; f< res.length; f++){
        countanswers += +(res[f].textContent);
    }
}

showFirst();

function changeLabelColor(label) {
    label.classList.toggle("checked-label");
}

let d = 0;
let step = 1;
let result = 0;

function show_result_for_question(){
    var lst2 = Array.from(new Set(lst));
    if(lst2.length == step){
        questionblock = document.getElementById(lst2[d]+'1');
        let countans = +(questionblock.querySelector('.vopr').textContent);
        let answersinblock = questionblock.querySelectorAll('.firstblock input[type="checkbox"]');
        let warning = questionblock.querySelector('.warning');
        let resultinblock = questionblock.querySelectorAll('.resultsecondblock');
        let question_pk = questionblock.querySelector('.vopr1').textContent.split(' ');
        let different_resultinblock = questionblock.querySelector('.not_all_answers_showing');
        all_checked_answers = [];
        sum_for_next_block = 0;
          for (let i=0; i<answersinblock.length; i++) {
             if(answersinblock[i].checked == true){
                 sum_for_next_block += 1;
             }
          }
        if(sum_for_next_block == countans){
             for (let i=0; i<answersinblock.length; i++) {
                 if(answersinblock[i].checked == true){
                    all_checked_answers.push(answersinblock[i].id);
                    resultinblock[i].querySelector('.checkbox-round').setAttribute("checked", "true");
                    resultinblock[i].querySelector('.checkbox-round').checked = true;
                    if(resultinblock[i].style.background == 'var(--success, rgba(25, 135, 84, 0.20))'){
                        resultinblock[i].classList.add("right-answer")
                    }else{
                        resultinblock[i].classList.add("wrong-answer")
                    }
                    different_resultinblock.innerHTML += resultinblock[i].outerHTML;
                 }
             }
            dict_to_send[question_pk[question_pk.length-1]] = all_checked_answers
            document.getElementById('show_result_for_question').style.display = "none";
            document.getElementById('next_question').style.display = "block";
            let blockwithcolours = document.getElementsByClassName('cont')[d]
            blockwithcolours.querySelector('.firstblock').style.display = "none";
            blockwithcolours.querySelector('.'+users_choice+'').checked = true;
            if(users_choice == 'Choice2'){
                blockwithcolours.querySelector('.not_all_answers_showing').style.display = "grid";
                blockwithcolours.querySelector('.all_answers_showing').style.display = "none";
            }else{
                blockwithcolours.querySelector('.not_all_answers_showing').style.display = "none";
                blockwithcolours.querySelector('.all_answers_showing').style.display = "grid";
            }
            blockwithcolours.querySelector('.secondblock').style.display = "block";
            warning.style.display = "none";
            legend.style.display = "block";
            if(step == b){
            document.getElementById('final_block').style.display = "block";
            document.getElementById('next_question').style.display = "none";
            }
        }else if(sum_for_next_block<countans){
            missing_answer = countans - sum_for_next_block
            missing_answer = missing_answer.toString()
            if(missing_answer.endsWith('2') || missing_answer.endsWith('3') || missing_answer.endsWith('4')){
                warning.innerHTML = "<span>Необходимо отметить ещё "
                +missing_answer+" ответа</span>";
            } else if(missing_answer.endsWith('1')){
                warning.innerHTML = "<span>Необходимо отметить ещё "
                +missing_answer+" ответ</span>";
            }else {
                warning.innerHTML = "<span>Необходимо отметить ещё "
                +missing_answer+" ответов</span>";
            }
            warning.style.display = "block";
            addNewNotification(answersinblock, countans, warning)
        }
    }else if(lst2.length < step){
        let questionblock = document.querySelector('.cont[style*="display: block"]')
        let countans = +(questionblock.querySelector('.vopr').textContent);
        let warning = questionblock.querySelector('.warning');
        let answersinblock = questionblock.querySelectorAll('input[type="checkbox"]');
        warning.innerHTML = "<span>Вы не дали ни одного ответа</span>";
        warning.style.display = "block";
        addNewNotification(answersinblock, countans, warning)
    }
}

function addNewNotification(answersinblock, countans, warning){
        let enabledSettings = []
        answersinblock.forEach(function(checkbox) {
          checkbox.addEventListener('change', function() {
            enabledSettings =
              Array.from(answersinblock)
              .filter(i => i.checked)
            let missing_answer = countans - enabledSettings.length
            missing_answer = missing_answer.toString()
            if(missing_answer.endsWith('2') || missing_answer.endsWith('3') || missing_answer.endsWith('4')){
                warning.innerHTML = "<span>Необходимо отметить ещё "
                +missing_answer+" ответа</span>";
            } else if(missing_answer.endsWith('1')){
                warning.innerHTML = "<span>Необходимо отметить ещё "
                +missing_answer+" ответ</span>";
            } else if(missing_answer == '0'){
                warning.innerHTML = "<span>Теперь ответов достаточно!</span>";
            }else {
                warning.innerHTML = "<span>Необходимо отметить ещё "
                +missing_answer+" ответов</span>";
            }
          })
        });
}

function ChangeResult(value){
    let questionblock = document.querySelector('.cont[style*="display: block"]')
    if(value=='all'){
        questionblock.querySelector('.not_all_answers_showing').style.display = "none";
        questionblock.querySelector('.all_answers_showing').style.display = "grid";
        users_choice = 'Choice1';
    }else{
        questionblock.querySelector('.not_all_answers_showing').style.display = "grid";
        questionblock.querySelector('.all_answers_showing').style.display = "none";
        users_choice = 'Choice2';
    }
}

function get_previous_question(){
    var lst2 = Array.from(new Set(lst));
    previous_question = document.getElementsByClassName('cont')[d-1].querySelector('.checkboxgroup');
    current_question = document.getElementsByClassName('cont')[d].querySelector('.checkboxgroup');
    <!--Это если нажали кнопку показать результат-->
    if(Object.keys(dict_to_send).length==step){
        delete dict_to_send[Object.keys(dict_to_send)[step-1]];
        delete dict_to_send[Object.keys(dict_to_send)[step-2]];
        current_question.querySelector('.secondblock').style.display = "none";
        current_question.querySelector('.firstblock').style.display = "grid";
        let current_resultinblock = current_question.querySelectorAll('.resultsecondblock');
        getUnchecked(current_question.querySelectorAll('.firstblock label'));
        getUnchecked(current_resultinblock);
        current_question.querySelector('.not_all_answers_showing').innerHTML = '';
    <!--А это если еще не нажимали кнопку результат-->
    }else{
        delete dict_to_send[Object.keys(dict_to_send)[step-2]];
    }
    current_question.parentNode.style.display = "none";
    document.getElementById('final_block').style.display = "none";
    previous_question.parentNode.style.display = "block";
    previous_question.querySelector('.secondblock').style.display = "none";
    previous_question.querySelector('.firstblock').style.display = "grid";
    let resultinblock = previous_question.querySelectorAll('.resultsecondblock');
    getUnchecked(previous_question.querySelectorAll('.firstblock label'));
    getUnchecked(resultinblock);
    previous_question.querySelector('.not_all_answers_showing').innerHTML = '';
    lst = []
    for(let key in Object.keys(dict_to_send)){
           lst.push('0'+key);
    }
    step = step-1;
    d = d-1;
    if(d == 0){
        document.getElementById('previous_question').style.display = "none";
    }
    result -= sum_of_answers_in_blocks[sum_of_answers_in_blocks.length-1];
    sum_of_answers_in_blocks.splice(sum_of_answers_in_blocks.length-1, 1);
    document.querySelector('#progress-bar').style.width = step*100/b+'%';
    document.querySelector('#progress').textContent = 'Вопрос '+step+' из '+b+'';
    legend.style.display = "none";
    document.getElementById('show_result_for_question').style.display = "block";
    document.getElementById('next_question').style.display = "none";
}

function getUnchecked(elements){
    elements.forEach((elem) => {
      elem.querySelector('.checkbox-round').checked = false;
      elem.classList.remove("right-answer");
      elem.classList.remove("checked-label");
      elem.classList.remove("wrong-answer");
    });
}

function next_block(){
    var lst2 = Array.from(new Set(lst));
    if(lst2.length < step){
    lst.push('0'+step);
    }else if(lst2.length == step ){
        questionblock = document.getElementById(lst2[d]+'1');
        let countans = +(questionblock.querySelector('.vopr').textContent);
        let answersinblock = questionblock.querySelectorAll('.firstblock input[type="checkbox"]');
        let p = [];
          for (let i=0; i<answersinblock.length; i++) {
             if(answersinblock[i].checked == true){
                p.push(+(answersinblock[i].value));
             }
          }
        sum_of_answers = p.reduce((partialSum, a) => partialSum + a, 0);
        sum_of_answers_in_blocks.push(sum_of_answers);
        result += sum_of_answers;
        let trs = document.getElementById(lst2[d]+'2');
        makeGrade(sum_of_answers,countans,trs);
    }
    if(step < b-1){
        if(step == 1){
            document.getElementById('previous_question').style.display = "block";
        }
        document.getElementsByClassName('cont')[d].style.display = "none";
        document.getElementsByClassName('cont')[step].style.display = "block";
        document.getElementById('show_result_for_question').style.display = "block";
        document.getElementById('next_question').style.display = "none";
        document.querySelector('#progress').textContent = 'Вопрос '+(step+1)+' из '+b+'';
        document.querySelector('#progress-bar').style.width = (step+1)*100/b+'%';
        legend.style.display = "none";
        d += 1;
        step +=1;
    }else if(step==b-1){
        document.getElementsByClassName('cont')[d].style.display = "none";
        document.getElementsByClassName('cont')[step].style.display = "block";
        document.getElementById('show_result_for_question').style.display = "block";
        document.getElementById('next_question').style.display = "none";
        legend.style.display = "none";
        document.querySelector('#progress').textContent = 'Вопрос '+(step+1)+' из '+b+'';
        document.querySelector('#progress-bar').style.width = (step+1)*100/b+'%';
        d += 1;
        step +=1;
    }else if(step == b){
        document.getElementById('final_block').style.display = "none";
        document.getElementById('previous_question').style.display = "none";
        legend.style.display = "none";
        document.querySelector('#progress').parentNode.style.display = "none";
        document.getElementsByClassName('cont')[d].style.display = "none";
        document.getElementById('rezultat').style.display = 'block';
        document.getElementById('next_question').style.display = 'none';
        document.getElementById('tryagain').style.display = 'block';
        makeGrade(result,countanswers,document.getElementById('final'));
        if((~~((result*100)/countanswers)) > 90){
            document.getElementById('result2').innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">'+gradeA+
        '</svg><div><p class="mb-2 small-title" style="color: var(--secondary, #6C757D);">Оценка теста:</p><p class="title m-0" style="font-weight:bold">Отлично</p></div>';
            document.getElementById('result2').classList.add("good-answer")
        }else if(90 >= (~~((result*100)/countanswers)) && (~~((result*100)/countanswers)) > 60){
            document.getElementById('result2').innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">'+gradeB+
        '</svg><div><p class="mb-2 small-title" style="color: var(--secondary, #6C757D);">Оценка теста:</p><p class="title m-0" style="font-weight:bold">Хорошо</p></div>';
            document.getElementById('result2').classList.add("good-answer")
        }else if(60 >= (~~((result*100)/countanswers)) && (~~((result*100)/countanswers)) > 30){
            document.getElementById('result2').innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none">'+gradeC+
        '</svg><div><p class="mb-2 small-title" style="color: var(--secondary, #6C757D);">Оценка теста:</p><p class="title m-0" style="font-weight:bold">Удовлетворительно</p></div>';
            document.getElementById('result2').classList.add("acceptable-answer")
        }else{
            document.getElementById('result2').classList.add("unacceptable-answer")
        }
    }
}

var lst = []
function keyCounter(label, question){
    lst.push(question)
	let a = document.getElementsByName(question);
	let b = 0;
	let limit =  +(document.getElementById(question).textContent);
	for(let i = 0; i < a.length; i++){
		if(a[i].checked==true){
			b = b +1;
		}
	}
	if(b>limit){
	    return false
	}else{
	    changeLabelColor(label.parentNode);
	}
}

function makeGrade(sum_of_answers, countans, row){
    var lst2 = Array.from(new Set(lst));
    let td = row.querySelectorAll('td');
    if((~~((sum_of_answers*100)/countans)) > 90){
        td[1].innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'+gradeA+
        '</svg> Отлично';
        td[1].style.background = 'var(--success, rgba(25, 135, 84, 0.20))';
        row.style.color = '#198754';
    }else if(90 >= (~~((sum_of_answers*100)/countans)) && (~~((sum_of_answers*100)/countans)) > 60){
        td[1].innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'+gradeB+
        '</svg> Хорошо';
        td[1].style.background = 'var(--success, rgba(25, 135, 84, 0.20))';
        row.style.color = '#198754';
    }else if(60 >= (~~((sum_of_answers*100)/countans)) && (~~((sum_of_answers*100)/countans)) > 30){
        td[1].innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">'+gradeC+
        '</svg> Удовлетворительно';
        td[1].style.background = 'var(--warning, #FFF8DD);';
        row.style.color = '#F7961E';
    }
    td[2].innerHTML = sum_of_answers+'/'+countans;
    tabl = document.getElementById(lst2[d]+'2');
}

function onButtonSendClick(){
    next_block();

    $.ajax({
        data: { 'values' : JSON.stringify(dict_to_send) },
        url: document.location.pathname + '/quiz_result/',
        success: function (response) {
        }
    });
}