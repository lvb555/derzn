$(function(){
  $("#id_bz").select2().on('change.select2', function(e){
    // Получаем выбранное значение из списка базовых знаний
	var selectedValue = $(this).val();

    // Отправляем запрос на сервер с выбранным значением
    fetch(`/drevo/get_required_tr?bz_id=${selectedValue}`)
    .then(response => response.json())
    .then(data => {
        const rz_list = document.getElementById('id_rz');
        if (rz_list.disabled === false){
            rz_list.disabled = true;
            rz_list.value = null;
        };
        if (Object.entries(data).length != 0){
            // Получаем ссылку на выпадающий список видов связей
            const tr_list = document.getElementById('id_tr');
            tr_list.disabled = false;

            // Очищаем содержимое списока видов связей
            tr_list.innerHTML = '';

            // Добавляем новые элементы в список видов связей
            const null_option = document.createElement('option');
            null_option.text = '-----';
            tr_list.appendChild(null_option);
            data.required_tr.forEach(item => {
               const option = document.createElement('option');
               option.value = item.id;
               option.text = item.name;
               tr_list.appendChild(option);
            });
        };
    });
  });;
});