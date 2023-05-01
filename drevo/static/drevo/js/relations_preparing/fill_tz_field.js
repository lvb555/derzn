function fill_tz_field() {
  // Получаем ссылку на выпадающий список видов связей
  const tz_list = document.getElementById('id_tz');
  // Получаем id базового знания
  const bz_id = document.querySelector('script[data-bz-id]').getAttribute('data-bz-id');
  const tr_id = document.querySelector('script[data-tr-id]').getAttribute('data-tr-id');
  const selected_tz = document.querySelector('script[data-selected-tz]').getAttribute('data-selected-tz');
  console.log(selected_tz)
  // Заполнение списка видов знания для формы создания дополнительного знания
  fetch(`/drevo/relations/preparing/related_tz?bz_id=${bz_id}&tr_id=${tr_id}`)
  .then(response => response.json())
  .then(data => {
        if (Object.entries(data).length != 0){
            tz_list.innerHTML = '';

            const null_option = document.createElement('option');
            null_option.text = '-----';
            tz_list.appendChild(null_option);

            // Добавляем новые элементы в список связанных знаний
            data.related_tz.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                if (item.id == selected_tz){
                    option.selected = true;
                }
                option.text = item.name;
                tz_list.appendChild(option);
            });
        };
   });
}