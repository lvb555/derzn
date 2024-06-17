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

document.addEventListener('DOMContentLoaded', (event) => {
    function checkAndDeleteCookie() {
        console.log('Checking path before unloading...');
        var currentPath = window.location.pathname;
        var distributionPages = ['/dimensional_distributions_1/', '/dimensional_distributions_2/'];
    
        if (!distributionPages.includes(currentPath)) {
            console.log('Deleting selected_interview cookie...');
            document.cookie = "selected_interview=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        }
    }
    window.addEventListener('beforeunload', checkAndDeleteCookie);
});