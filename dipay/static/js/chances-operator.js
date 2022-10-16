

//  控制全长文本的收放，用一个function实现收放两个动作
function expandRemark(iTag) {
    let pk = $(iTag).attr("pk");
    let $icon = $(`i[pk=${pk}]`);
    let $remark = $("#remark_"+pk);
    let rawText = $remark.attr("text");

    // 判断more_icon的状态，决定动作
    if ($icon.hasClass('fa-chevron-down')) {
         $icon.removeClass('fa-chevron-down').addClass("fa-chevron-up")
    } else {
         $icon.removeClass('fa-chevron-up').addClass("fa-chevron-down")
    }
    // 交换 text存储的文本和span中显示的文本
    $remark.attr("text",$remark.html());
    $remark.html(rawText);
}