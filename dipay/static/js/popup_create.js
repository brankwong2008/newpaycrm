// 改成modal框的弹出方式，把整个体验做一致了
function showAPP(tag) {
    var href = tag.href;
    // 获取get的数据，显示需要用户数据的界面
    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            console.log('get get request, got responds from server ...')
            $('#FastCreateModal .modal-body .modal-details').replaceWith(respond);
            $('#FastCreateModal .modal-body .modal-details form').attr('action', href);
            $('#FastCreateModal .modal-error').html('')

            // 获取对应的select的id值，并传递给模态框的提交按钮
            var $select = $(tag).next().find('select')
            console.log($select)
            $('#submit_data').data('select_dom',$select);


            // 显示模态框
            // $('#id_customer').selectpicker('render');
            $('#FastCreateModal .modal-body .modal-details form .selectpicker').selectpicker('show');
            $('#FastCreateModal').modal('show');

        }
    });

    return false;
}


function closePopup(buttontag){


 console.log("closePopup() workds");
    // 如果required的字没有填，则直接调用form的button方法
    var empty_flag = false;
    $("#FastCreateModal .modal-body .modal-details form [name][required]").each(function (i) {
        if (!$(this).val()) {
            empty_flag = true;
            return false;
        }
    });
    // 触发h5的自动数据校验机制
    if (empty_flag) {
        $("#FastCreateModal .modal-body .modal-details form button[type=submit]").click();
        return false
    }

    var formdata = new FormData();
    var form_list = $("#FastCreateModal .modal-body .modal-details form").serializeArray();
    $.each(form_list, function (index, data) {
        formdata.append(data.name, data.value);
    })
    var failure_flag = false;

  // 手动搜集forms中的data，发post请求，并获得返回值，决定是否关闭模态框

    $.ajax({
        url: $('#FastCreateModal .modal-body .modal-details form').attr('action'),
        contentType: false,
        processData: false,
        type: 'post',
        async: false,
        data: formdata,
        success: function (respond) {
            console.log(respond);
            if (respond.status) {
                // 如果成功，关闭模态框
                 $('#FastCreateModal').modal('toggle');
                var newID = respond.data.pk;
                var newRepr = respond.data.title;
                var id = respond.data.id_name;
                // 将新增加的数据添加到select的选项里面，并设为已选
                var $select = $('#submit_data').data('select_dom');
                $select.children().attr('selected', false);
                $select.prepend('<option value=' + newID + ' selected >' + newRepr + '</option>')
                // 必须要刷新picker，否则不显示也搜不到
                $select.selectpicker('refresh');
                $select.selectpicker('render');
            } else {
                // 如果失败在模态框中显示错误信息
                $('#FastCreateModal .modal-error').html(respond.error)
                failure_flag = true;
            }
        }

    });

  //   ajax处理是异步的，所以这个时候，failure flag还是false
  // if (!failure_flag) {
  //     // console.log('failure lag is ',failure_flag )
  //       $('#FastCreateModal').modal('toggle');
  //   }

}





// $(id).children().attr('selected',false);
// $(id).prepend('<option value=' + newID + ' selected >' + newRepr + '</option>')
// win.close();
//  // 必须要刷新picker，否则不显示也搜不到
// $(id).selectpicker('refresh');
// $(id).selectpicker('render');


