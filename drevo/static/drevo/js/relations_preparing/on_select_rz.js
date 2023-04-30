const rel_kn_select = document.getElementById('related_knowledge');

rel_kn_select.addEventListener('change', () => {

const status_select = document.getElementById('relation_status')

const show_knowledge = document.getElementById('show_knowledge')
const update_knowledge = document.getElementById('update_knowledge')

  const selectedValue = rel_kn_select.value;

  show_knowledge.setAttribute('href', `/drevo/znanie/${selectedValue}`)

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

  const default_relation_status = document.getElementById('default_relation_status');
  if (data.is_pub === true) {
    status_select.disabled = false
    default_relation_status.disabled = true
  } else {
    status_select.disabled = true
    default_relation_status.disabled = false
  }
    });

});