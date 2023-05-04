function isValueInList(value, list) {
  return list.some(item => item.id == value);
}

// Получаем ссылку на выпадающий список видов связей
const tr_list = document.getElementById('relation_type');
const add_knowledge = document.getElementById('add_knowledge');
// Добавляем обработчик события на изменение значения в списке видов связей
tr_list.addEventListener('change', () => {
  // Получаем выбранное значение из списка видов связей
  const selectedValue = tr_list.value;
  // Получаем id уже выбранного базового знания
  const bz_id = document.querySelector('script[data-bz-id]').getAttribute('data-bz-id');
  // Отправляем запрос на сервер с выбранным значением
  fetch(`/drevo/get_required_rz?tr_id=${selectedValue}&bz_id=${bz_id}`)
    .then(response => response.json())
    .then(data => {
        if (Object.entries(data).length != 0){
            // Получаем ссылку на выпадающий список связанных знаний
            const rz_list = document.getElementById('related_knowledge');
            const selected_rz = rz_list.value;

            const selectedOption = rz_list.options[rz_list.selectedIndex];
            const selected_rz_name = selectedOption.text;


            // Очищаем содержимое списока связанных знаний
            rz_list.innerHTML = '';

            rz_list.disabled = false;
            add_knowledge.style.pointerEvents = 'auto'
            const null_option = document.createElement('option');
            null_option.text = '-----';
            null_option.value = '';
            rz_list.appendChild(null_option);

            if (selected_rz){
                if (isValueInList(selected_rz, data.required_rz)) {
                    console.log('Значение найдено в списке');
                    rz_list.disabled = false;
                    tr_label = document.getElementById('tr_error');
                    if (tr_label) {
                        tr_label.remove();
                    }
                } else {
                    console.log('Значение не найдено в списке');
                    const option = document.createElement('option');
                    option.value = selected_rz;
                    option.text = selected_rz_name;
                    option.selected = true;
                    rz_list.appendChild(option);

                    tr_label = document.getElementById('relation_type_label');
                    const caption = document.createElement('span');
                    caption.textContent = 'Данный вид связи не поддерживает выбранное вами знание';
                    caption.className = 'text-danger ms-3';
                    caption.id = 'tr_error';
                    tr_label.appendChild(caption);
                    rz_list.disabled = true;

                }
            }

            // Добавляем новые элементы в список связанных знаний
            data.required_rz.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.text = item.name;
                if (selected_rz == item.id){
                    option.selected = true;
                }
                rz_list.appendChild(option);
            });
        };
    });

  fetch(`/drevo/relations/preparing/related_tz?bz_id=${bz_id}&tr_id=${selectedValue}`)
  .then(response => response.json())
  .then(data => {
        if (Object.entries(data).length != 0){
            const tz_list = document.querySelector('#addition_create').querySelector('#id_tz');
            tz_list.innerHTML = '';

            const null_option = document.createElement('option');
            null_option.text = '-----';
            null_option.value = '';
            tz_list.appendChild(null_option);

            // Добавляем новые элементы в список связанных знаний
            data.related_tz.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.text = item.name;
                tz_list.appendChild(option);
            });
        };
   });
});