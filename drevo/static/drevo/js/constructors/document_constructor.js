// Открытие документа
$('#open_zn').click(function () {
    let main_zn_id = $('#main_zn_id').val()
    window.open(`/drevo/znanie/${main_zn_id}`);
})