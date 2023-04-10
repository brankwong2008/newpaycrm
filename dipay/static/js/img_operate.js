
// 关闭照片popup

function closeImg() {
    $("#ImgModal").css("display","none");
    $("#img01").css("width","auto").css("height","auto");
    $("#img01").css("max-height","80%").css("max-width","80%");
}


// 放大图片
function Zoomout() {
   // 获取图片控件
    var $img = $(".newmodal-content");
    var width = $img.css("width");
    var height = $img.css("height");
    // 千万要记住输出的是什么类型的
    $img.css("width",(parseFloat(width)+50)+"px").css("height",(parseFloat(height)+50)+"px");
    // 把max-width和height属性变成200%，否则不能比原图形大
    $img.css("max-width","200%").css("max-height","200%");
}

//  chatGPT给的建议
// function Zoomout() {
//   var img = document.getElementById("img01");
//   var currWidth = img.clientWidth;
//   if (currWidth == 1000) return false;
//   else img.style.width = (currWidth + 50) + "px";
// }


// 放大图片
function Zoomin() {
   // 获取图片控件
    var $img = $(".newmodal-content");
    var width = $img.css("width");
    var height = $img.css("height");
    // 千万要记住输出的是什么类型的
    $img.css("width",(parseFloat(width)-50)+"px").css("height",(parseFloat(height)-50)+"px");
    // 把max-width和height属性去掉，否则不能比原图形大
    $img.css("max-width","200%").css("max-height","200%");
}
