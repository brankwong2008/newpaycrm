
$(function () {
    $('input[id^="check_all_"]').change(function () {
        console.log(1111111)
        var is_check = $(this).prop("checked");
        console.log(2222,is_check)
        var children_cls = $(this).attr("id")
        $("."+children_cls).prop("checked",is_check);

    })

})