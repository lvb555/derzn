// Разрешается редактирование/удаление выбранного option
function allow_actions(zn_edit, zn_delete) {
    zn_edit.css('cursor', 'pointer').attr("class", "text-primary");
    zn_delete.css('cursor', 'pointer').attr("class", "text-danger");
}

// Запрещается редактирование/удаление выбранного option
function disable_actions(zn_edit, zn_delete) {
    zn_edit.css('cursor', 'default').attr("class", "text-secondary");
    zn_delete.css('cursor', 'default').attr("class", "text-secondary");
}

