

// 点击切换任务状态 (模拟点击批量处理按钮的效果）

function accomplishTask(atag) {
    var data_obj = new Object();
    // 加入csrf token
    data_obj['csrfmiddlewaretoken'] = $("[name='csrfmiddlewaretoken']").val();
     // 加入 handle_type
    data_obj['handle_type'] = 'batch_switch_status';
    // 加入 pk
    data_obj['pk'] = $(atag).attr('pk');

    // 发送ajax 请求
       $.ajax({
        url: atag.href,
        type: "post",
        data: data_obj,
        // 当响应正常的时候执行success，responses是响应的json数据
        success: function (response) {
            console.log(response);
            if (response.status) {
                location.reload();
            } else {
                console.log('errors');
            }
        }
    })
    return false;

}

function switchUrgence(atag) {
    var urgence = $(atag).attr('urgence');
    var ret = urgence=='True'?'False':'True';
    var pk = $(atag).attr('pk');

    //构建input标签，模拟savePlan需要的数据
     var $input = `<input id='urgence-id-${pk}' class="hidden" value='${ret}' >`
     $(atag).after($input);
     // 如果是更新为紧急，同时把sequence改为0
     if (ret=='True') {
         $(`[id$='sequence-id-${pk}']`).val(0)
     };

    // 触发savePlan
    $(`.save-sequence[pk="${pk}"]`).trigger('click');

    return false;



}
