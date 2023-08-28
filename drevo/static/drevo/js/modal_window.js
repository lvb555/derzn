function ovarlayClose(className) {
    $(document).on('click', className, function () {
        $('.overlay').fadeOut();
    });
}

const inputs = document.querySelectorAll('input');
inputs.forEach(function(input) {
    if (input.classList.contains('js-cancel-successful')) {
        ovarlayClose('.js-cancel-successful');
    }
    if (input.classList.contains('js-close-successful')) {
        ovarlayClose('.js-close-successful');
    }
});
$(document).mouseup(function (e) {
    var popup = $('.popup');
    if (e.target !== popup[0] && popup.has(e.target).length === 0) {
        $('.overlay').fadeOut();
    }
})
