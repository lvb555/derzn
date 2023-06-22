function toggleHiddenElement(element) {
    element.parentNode.querySelector('.small-title').hidden = !element.parentNode.querySelector('.small-title').hidden;

    if (element.classList.contains("bi-play-circle-open")) {
        element.classList.remove("bi-play-circle-open")
        element.classList.add("bi-play-circle-close");
        element.parentNode.style.background = 'white';
    } else {
        element.classList.remove("bi-play-circle-close")
        element.classList.add("bi-play-circle-open");
        element.parentNode.style.background = 'rgba(245, 245, 245, 0.75)';
    }
}