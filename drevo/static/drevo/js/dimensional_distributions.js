document.addEventListener("DOMContentLoaded", function() {
    window.enableQuestion2 = function() {
        var question1 = document.getElementById("question1");
        var question2 = document.getElementById("question2");
        if (question1.value != "") {
            question2.disabled = false;
        } else {
            question2.disabled = true;
        }
    }
});