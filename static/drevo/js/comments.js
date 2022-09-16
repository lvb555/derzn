$(document).ready(init)

function init() {
    getComments(null);
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

    document.getElementById(currentCounterId).innerText = textarea.value.length;
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

function getComments(loadMoreCommentsButton) {
    const commentsListBlock = document.getElementById('comments-list-block');
    const commentsListSpinner = document.getElementById('commentsListSpinner');
    if (!loadMoreCommentsButton) {
        loadMoreCommentsButton = document.getElementById('loadMoreCommentsButton');
    }

    commentsListSpinner.style.display = 'inherit';
    if (loadMoreCommentsButton) {
        loadMoreCommentsButton.disabled = true;
    }

    const url = document.location.pathname + '/comments/';

    let data = {};

    let cards = document.getElementsByClassName('comment-card');
    if (cards.length > 0) {
        data['last_comment_id'] = cards[cards.length - 1].id;
        data['parent_comment_id'] = cards[cards.length - 1].id;
    }

    $.ajax({
        data: data,
        url: url,
        success: function (response) {
            const isLastPage = response.is_last_page;

            commentsListSpinner.style.display = 'none';

            commentsListBlock.insertAdjacentHTML('beforeend', response.data);

            if (!loadMoreCommentsButton) {
                loadMoreCommentsButton = document.getElementById('loadMoreCommentsButton');
            }

            if (isLastPage) {
                loadMoreCommentsButton.style.display = 'none';
                loadMoreCommentsButton.disabled = true;
            } else {
                loadMoreCommentsButton.style.display = 'block';
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
            $('#no-comments-text').hide();

            let answersBlock = document.getElementById('answersBlock' + object.parent);

            let newCommentId = '';
            if (response.new_comment_id) {
                newCommentId = response.new_comment_id;
            }

            if (object.parent) {
                if (response.is_first_answer) {
                    answersBlock.insertAdjacentHTML('afterbegin', response.data);
                    let collapsedBlock = document.getElementById('collapsedAnswers' + object.parent);
                    collapsedBlock.classList.add('show');
                } else {
                    let collapsedBlock = document.getElementById('collapsedAnswers' + object.parent);
                    collapsedBlock.querySelector('.col').insertAdjacentHTML('afterbegin', response.data);
                    collapsedBlock.classList.add('show');
                }
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

function showMoreAnswersClick(button) {
    const collapsedAnswersBasicId = 'collapsedAnswers';
    const buttonBasicId = 'showMoreAnswersButton';
    const id = button.id.replace(buttonBasicId, '');
    let offset = parseInt(button.getAttribute('data-offset'));
    const answers = document.querySelector('#' + collapsedAnswersBasicId + id)
        .lastElementChild.querySelectorAll('.comment-answer');

    let hasHiddenAnswers = false;
    for (let answer of answers) {
        if (!answer.classList.contains('row')) {
            if (offset === 0) {
                if (answer.hidden) {
                    hasHiddenAnswers = true;
                    break;
                }
            }
            if (answer.hidden) {
                answer.hidden = false;
                offset -= 1;
            }
        }
    }
    if (!hasHiddenAnswers) {
        button.style.display = 'none';
    }
}
