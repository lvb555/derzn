$(document).ready(function ($) {
    let url = $(location).attr('href')
    let sendNotify = false
    if (url.indexOf('change') !== -1) {
        $('.default').click(function () {
            let relationType = $('[name=tr] :selected').text()
            if (relationType === 'Состав' || relationType === 'Период интервью') {
                sendNotify = confirm("Отправить уведомление экспертам?")
            }
            if (sendNotify) {
                $('#id_send_flag')[0].checked = true
            }
        })
    } else {
        $('.default').click(function () {
            let relationType = $('[name=tr] :selected').text()
            if (relationType === 'Состав') {
                sendNotify = confirm("Отправить уведомление экспертам?")
            }
            if (sendNotify) {
                $('#id_send_flag')[0].checked = true
            }
        })
    }

})