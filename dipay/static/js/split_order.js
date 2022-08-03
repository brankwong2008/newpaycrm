// 点击加号新增一行同样数据
function addRow(btn) {
    // btn是加号所在单元格的td标签
    var sub_sequence = $(btn).siblings().eq(2).children(":first").val();
    var $newTr = $(btn).parent().clone();
    $newTr.children().eq(2).children(":first").val(parseInt(sub_sequence) + 1);
    $('tbody').append($newTr);
    $(btn).replaceWith('<td></td>');

}

// 自动调整发票金额
function rectAmount(inputbox) {
    var total_amount = inputbox.getAttribute("total_amount");
    var temp = inputbox.value;
    if (parseFloat(temp) > parseFloat(total_amount)) {
        alert('金额超过总额');
        return false;
    }
    // console.log('total amount', total_amount,temp);
    var remain_amount = minus(total_amount, temp);
    $('.split-amount').val(remain_amount);
    inputbox.value = temp;
}


// 自动调整定金分配金额
function rectRcvdAmount(inputbox) {

    var total_rcvd_amount = inputbox.getAttribute("total_rcvd_amount");
    var temp = inputbox.value;
    if (parseFloat(temp) > parseFloat(total_rcvd_amount)) {
        alert('金额超过总额');
        return false;
    }
    // console.log('total amount', total_rcvd_amount,temp);
    // var remain_amount = (total_rcvd_amount * 100 - temp * 100) / 100;
    var remain_amount = minus(total_rcvd_amount, temp ) ;
    $('.split-rcvd-amount').val(remain_amount);
    inputbox.value = temp;

}

// 定义一个保留精度的减法运算，就是先把小数转换为整数，然后再转换为小数
function minus(arg1, arg2) {
    // 把小数处理为整数，默认小数点后不多于两位
    var args = [arg1, arg2];
    for (var i in args) {
        var res = args[i].toString().split('.');
        if (res.length > 1) {
            var r1_int = res[0];
            var r1_dec = res[1].padEnd(2, '0');
            args[i]= r1_int * 100 + parseInt(r1_dec);
            // console.log(i,args[i])
        } else {
            args[i] = args[i] * 100;
            // console.log(i,args[i])
        }
    }
    return (args[0]-args[1])/100;

}


