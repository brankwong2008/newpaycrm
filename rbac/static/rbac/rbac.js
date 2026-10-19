(function (jq) {
    // 页面加载时：给服务端渲染为展开状态的分组标题补上 .open 高亮
    jq('.multi-menu .sub-titles').each(function () {
        if (!jq(this).hasClass('hide')) {
            jq(this).prev('.title').addClass('open');
        }
    });

    jq('.multi-menu .title').click(function () {
        var $title = jq(this);
        // 记录点击前是否处于收起状态
        var willOpen = $title.next().hasClass('hide');
        // 先收拢所有菜单
        jq('.multi-menu .sub-titles').addClass('hide');
        jq('.multi-menu .title').removeClass('open');
        // 再展开当前点击的分组（重复点击同一分组则仅收拢）
        if (willOpen) {
            $title.next().removeClass('hide');
            $title.addClass('open');
        }
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
    ShowTip(msg, 'success',time)
}

