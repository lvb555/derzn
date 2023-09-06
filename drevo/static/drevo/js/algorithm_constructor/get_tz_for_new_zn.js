function get_tz_for_new_zn(id_tr, base_kn_id) {
    // Получение видов знания, учитывая выбранные bz_id и tr_id
    fetch(`/drevo/get_tz_for_zn_in_algorithm?tr_id=${id_tr}&bz_id=${base_kn_id}`)
        .then(response => response.json())
        .then(data => {
            if (Object.entries(data).length !== 0){
                id_tz.prop('disabled', false);
                id_tz.empty();
                const null_option = $('<option>').text('-----');
                id_tz.append(null_option);
                data.tz.forEach(item => {
                    const option = $('<option>').val(item.id).text(item.name);
                    id_tz.append(option);
                });
            }
        });
}
