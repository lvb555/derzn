// Получаем ссылку на выпадающий список базовых знаний
const bz_list = document.getElementById('id_bz');

// Добавляем обработчик события на изменение значения в списке базовых знаний
bz_list.addEventListener('change', () => {
  // Получаем выбранное значение из списка базовых знаний
  const selectedValue = bz_list.value;

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
        }else{
            const tr_list = document.getElementById('id_tr');
            if (tr_list.disabled === false){
                tr_list.disabled = true;
                tr_list.value = null;
            };
        };
    });
});