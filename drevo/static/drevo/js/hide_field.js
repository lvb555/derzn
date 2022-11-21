$(document).ready(function () {
    readonly_status = $('#id_name').attr('readonly')
    if (readonly_status === 'readonly') {
        save_button = $('input[type=submit]')
        save_button.attr('type', 'hidden')
        $('#id_photos-1-photo').attr('type', 'hidden')
        $('label[for=id_photos-1-photo]').hide()
    }
})

