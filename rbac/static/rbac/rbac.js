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
         $(this).css("background",'#79a4cf')
         $(this).next().toggleClass('hide');
         // 将其他菜单收拢
          $(this).parent().siblings().children('.sub-titles').addClass('hide');
          $(this).parent().siblings().children('.title').css('background','')


    });
})(jQuery);