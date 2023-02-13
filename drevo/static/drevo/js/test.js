if (!$) {
    $ = django.jQuery;
}
jQuery(document).ready(function($){
    $(function(){
        console.log("hello")
        let endpoint = $("#test_res").attr("data-url")
        console.log(endpoint)
        $("#id_bz").on('change', function(){
            $.ajax({
                type: 'GET',
                url: endpoint,
                contentType: "application/json; charset=utf-8",
                data: {
                    bz : $("option:selected", this).text() 
                },
                success: (res) => {
                    console.log(res)
                    // $("#id_tr option").each(function(index){
                    //     if (!($(this).text() in Object.keys(res))){
                    //         $(this).hide();
                    //     } 
                    // }) 
                },
                error: (res) => {
                    console.log("error")
                }
            })
            console.log("changed base knowledge")
            console.log(`Current value: ${$("option:selected", this).text()}`)
        })
        $("#id_tr").on('change', function(){
            console.log("changed type of realtion")
            console.log(`Current value: ${$("option:selected", this).text()}`)
        })
        $("#id_rz").on('change', function(){
            console.log("changed connected knowledge")
            console.log(`Current value: ${$("option:selected", this).text()}`)
        })
    })  
});