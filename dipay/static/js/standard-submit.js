

var submitNewOrder =  debounce( checkNewOrder,500)


function checkNewOrder() {
   var amount = $("input[name=amount]").val()
   if (amount <= 0) {
       ShowMsg("发票金额必须大于零")
       return
   }
    $("#submitbtn").trigger("click");
}


// 防抖函数
function debounce(fn, delay) {
    var timer = null;
    return function (e) {
        var args = e;
        if (timer) {
            clearTimeout(timer);
        }
        timer = setTimeout(()=>{
             fn(args)
        }, delay)
    }
}


