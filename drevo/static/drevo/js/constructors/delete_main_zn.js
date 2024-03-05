function deleteZn(zn_id, name, type_of_zn) {
    $('.confirmation-of-delete').text(`Вы действительно хотите удалить знание <${name}>?`);
    $('#zn_delete_modal').modal("show");
    $('.okay-delete').click(function () {
        if (type_of_zn === 'document') {
            fetch(`/drevo/delete_complex_zn/?id=${zn_id}`)
                .then(response => response.json())
                .then(data => {
                    window.location.href = data.redirect_url;
                });
        }
        else if (type_of_zn === 'algorithm') {
            fetch(`/drevo/delete_algorithm/?id=${zn_id}`)
                .then(response => response.json())
                .then(data => {
                    window.location.href = data.redirect_url;
                });
        }
    })
}

