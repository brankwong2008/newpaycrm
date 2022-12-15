// 提交新增收款前的检查
function inspectSubmitPayment() {

    //思路如下
    // 手工检查和调整需要调整的内容
    // 检查如果发现严重问题直接return false
    // 检查如果发现可能有问题，提示用户，由用户决定是否继续提交
    // 手工检查通过后，触发form表单submit按钮
    console.log('enter intou sumit')

    // 手工检查和调整需要调整的内容
    let $form = $('#new-payment');
    let amount = $form.find('[name=amount]').val();
    let got_amount = $form.find('[name=got_amount]').val();

    if (amount == 0 || got_amount == 0) {
        ShowMsg("水单金额和收到金额不能为空")
        return false;
    }

    if (eval(got_amount) > eval(amount)) {
        ShowMsg("收到金额不应大于水单金额")
        return false;
    }

    // Decimal的减法是支持的，但是比较大小不行
    if (Decimal(amount) - Decimal(got_amount) > 100) {
        let ans = confirm('手续费差异超过100，是否继续提交')
        if (!ans) {
            return false
        }
    }

    // 手工检查通过后，触发form表单submit按钮
    $form.find('button[type=submit]').trigger('click')

}


// 校正input number里面的输入，自动去除非数值字符
function justifyNumberInput(inputTag){
    var content = $(inputTag).val();
    if (content){
        $(inputTag).val(content.replaceAll(/[^0-9\.]/g,''))
    }
}
