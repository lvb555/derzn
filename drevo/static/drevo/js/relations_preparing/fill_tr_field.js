function fill_tr_field() {
  // Получаем ссылку на выпадающий список видов связей
  const tr_list = document.getElementById('relation_type');
  // Получаем id базового знания
  const bz_id = document.querySelector('script[data-bz-id]').getAttribute('data-bz-id');
  const selected_tr = document.querySelector('script[data-selected-tr]').getAttribute('data-selected-tr');

  // Отправляем запрос на сервер с выбранным значением
  fetch(`/drevo/get_required_tr?bz_id=${bz_id}`)
    .then(response => response.json())
    .then(data => {
        if (Object.entries(data).length != 0){
            const null_option = document.createElement('option');
            null_option.text = '-----';
            null_option.value = '';
            tr_list.appendChild(null_option);

            // Добавляем новые элементы в список связанных знаний
            data.required_tr.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.text = item.name;
                if (item.id == selected_tr){
                    option.selected = true;
                }
                tr_list.appendChild(option);
            });
        };
    });


  // Заполнение списка видов знания для формы создания дополнительного знания
  fetch(`/drevo/relations/preparing/related_tz?bz_id=${bz_id}&tr_id=${selected_tr}`)
  .then(response => response.json())
  .then(data => {
        if (Object.entries(data).length != 0){
            const tz_list = document.querySelector('#addition_create').querySelector('#id_tz');
            tz_list.innerHTML = '';

            const null_option = document.createElement('option');
            null_option.text = '-----';
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
}