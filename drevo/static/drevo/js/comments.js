$(document).ready(init)

function init() {
    const loadMoreCommentsButton = document.getElementById('loadMoreCommentsButton');
    loadMoreCommentsButton.addEventListener('click', function (event) {
        getComments();
    })

    getComments();
}

function onInputHandler(textarea) {
    const basicTextareaId = 'commentTextareaForm';
    const basicButtonId = 'sendFormButton';
    const basicCounterId = 'commentCharCounter';

    let currentTextareaId = textarea.id;
    let currentCounterId;
    let currentButtonId;

    if (currentTextareaId === basicTextareaId) {
        currentCounterId = basicCounterId;
        currentButtonId = basicButtonId;
    } else {
        let id = currentTextareaId.replace(basicTextareaId, '');
        currentCounterId = basicCounterId + id;
        currentButtonId = basicButtonId + id;
    }

    let value = textarea.value.trim();
    document.getElementById(currentButtonId).disabled = !value;

    document.getElementById(currentCounterId).innerHTML = textarea.value.length;
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + "px";
}

function scrollToComment(commentId) {
    const comment = document.getElementById(commentId);
    comment.scrollIntoView({behavior: 'smooth', block: 'start'});
    animateCard(comment.id);
}

function animateCard(id) {
    document.getElementById(id).animate(
        [{backgroundColor: '#fff7df'}, {backgroundColor: 'inherit'}],
        {duration: 1500, iterations: 1}
    );
}

function getComments() {
    const commentsListBlock = document.getElementById('comments-list-block');
    const commentsListSpinner = document.getElementById('commentsListSpinner');
    const loadMoreCommentsButton = document.getElementById('loadMoreCommentsButton');

    commentsListSpinner.style.display = '';
    loadMoreCommentsButton.disabled = true;

    const url = document.location.pathname + '/comments/';

    let data = {};

    let cards = document.getElementsByClassName('comment-card');
    if (cards.length > 0) {
        data['last_comment_id'] = cards[cards.length - 1].id;
    }

    $.ajax({
        data: data,
        url: url,
        success: function (response) {
            const isLastPage = response.is_last_page;

            commentsListSpinner.style.display = 'none';
            commentsListBlock.insertAdjacentHTML('beforeend', response.data);

            if (!isLastPage) {
                loadMoreCommentsButton.disabled = false;
            }
        }
    });
}

function onButtonSendClick(parent_id = '') {
    const id = parent_id ? parent_id : '';
    const commentForm = $('#commentForm' + id);
    const data = commentForm.serializeArray();
    sendComment(data, commentForm);
}

function onCollapseRepyFormShow(button) {
    let replyFormId = button.attributes['aria-controls'].value;
    let isShow = document.getElementById(replyFormId).classList.contains('collapsing');
    if (isShow) {
        let forms = document.getElementsByClassName('reply-form-block show');
        for (let form of forms) {
            if (form.id !== replyFormId) {
                form.classList.remove('show');
            }
        }
    }
}

function sendComment(data, form) {
    const sendFormButton = form[0].querySelector('.send-comment-button');
    const textareaForm = form[0].querySelector('textarea');
    const buttonValue = sendFormButton.value;

    let object = {};

    for (let el of data) {
        object[el.name] = el.value;
    }
    object.content = object.content.trim();

    if (!object.content) {
        return false;
    }

    sendFormButton.disabled = true;
    textareaForm.disabled = true;

    $.ajax({
        data: object,
        url: document.location.pathname + '/comments/send/',
        success: function (response) {
            let answersBlock = document.getElementById('answersBlock' + object.parent);
            let newCommentId = '';
            if (response.new_comment_id) {
                newCommentId = response.new_comment_id;
            }

            if (object.parent) {
                answersBlock.innerHTML = response.data;

                document.getElementById('collapsedAnswers' + object.parent).classList.add('show');

                let answersCountElement = document.getElementById('answersCount' + object.parent);
                let currentAnswersCount = parseInt(answersCountElement.innerText);
                answersCountElement.innerText = currentAnswersCount + 1;
                let answersButton = document.getElementById('answersButton' + object.parent);
                answersButton.disabled = false;
            } else {
                document.getElementById('comments-list-block').insertAdjacentHTML('afterbegin', response.data);
            }
            form[0].querySelector('textarea').value = null;
            document.getElementById('commentCharCounter' + object.parent).innerText = '0';

            sendFormButton.value = buttonValue;
            textareaForm.style.height = 'auto';
            textareaForm.disabled = false;

            animateCard(newCommentId);
        }
    });
}
