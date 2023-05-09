$(function(){
  $("#related_knowledge").select2().on('change.select2', function(e){
    // Получаем выбранное значение из списка базовых знаний
	var selectedValue = $(this).val();

    // Отправляем запрос на сервер с выбранным значением
    fetch(`/drevo/get_required_tr?bz_id=${selectedValue}`)
    .then(response => response.json())
    .then(data => {

        const show_knowledge = document.getElementById('show_knowledge')
        const update_knowledge = document.getElementById('update_knowledge')

        show_knowledge.setAttribute('href', `/drevo/znanie/${selectedValue}`)
        show_knowledge.style.pointerEvents = 'auto'

        fetch(`/drevo/relations/preparing/check_related?rz_id=${selectedValue}`)
            .then(response => response.json())
            .then(data => {
                if (data.user_knowledge === true) {
                    update_knowledge.style.pointerEvents = 'auto'
                    const selected_tr = document.getElementById('relation_type').value;
                    const bz_id = document.querySelector('script[data-bz-id]').getAttribute('data-bz-id');
                    update_knowledge.setAttribute('href', `/drevo/relation/preparing/additional_knowledge/update/${selectedValue}?bz_id=${bz_id}&tr_id=${selected_tr}`);

                } else {
                    update_knowledge.style.pointerEvents = 'none'
                    update_knowledge.removeAttribute('href')
                }
        });
    });
  });;
});