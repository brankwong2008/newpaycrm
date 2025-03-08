
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

// 付费单页面上传文件的图标控制
// 点击上传图标触发文件选择框
function uploadImg(iconTag) {
    const pk = $(iconTag).attr("id").split("-")[1]
    const link = $(iconTag).attr("link")
    const csrfmiddlewaretoken = $(`[name=csrfmiddlewaretoken]`).val()
    const name = $(`#imageInput-${pk}`).attr("name");
    console.log(name);


    $(`#imageInput-${pk}`).on('change', function() {
        const file = this.files[0];
        console.log("imageinput changed")
        if (file) {
            const formData = new FormData();
            const imageName = $(`#imageInput-${pk}`).attr("name")
            formData.append(imageName, file);
            // formData.append("csrfmiddlewaretoken", csrfmiddlewaretoken);

            $.ajax({
                url: link,
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                headers: {
                    'X-CSRFToken': csrfmiddlewaretoken
                },
                success: function (data) {
                    ShowMsg(data.msg)
                    setTimeout("location.reload()", 800);
                },
                error: function () {
                    alert("error, cannot proceed")
                }
            });
        }
    })

    $(`#imageInput-${pk}`).click()


}

