$(document).ready(init)

function init() {
    const likeButton = document.getElementById('likeButton');
    const dislikeButton = document.getElementById('dislikeButton');
    const likeIcon = document.getElementById('likeIcon');
    const dislikeIcon = document.getElementById('dislikeIcon');

    const likesCounter = document.getElementById('likesCounter');
    const dislikesCounter = document.getElementById('dislikesCounter');

    const likeIconClass = 'bi-hand-thumbs-up';
    const pressedLikeIconClass = 'bi-hand-thumbs-up-fill';
    const dislikeIconClass = 'bi-hand-thumbs-down';
    const pressedDislikeIconClass = 'bi-hand-thumbs-down-fill';

    let likeButtonState = false;
    let dislikeButtonState = false;

    if (likeIcon.classList.contains(pressedLikeIconClass)) {
        likeButtonState = true;
    }
    if (dislikeIcon.classList.contains(pressedDislikeIconClass)) {
        dislikeButtonState = true;
    }

    likeButton.addEventListener('click', likeClickHandler);
    dislikeButton.addEventListener('click', dislikeClickHandler);

    function likeClickHandler(event) {
        let target = event.currentTarget;
        let url = document.location.pathname + '/vote/like';

        $.ajax({
            url: url,
            success: function (response) {
                successFunc(target);
            },
            error: function (response) {

            }
        });
    }

    function dislikeClickHandler(event) {
        let target = event.currentTarget;
        let url = document.location.pathname + '/vote/dislike';

        $.ajax({
            url: url,
            success: function (response) {
                successFunc(target);
            },
            error: function (response) {

            }
        });
    }

    function successFunc(target) {
        let likesCount = parseInt(likesCounter.innerText);
        let dislikesCount = parseInt(dislikesCounter.innerText);

        if (target === likeButton) {
            toggleLikeIcon();

            if (likeButtonState === false) {
                likeButtonState = true;
                likesCounter.innerText = likesCount + 1;

                if (dislikeButtonState === true) {
                    toggleDislikeIcon();
                    dislikeButtonState = false;
                    dislikesCounter.innerText = dislikesCount - 1;
                }
            } else {
                likeButtonState = false;
                likesCounter.innerText = likesCount - 1;
            }
        } else {
            toggleDislikeIcon();

            if (dislikeButtonState === false) {
                dislikeButtonState = true;
                dislikesCounter.innerText = dislikesCount + 1;

                if (likeButtonState === true) {
                    toggleLikeIcon();
                    likeButtonState = false;
                    likesCounter.innerText = likesCount - 1;
                }
            } else {
                dislikeButtonState = false;
                dislikesCounter.innerText = dislikesCount - 1
            }
        }
    }

    function toggleLikeIcon() {
        likeIcon.classList.toggle(likeIconClass)
        likeIcon.classList.toggle(pressedLikeIconClass)
    }

    function toggleDislikeIcon() {
        dislikeIcon.classList.toggle(dislikeIconClass)
        dislikeIcon.classList.toggle(pressedDislikeIconClass)
    }
}