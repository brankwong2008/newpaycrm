// 关闭照片popup

function closeImg() {
    $("#ImgModal").css("display", "none");
    $("#img01").css("width", "auto").css("height", "auto");
    $("#img01").css("max-height", "80%").css("max-width", "80%");
}


// 放大图片
function Zoomout() {
    // 获取图片控件
    var $img = $(".newmodal-content");
    var width = $img.css("width");
    var height = $img.css("height");
    // 千万要记住输出的是什么类型的
    $img.css("width", (parseFloat(width) + 50) + "px").css("height", (parseFloat(height) + 50) + "px");
    // 把max-width和height属性变成200%，否则不能比原图形大
    $img.css("max-width", "200%").css("max-height", "200%");
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
    $img.css("width", (parseFloat(width) - 50) + "px").css("height", (parseFloat(height) - 50) + "px");
    // 把max-width和height属性去掉，否则不能比原图形大
    $img.css("max-width", "200%").css("max-height", "200%");
}

// 付费单页面上传文件的图标控制
// 点击上传图标触发文件选择框
function uploadImg(iconTag) {
    const pk = $(iconTag).attr("id").split("-")[1]
    const link = $(iconTag).attr("link")
    const csrfmiddlewaretoken = $(`[name=csrfmiddlewaretoken]`).val()
    const imageName = $(iconTag).prev().attr("name");
    var inputID = `#imageInput-${pk}`
    if (imageName === "ttcopy") {
        inputID = `#imageInput-ttcopy-${pk}`
    }

    console.log(imageName);

    $(inputID).on('change', function () {
        const file = this.files[0];

        if (file) {
            const formData = new FormData();
            formData.append(imageName, file);
            // formData.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
            if (imageName === "ttcopy") {
                formData.append("bank", 2);
                formData.append("remark", "remarkxxxx")
            }

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
                    setTimeout("location.reload()", 1000);
                },
                error: function () {
                    alert("error, cannot proceed")
                }
            });
        }
    })

    if (imageName === "fee_invoice") {
        $(inputID).click()
    } else {
        $.ajax({
            url: link,
            type: 'GET',
            data: '',
            success: function (response) {
                console.log(response)
                $('#myModalLabel').text("新增付款信息");
                $('#myModal .modal-body .mymodal-details').replaceWith(response);
                $('#myModal').modal('show');
                $('#myModal .modal-body .mymodal-details form .selectpicker').selectpicker('show');
            },
            error: function () {
                alert("error, cannot proceed")
            }
        })

    }
}


// 快速上传付款水单
function submitPaymentslip(spanTag) {
    const formData = new FormData();
    $("#myModal .mymodal-details form [name]").each(function (i) {
        const itemname = $(this).attr("name")
        if (itemname==="ttcopy") {
            formData.append(itemname, this.files[0])
        }else{
            formData.append(itemname, $(this).val())
        }
    })
    const link = $("#myModal .mymodal-details form").attr("action")

    $.ajax({
        url: link,
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            if(response.status) {
                $('#myModal').modal('hide');
                ShowMsg(response.msg)
                setTimeout("location.reload()", 1000);
            }
        },
        error: function () {
            alert("system error")
        }
    })

}

