// Получаем форму и select элемент
const form = document.getElementById('addition_create');
const rz_list = document.getElementById('related_knowledge');

//// Обработчик отправки формы
form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
    const response = await fetch('/drevo/relation/preparing/additional_knowledge/create', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();

    const option = document.createElement('option');
    option.value = data.value;
    option.textContent = data.name;
    option.selected = true;
    rz_list.appendChild(option);

    const show_knowledge = document.getElementById('show_knowledge')
    const update_knowledge = document.getElementById('update_knowledge')

    show_knowledge.setAttribute('href', `/drevo/znanie/${data.value}`)
    update_knowledge.style.pointerEvents = 'auto'
    const selected_tr = document.getElementById('relation_type').value;
    const bz_id = data.bz_pk;
    update_knowledge.setAttribute('href', `/drevo/relation/preparing/additional_knowledge/update/${data.value}?bz_id=${bz_id}&tr_id=${selected_tr}`);

    const status_select = document.getElementById('relation_status');
    const default_relation_status = document.getElementById('default_relation_status');
    status_select.disabled = false
    default_relation_status.disabled = true
});