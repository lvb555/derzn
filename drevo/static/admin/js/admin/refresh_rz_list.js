// Получаем ссылку на выпадающий список видов связей
const tr_list = document.getElementById('id_tr');

// Добавляем обработчик события на изменение значения в списке видов связей
tr_list.addEventListener('change', () => {
  // Получаем выбранное значение из списка видов связей
  const selectedValue = tr_list.value;
  // Получаем id уже выбранного базового знания
  const bz_id = document.getElementById('id_bz').value;
  // Отправляем запрос на сервер с выбранным значением
  fetch(`/drevo/get_required_rz?tr_id=${selectedValue}&bz_id=${bz_id}`)
    .then(response => response.json())
    .then(data => {
        if (Object.entries(data).length != 0){
            // Получаем ссылку на выпадающий список связанных знаний
            const rz_list = document.getElementById('id_rz');
            rz_list.disabled = false;
            // Очищаем содержимое списока связанных знаний
            rz_list.innerHTML = '';

            // Добавляем новые элементы в список связанных знаний
            const null_option = document.createElement('option');
            null_option.text = '-----';
            rz_list.appendChild(null_option);
            data.required_rz.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.text = item.name;
                rz_list.appendChild(option);
            });
        };
    });
});