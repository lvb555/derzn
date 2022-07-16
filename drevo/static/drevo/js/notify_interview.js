$(document).ready(function ($) {
    let url = $(location).attr('href')
    let baseKnowledgeName
    let sendNotify = false
    if (url.indexOf('change') !== -1) {
        $('.default').click(function () {
            let relationType = $('[name=tr] :selected').text()
            if (relationType === 'Состав' || relationType === 'Период интервью') {
                sendNotify = confirm("Отправить уведомление экспертам?")
            }
            if (sendNotify) {
                baseKnowledgeName = $('#select2-id_bz-container').text()
                sendNotifyRequest(baseKnowledgeName)
            }
        })
    } else {
        $('.default').click(function () {
            let relationType = $('[name=tr] :selected').text()
            if (relationType === 'Состав') {
                sendNotify = confirm("Отправить уведомление экспертам?")
            }
            if (sendNotify) {
                alert('Подтвердили отправку уведомления о новом вопросе')
                baseKnowledgeName = $('#select2-id_bz-container').text()
                sendNotifyRequest(baseKnowledgeName)
            }
        })
    }

    function sendNotifyRequest(name) {
        $.ajax({
            url: "/drevo/notify_interview/" + name + "/",
            success: function (data) {
                if (data.result === true) {
                    alert('Уведомления успешно отправлены')
                } else {
                    alert('Ошибка отправки уведомлений')
                }
            }
        })
    }
})