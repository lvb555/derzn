$(document).ready(function ($) {
    let url = $(location).attr('href')
    if (url.indexOf('change') !== -1) {
        $('.default').click(function () {
            let relationType = $('[name=tr] :selected').text()
            if (relationType == 'Состав' || relationType == 'Период интервью') {
                let sendNotify = confirm("Отправить уведомление экспертам?")
            }
            alert(relationType)
        })
    } else {
        $('.default').click(function () {
            let relationType = $('[name=tr] :selected').text()
            if (relationType == 'Состав') {
                let sendNotify = confirm("Отправить уведомление экспертам?")
            }
            alert(relationType)
        })
    }
})