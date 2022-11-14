
//定义全局变量 货代，货币
let forwarder_list=[];
let currency_list=[];
let totalAmount =new Decimal(0);

function showTotalValue(val,currency) {
    totalAmount = totalAmount.add(new Decimal(val))
    if (totalAmount == 0) {
         $("#total-chozen-amount-label").css("display","none")
    } else {
         $("#total-chozen-amount-label").css("display","")
    }
    $("#total-chozen-amount").html(totalAmount.toString());
    $("#total-chozen-amount-currency").html(currency);

}

//  点击单元格也能触发 function addToPayCharge，方便操作，这里重点是防止冒泡事件的发生
$("[name$=amount]").parent('td').click(function (event) {
    if (event.target==this){ $(this).children(":first").trigger("click");}
    return false; //只能阻止空间的默认事件，但是不能阻止冒泡
})


// 点击把费用表中的金额和订单号增加到提交清单中
function addToPayCharge(spanTag) {
    let $span = $(spanTag);
    let name = $span.attr("name");
    let val = $span.text();
    let pk = $span.attr("pk");
    let currency =  $span.attr("name")=="USD_amount"?"$":"￥";
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
        showTotalValue(-val,currency)
    }
    else {
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
        // 加到合计金额中区，并显示
        showTotalValue(val,currency)
        console.log('forwarder_id,currency name',forwarder_id,name)

    }
    return false;
}


// 批量处理： 生成付款单的按钮事件
function createPaySlip() {
    let formdata = new Object();
    formdata = $("form").serialize();
    console.log('formdata:', formdata)

    $.ajax({
        url:"",
        type: 'post',
        data: formdata,
        success: function (res) {
            console.log('got a response', res)
            if (res.status) {
                ShowMsg(res.msg,);
                // 延迟两秒，跳转到付费单页面
                setTimeout(()=>{location.href = res.url;},1000)

            } else {
                 ShowMsg(res.msg,time=2000);
            }
        },
        error:function(res){
            console.log(res)}
    });
    return false

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