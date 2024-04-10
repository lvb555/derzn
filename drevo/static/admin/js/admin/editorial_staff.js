const searchInput = document.getElementById('search-input');
const allUsersCheckbox = document.getElementById('all-users-checkbox');

function filterUsers() {
    const searchString = searchInput.value.toLowerCase();
    const employeeCheckboxes = document.querySelectorAll('.employee-checkbox');
    const adminCheckboxes = document.querySelectorAll('.admin-checkbox');

    employeeCheckboxes.forEach(function(checkbox) {
        const userName = checkbox.closest('tr').querySelector('td:first-child').textContent.toLowerCase();
        const isEmployee = checkbox.checked || checkbox.disabled; // Обновленное условие
        const isVisible = allUsersCheckbox.checked || (isEmployee && !checkbox.disabled);
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
        var isEmployee = $(this).prop("checked");
        var isAdminCheckbox = $(".admin-checkbox[data-userid='" + userId + "']");
        var isAdmin = isAdminCheckbox.prop("checked");

        if (!isEmployee) {
            isAdminCheckbox.prop("checked", false).prop("disabled", true);
            updateRoles(userId, isEmployee, false);
        } else {
            isAdminCheckbox.prop("disabled", false);
            if (isAdmin) {
                $(".employee-checkbox[data-userid='" + userId + "']").prop("checked", true);
                updateRoles(userId, true, true);
            } else {
                updateRoles(userId, true, false);
            }
        }
    });

    $(".admin-checkbox").change(function() {
        var userId = $(this).data("userid");
        var isChecked = $(this).prop("checked");
        var isEmployeeCheckbox = $(".employee-checkbox[data-userid='" + userId + "']");

        updateRoles(userId, true, isChecked);
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
        button.addEventListener('click', function(e) {
            e.stopPropagation();
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




$(document).ready(function() {
    $(document).on('change', '.group-checkbox', function() {
        var checkbox = $(this);
        var userId = checkbox.data('userid');
        var group = checkbox.val();
        var granted = checkbox.prop('checked');

        var data = {
            userId: userId,
            group: group,
            granted: granted
        };

        $.ajax({
            type: "POST",
            url: '/drevo/editorial_staff/update-group-permissions/',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                console.log('Permissions updated successfully:', response);
            },
            error: function(error) {
                console.error('Error updating permissions:', error);
            }
        });
    });

    function getCookie(name) {
        var cookieValue = null;
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = cookie.substring(name.length + 1);
                break;
            }
        }
        return cookieValue;
    }
});