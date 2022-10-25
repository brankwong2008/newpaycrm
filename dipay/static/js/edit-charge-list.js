// 点击把费用表中的金额和订单号增加到提交清单中
function addToPayCharge(spanTag) {
    let $span = $(spanTag);
    let name = $span.attr("name");
    let val = $span.text();
    let pk = $span.attr("pk");
    let $input;
    let $checkbox = $(`input[type=checkbox][value=${pk}]`);
    console.log('background-color:', $span.parent().css("background-color"));
    if ($checkbox.prop("checked")) {
        $span.parent().css("background-color", "rgba(0, 0, 0, 0)");
        $span.next("input").remove();

    } else {
        $span.parent().css("background-color", "#5bc0de");
        $input = `<input type="hidden" name="${name}" value="${val}"  >`;
        $span.parent().append($input)
        let $span_forwarder = $(`span[name=forwarder][pk=${pk}]`);
        let forwarder_id = $span_forwarder.attr("forwarder_id");
        $input = `<input type="hidden" name="forwarder_id" value="${forwarder_id}" >`;
        $span_forwarder.after($input)
    }
    $checkbox.prop("checked", !$checkbox.prop("checked"));
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