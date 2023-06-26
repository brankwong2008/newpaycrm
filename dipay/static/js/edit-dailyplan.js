

// 点击切换任务状态 (模拟点击批量处理按钮的效果）
function accomplishTask(atag) {
    console.log('enter accompany task')
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

// 切换紧急状态
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


// 在任务列表简单新增任务的模态框弹出
function simpleAddDailyPlan(atag) {
    var href = atag.href;
    var title = '新任务';

    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            $('#taskModalLabel').text(title);
            $('#taskModal .modal-body .mymodal-details').replaceWith(respond);
            // 给form的action加上url
            $('#taskModal .modal-body .mymodal-details form').attr('action', href);
            var $input = `<input type="hidden" name="link_id" id="id_link_id" value=''>`
            $('#taskModal .modal-body .mymodal-details form').append($input);
            $('#taskModal .modal-body .mymodal-details form span.dailyplan').attr('id', 'task_button');
            $('#taskModal').modal('show');
            $('#taskModal .modal-body .mymodal-details form .selectpicker').selectpicker('show');
            // 光标foucus到第一个input框
            setTimeout("$('#taskModal form input[type=text]').first().focus()", 500)

        }
    });
    return false;
}



// 给提交任务信息手动绑定一个点击事件
// $('#taskModal .modal-body').on('click', 'span.dailyplan', function (e) {
//     var href = $('#taskModal .modal-body  form').attr('action');
//     var data_obj = new Object();
//     // 手动获取form中的input name和val， 存入data_obj
//     $('#taskModal .modal-body form [name]').each(function (i) {
//         data_obj[$(this).attr('name')] = $(this).val()
//     })
//
//
//     $.ajax({
//         url: href,
//         type: 'post',
//         data: data_obj,
//         success: function (respond) {
//             console.log(respond)
//             if (respond.status) {
//                 $('#taskModal').modal('hide');
//                 ShowMsg(respond.msg);
//                 setTimeout("location.reload()", 500);
//             } else {
//                  $('#taskModal .modal-header .modal-error').html(respond.msg)
//             }
//         }
//     });
//
// });


// 在跟单页面提交新增任务  ， 因为模态框有多个名字的情况，可能导致使用的时候混乱，需要提前规划好
function  submitAddDailyplanForm(spanTag){
    var $form = $(spanTag).parent().parent();
    console.log($form)
    var href = $form.attr('action');
    var data_obj = new Object();
    // 手动获取form中的input name和val， 存入data_obj
    $form.find('[name]').each(function (i) {
        data_obj[$(this).attr('name')] = $(this).val()
    })

    $.ajax({
        url: href,
        type: 'post',
        data: data_obj,
        success: function (respond) {
            console.log(respond)
            if (respond.status) {
                $("[id$='Modal']").modal('hide');
                ShowMsg(respond.msg);
                setTimeout("location.reload()", 500);
            } else {
                 $('[id$="Modal"] .modal-header .modal-error').html(respond.msg)
            }
        }
    });

}



//回车提交新增任务，并清除默认动作 （需要事件委派，因为input这个内容是后生成的）
$('#taskModal .modal-body').on('keypress', 'input', function (event) {
    console.log('event kecode:', event.keyCode)
    // 判断keycode 是不是回车，回车的code是13
    if (event.keyCode == 13) {
        //回车执行自定义的动作
        $('span.dailyplan').click();
        //  return false, 避免回车的默认事件
        return false;
    }
})

// 提醒项目中的延后一天提醒按钮的功能
function deferToNextDay(spanTag) {
    console.log("defer working")
    var $spanTag = $(spanTag);
    var pk = $spanTag.attr("pk");
    var date = new Date();
    var nextDay = new Date(+date + 1000*60*60*24);
    var year = nextDay.getFullYear();
    var month = nextDay.getMonth()+1;
    var day = nextDay.getDate();
    month = month<10?("0"+month):(month);
    day = day<10?("0"+day):(day);

    var inputTag = `<input type="date" id="remind_date-id-${pk}" value="${year}-${month}-${day}">`;
    $(`#remind_date-id-`+pk).replaceWith(inputTag);

    $(`.save-sequence[pk="${pk}"]`).trigger('click');
    return false;

}

