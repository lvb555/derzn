if (!$) {
    $ = django.jQuery;
}
jQuery(document).ready(function($){
    $(function(){
        console.log("hello")
        console.log($("#id_bz").val())
        let bz_endpoint = $("#load_tr").attr("data-url")
        let tr_endpoint = $("#load_bz").attr("data-url")
        let tr_choice;
        console.log(bz_endpoint)
        console.log(tr_endpoint)
        $("#id_bz").on('change', function(){
            if (tr_choice!=undefined){
                $.ajax({
                    type: 'GET',
                    url: bz_endpoint,
                    contentType: "application/json; charset=utf-8",
                    data: {
                        bz : $("option:selected", this).text() 
                    },
                    success: (res) => {
                        console.log(res)
                        let html_data = '<option value="">----------</option>'
                        for (const [name, id] of Object.entries(res)) {
                            console.log(name, id);
                            html_data += `<option value="${id}">${name}</option>`;
                        }
                        console.log(html_data)
                        $("#id_tr").html(html_data);
                        console.log($("#id_bz").val())
                    },
                    error: (res) => {
                        console.log("error")
                    }
                })
            }
            })
            console.log("changed base knowledge")
            console.log(`Current value: ${$("option:selected", this).text()}`)
        })
        $("#id_tr").on('change', function(){
            tr_choice = $("option:selected", this).attr('value')
            let $select = $("#id_bz");
            $select.select2("destroy").djangoAdminSelect2({
                ajax: {
                data: function (params) {
                    return {
                    term: params.term,
                    page: params.page,
                    app_label: $select.data("app-label"),
                    model_name: $select.data("model-name"),
                    field_name: $select.data("field-name"),
                    tr: tr_choice 
                    }
                }
            }
            })
            // $.ajax({
            //     type: 'GET',
            //     url: tr_endpoint,
            //     contentType: "application/json; charset=utf-8",
            //     data: {
            //         tr : $("option:selected", this).text() 
            //     },
            //     success: (res) => {
            //         // $("#id_bz").select2();
            //         console.log(res)
            //         tr_changed = true
            //         $('#id_bz').val(null).trigger('change.select2')
            //         console.log($('.select2 select2-container select2-container--admin-autocomplete select2-container--focus').val())
            //         // let html_data = '<option value="">----------</option>'
            //         for (const [name, id] of Object.entries(res)) {
            //             console.log(name, id);
            //             let newOption = new Option(name, id, false, false)
            //             console.log('--------------------------')
            //             $("#id_bz").append(newOption).trigger('change.select2');
            //             //html_data += `<option value="${id}">${name}</option>`;
            //         }
            //         // console.log(html_data)
            //         // $("#id_bz").val(html_data);
            //         //$("#id_bz").select2().trigger('change.select2');
            //         //-------------------------------
            //         //select2 select2-container select2-container--admin-autocomplete select2-container--focus



            //         //select2-id_bz-container
            //     },
            //     error: (res) => {
            //         console.log("error")
            //     }
    
            console.log("changed type of realtion")
            console.log(`Current value: ${$("option:selected", this).text()}`)
        })
    // }
        $("#id_rz").on('change', function(){
            console.log("changed connected knowledge")
            console.log(`Current value: ${$("option:selected", this).text()}`)
        })
    }) 