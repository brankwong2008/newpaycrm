
$(function () {
    $('input[id^="check_all_"]').change(function () {
        var is_check = $(this).prop("checked");
        var children_cls = $(this).attr("id")
        $("."+children_cls).prop("checked",is_check);
    })

})