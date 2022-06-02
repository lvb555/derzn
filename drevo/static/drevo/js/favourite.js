$(document).ready(init)

function init() {
    const favouriteButton = document.getElementById('favouriteButton');
    const favouriteIcon = document.getElementById('favouriteIcon');

    const favouriteIconClass = 'bi-star';
    const pressedFavouriteIconClass = 'bi-star-fill';

    let favouriteButtonState = false;

    if (favouriteIcon.classList.contains(pressedFavouriteIconClass)) {
        favouriteButtonState = true;
    }

    favouriteButton.addEventListener('click', favouriteClickHandler);


    function favouriteClickHandler(event) {
        let target = event.currentTarget;
        let url = document.location.pathname + '/favourite';

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
        toggleFavouriteIcon();

        if (favouriteButtonState === false) {
            favouriteButtonState = true;
        } else {
            favouriteButtonState = false;
        }
    }


    function toggleFavouriteIcon() {
        favouriteIcon.classList.toggle(favouriteIconClass)
        favouriteIcon.classList.toggle(pressedFavouriteIconClass)
    }
}