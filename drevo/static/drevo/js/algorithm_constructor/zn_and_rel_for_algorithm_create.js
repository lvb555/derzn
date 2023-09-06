id_tr = $('#id_tr')
id_tz = $('#id_tz')

fetch(`/drevo/rel_for_algorithm/create?tr_id=${id_tr}`)
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
id_tr.change( function (){
    get_tz_for_new_zn($('#id_tr').val(), $('#base_kn_id').val())
})