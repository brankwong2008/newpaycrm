// // 弹出新的网页，modal框在控制select下来搜索的情况下有冲突
// function showAPP(tag) {
//     var href = tag.href;
//     var name = '登录'
//     var win = window.open(href, name, 'left=500,top=300,width=400,height=300');
//     win.focus();
//     return false
//
// }


// 改成modal框的弹出方式，把整个体验做一致了
function showAPP(tag) {
    var href = tag.href;
    // 获取get的数据，显示需要用户数据的界面
    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            console.log(respond)
            $('#FastCreateModal .modal-body .modal-details').replaceWith(respond);

            // 显示模态框
            // $('#id_customer').selectpicker('render');
            $('#id_customer').selectpicker('show');
            $('#FastCreateModal').modal('show');

        }
    });

     return false;
}


function closePopup(buttontag) {
    $('#FastCreateModal').modal('toggle');
    $('#fast-add-submit').trigger('click');
    console.log("closePopup() workds")

    // $(id).children().attr('selected',false);
    // $(id).prepend('<option value=' + newID + ' selected >' + newRepr + '</option>')
    // win.close();
    //  // 必须要刷新picker，否则不显示也搜不到
    // $(id).selectpicker('refresh');
    // $(id).selectpicker('render');
}
