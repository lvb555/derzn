function fill_rz_field() {
  const rz_list = document.getElementById('related_knowledge');
  if (!rz_list) return;

  const bz_id = document.querySelector('script[data-bz-id]')?.getAttribute('data-bz-id');
  const selected_rz = document.querySelector('script[data-selected-rz]')?.getAttribute('data-selected-rz');
  const tr_id = document.querySelector('script[data-tr-id]')?.getAttribute('data-tr-id');

  if (!bz_id || !tr_id) return;

  // Запрос для заполнения списка связанных знаний
  fetch(`/drevo/get_required_rz?bz_id=${bz_id}&tr_id=${tr_id}`)
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(data => {
      rz_list.innerHTML = ''; // Очищаем список перед заполнением

      if (data && data.required_rz && data.required_rz.length > 0) {
        const null_option = document.createElement('option');
        null_option.text = '-----';
        null_option.value = '';
        rz_list.appendChild(null_option);

        data.required_rz.forEach(item => {
          const option = document.createElement('option');
          option.value = item.id;
          option.text = item.name;
          if (item.id == selected_rz) {
            option.selected = true;
          }
          rz_list.appendChild(option);
        });
        const insertBtn = document.getElementById('insert_knowledge');
        if (insertBtn && data.required_rz.length > 0) {
            insertBtn.style.pointerEvents = 'auto';
            insertBtn.classList.remove('disabled');
            insertBtn.onclick = function(e) {
                e.preventDefault();
                const selectedRzId = rz_list.value;
                if (selectedRzId) {
                    window.location.href = `/drevo/relation/preparing/additional_knowledge/insert/${selectedRzId}?bz_id=${bz_id}&tr_id=${tr_id}`;
                }
            };
        }
      }
    })
    .catch(error => {
      console.error('Error fetching required rz:', error);
    });

  if (selected_rz) {
    // Проверка прав на обновление знания
    fetch(`/drevo/relations/preparing/check_related?rz_id=${selected_rz}`)
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => {
        const update_knowledge = document.getElementById('update_knowledge');
        if (update_knowledge) {
          if (data.user_knowledge === true) {
            update_knowledge.style.pointerEvents = 'auto';
            update_knowledge.setAttribute('href', `/drevo/relation/preparing/additional_knowledge/update/${selected_rz}?bz_id=${bz_id}&tr_id=${tr_id}`);
          } else {
            update_knowledge.style.pointerEvents = 'none';
            update_knowledge.removeAttribute('href');
          }
        }
      })
      .catch(error => {
        console.error('Error checking related knowledge:', error);
      });
  }
}

function setupDeleteHandler() {
  const deleteBtn = document.getElementById('delete_knowledge');
  if (!deleteBtn) return;

  deleteBtn.addEventListener('click', function(e) {
    e.preventDefault();

    const rz_id = document.getElementById('related_knowledge')?.value;
    const bz_id = document.querySelector('script[data-bz-id]')?.getAttribute('data-bz-id');
    const tr_id = document.querySelector('script[data-tr-id]')?.getAttribute('data-tr-id');

    if (!rz_id || !bz_id || !tr_id) {
      alert('Недостаточно данных для удаления');
      return;
    }

    if (confirm('Вы уверены, что хотите удалить это знание?')) {
      fetch(`/drevo/delete_knowledge?rz_id=${rz_id}&bz_id=${bz_id}&tr_id=${tr_id}`, {
        method: 'DELETE',
      })
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => {
        if (data.success) {
          window.location.reload();
        } else {
          alert(data.error || 'Ошибка при удалении знания');
        }
      })
      .catch(error => {
        console.error('Error deleting knowledge:', error);
        alert('Произошла ошибка при удалении');
      });
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  fill_rz_field();
  setupDeleteHandler();
});