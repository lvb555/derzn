function fill_rz_field() {
  // Получаем ссылку на выпадающий список связанных знаний
  const rz_list = document.getElementById('related_knowledge');
  // Получаем id базового знания
  const bz_id = document.querySelector('script[data-bz-id]').getAttribute('data-bz-id');
  const selected_rz = document.querySelector('script[data-selected-rz]').getAttribute('data-selected-rz');
  const tr_id = document.querySelector('script[data-tr-id]').getAttribute('data-tr-id');

  // Отправляем запрос на сервер с выбранным значением
  fetch(`/drevo/get_required_rz?bz_id=${bz_id}&tr_id=${tr_id}`)
    .then(response => response.json())
    .then(data => {
        if (Object.entries(data).length != 0){
            const null_option = document.createElement('option');
            null_option.text = '-----';
            null_option.value = '';
            rz_list.appendChild(null_option);

            // Добавляем новые элементы в список связанных знаний
            data.required_rz.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.text = item.name;
                if (item.id == selected_rz){
                    option.selected = true;
                }
                rz_list.appendChild(option);
            });
        };
    });


  fetch(`/drevo/relations/preparing/check_related?rz_id=${selected_rz}`)
    .then(response => response.json())
    .then(data => {
        const update_knowledge = document.getElementById('update_knowledge')
        if (data.user_knowledge === true) {
            update_knowledge.style.pointerEvents = 'auto'
            update_knowledge.setAttribute('href', `/drevo/relation/preparing/additional_knowledge/update/${selected_rz}?bz_id=${bz_id}&tr_id=${tr_id}`);
        } else {
            update_knowledge.style.pointerEvents = 'none'
            update_knowledge.removeAttribute('href')
        }
    });
}