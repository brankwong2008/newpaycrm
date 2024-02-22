
//  设置每页显示记录条数
function setPerPageCount(selectTag) {

    var perPage = $(selectTag).val();

    var data = {
        'csrfmiddlewaretoken': $("[name='csrfmiddlewaretoken']").val(),
        "per_page_count":perPage
    }

    // 向后台发送用户页面记录选择
    $.ajax({
        url:location.href,
        type:"post",
        data: data,
        success: function (res) {
            console.log(res)
            location.reload()
        }
        }
    )
}