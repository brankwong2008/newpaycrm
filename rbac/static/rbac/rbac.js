(function (jq) {
    jq('.multi-menu .title').click(function () {
        // var $status = $(this).next().hasClass('hide');
        //
        // $('.multi-menu .sub-titles').addClass('hide');
        // if ($status) {
        //     $(this).next().removeClass('hide')
        // } else {
        //     $(this).next().addClass('hide')
        // }

        // 第二种写法
        $(this).css("background", '#79a4cf')
        $(this).next().toggleClass('hide');
        // 将其他菜单收拢
        $(this).parent().siblings().children('.sub-titles').addClass('hide');
        $(this).parent().siblings().children('.title').css('background', '')


    });
})(jQuery);

// 清除搜索框的内容的js
function clearSearch() {
    $("input[name='q']").val('');

}


// 显示和收起筛选区域
function toggleOptionSection() {
    $('div.options-section').toggleClass('hidden');

}


// 自定义消息提示框的淡入淡出
function ShowTip(tip, type,time=2000) {
    var $tip = $('#tip');
    if ($tip.length == 0) {
        var $tip_span = `<span id='tip' style='position:fixed; top:100px;left:50%;z-index:99;height:35px;line-height: 8px'>${tip}</span>`;
        $('body').append($tip_span);
    }
    $('#tip').stop(true).prop('class', 'alert alert-' + type).text(tip).fadeIn(500).delay(time).fadeOut(500);
}

function ShowMsg(msg,time=2000) {
    console.log('show msg....:', msg)
    ShowTip(msg, 'info',time)
}

