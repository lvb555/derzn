const searchInput = document.getElementById('search-input');
const allUsersCheckbox = document.getElementById('all-users-checkbox');

function filterUsers() {
    const searchString = searchInput.value.toLowerCase();
    const employeeCheckboxes = document.querySelectorAll('.employee-checkbox');
    const adminCheckboxes = document.querySelectorAll('.admin-checkbox');

    employeeCheckboxes.forEach(function(checkbox) {
        const userName = checkbox.closest('tr').querySelector('td:first-child').textContent.toLowerCase();
        const isVisible = allUsersCheckbox.checked || checkbox.checked; // Update this line
        checkbox.closest('tr').style.display = userName.includes(searchString) && isVisible ? 'table-row' : 'none';
    });
}

searchInput.addEventListener('input', filterUsers);
allUsersCheckbox.addEventListener('change', filterUsers);






function updateRoles(userId, isEmployee, isAdmin) {
    const formData = new FormData();
    formData.append('userId', userId);
    formData.append('isEmployee', isEmployee);
    formData.append('isAdmin', isAdmin);

    fetch('/drevo/editorial_staff/update_roles/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('AJAX запрос успешно выполнен:', data);
    })
    .catch(error => {
        console.error('Ошибка AJAX запроса:', error);
    });
}

// Функция для получения значения куки по имени; необходима для CSRF-токена в Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function(){
    $(".employee-checkbox").change(function() {
        var userId = $(this).data("userid");
        var isChecked = $(this).prop("checked");
        var adminCheckbox = $(".admin-checkbox[data-userid='" + userId + "']");

        if (!isChecked) {
            adminCheckbox.prop("checked", false);
            adminCheckbox.prop("disabled", true);
        } else {
            adminCheckbox.prop("disabled", false);
        }

        updateRoles(userId, isChecked, adminCheckbox.prop("checked"));
    });

    $(".admin-checkbox").change(function() {
        var userId = $(this).data("userid");
        var isChecked = $(this).prop("checked");
        var employeeCheckbox = $(".employee-checkbox[data-userid='" + userId + "']");

        updateRoles(userId, employeeCheckbox.prop("checked"), isChecked);
    });
});



$(document).ready(function() {
    $('#search-button').click(function() {
        var searchText = $('#search-input').val().toLowerCase();

        $('.table tbody tr').each(function() {
            var fullName = $(this).find('td:first').text().toLowerCase();

            if (fullName.includes(searchText)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
});




document.addEventListener('DOMContentLoaded', function() {
    var showButtons = document.querySelectorAll('.show-info');
    var popups = document.querySelectorAll('.popup');
    var overlay = document.querySelector('.popup-overlay');
    var closeButtons = document.querySelectorAll('.close-popup');

    showButtons.forEach(function(button, index) {
        button.addEventListener('click', function() {
            popups.forEach(function(popup) {
                popup.style.top = '-100%';
            });
            popups[index].style.top = '50%';
            overlay.style.display = 'block';
        });
    });

    closeButtons.forEach(function(closeButton) {
        closeButton.addEventListener('click', function() {
            popups.forEach(function(popup) {
                popup.style.top = '-100%';
            });
            overlay.style.display = 'none';
        });
    });

    overlay.addEventListener('click', function() {
        popups.forEach(function(popup) {
            popup.style.top = '-100%';
        });
        overlay.style.display = 'none';
    });
});