
//定义全局变量 货代，货币
let forwarder_list=[];
let currency_list=[];


// 点击把费用表中的金额和订单号增加到提交清单中
function addToPayCharge(spanTag) {
    let $span = $(spanTag);
    let name = $span.attr("name");
    let val = $span.text();
    let pk = $span.attr("pk");
    let $input;
    let $checkbox = $(`input[type=checkbox][value=${pk}]`);
    console.log('background-color:', $span.parent().css("background-color"));
    if ($span.hasClass('chosen')) {
        $span.parent().css("background-color", "rgba(0, 0, 0, 0)");
        $span.next("input").remove();
        forwarder_list.pop();
        currency_list.pop();
        $checkbox.prop("checked", !$checkbox.prop("checked"));
        $span.removeClass('chosen')
    } else {
        let $span_forwarder = $(`span[name=forwarder][pk=${pk}]`);
        let forwarder_id = $span_forwarder.attr("forwarder_id");

        // 如果选择的货代不是同一个，不通过
        if (forwarder_list.length>0 && forwarder_id != forwarder_list[forwarder_list.length-1]){
            ShowMsg("必须是同一货代");
            return false
        }
        // 如果选择的币种不是同一个，不通过
        if (currency_list.length>0 && name != currency_list[currency_list.length-1]){
            ShowMsg("必须是同一币种");
            return false
        }

        $span.parent().css("background-color", "#5bc0de");
        $input = `<input type="hidden" name="${name}" value="${val}"  >`;
        $span.parent().append($input)
        $input = `<input type="hidden" name="forwarder_id" value="${forwarder_id}" >`;
        $span_forwarder.after($input)
        // checkbox框反选
         $checkbox.prop("checked", !$checkbox.prop("checked"));
        $span.addClass('chosen')

        forwarder_list.push(forwarder_id)
        currency_list.push(name)
        console.log('forwarder_id,currency name',forwarder_id,name)
    }

}


// 批量处理： 生成付款单的按钮事件
function createPaySlip() {
    let formdata = new Object();
    formdata = $("form").serialize();
    console.log('formdata:', formdata)

    $.ajax({
        url: location.href,
        type: 'post',
        data: formdata,
        success: function (respond) {
            console.log(respond)
            if (respond.status) {
                $('#myModal').modal('hide');
                ShowMsg(respond.msg);

            } else {

            }
        }
    });

    return false;

}

// 跟踪表中点击美元符号弹出模态框：显示费用明细
function showCharges(spanTag) {
    console.log('enter show charges')
    let order_number = $(spanTag).attr("followorder")
    //向服务器请求费用明细
    $.ajax({
        url: $(spanTag).attr("url"),
        type: 'get',
        data: "",
        success: function (respond) {
            console.log(respond)
            // 获取服务render回来的页面，直接显示在模态框中
             $('#myModal .modal-body .mymodal-details').replaceWith(respond);
            $('#myModalLabel').text(order_number +" 运杂费用明细");
            $('#myModal').modal('show');

        }
    });


}