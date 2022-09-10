// 功能：双击表格，替换成相应的input控件，点击保存更新到数据库

function savePlan(btn) {
    // 找到控件和input信息
    var pk = $(btn).attr('pk');
    var url = $(btn).attr('url');
    var $textarea_list = $(`[id$='-id-${pk}']`);
    // 构建需传输的数据对象
    var data_obj = new Object();
    // 遍历所有的控件，获取name和val
    $textarea_list.each(function (i) {
        var content = $(this).val();
        if (content) {
            var name = $(this).attr('id').split('-')[0];
            // 去除金额里面含有的美元和人民币符号
            if (name == 'amount') {
                var remove_chars = ['$', '￥', ','];
                for (var i in remove_chars) {
                    content = content.replaceAll(remove_chars[i], '');
                }
            }

            data_obj[name] = content;
        }
    });
    // pk 是followorder_obj.pk
    data_obj['pk'] = pk;
    // 加入csrf token
    data_obj['csrfmiddlewaretoken'] = $("[name='csrfmiddlewaretoken']").val();


    // 发送Ajax请求，
    // :text获取type为text的标签, blur失去聚焦事件
    $.ajax({
        url: url,
        type: "post",
        data: data_obj,
        // 当响应正常的时候执行success，responses是响应的json数据
        success: function (response) {
            console.log(response);
            if (response.status) {
                location.reload();
            } else {
                var name = response.field;
                var $target = $(`[id='${name}-id-${pk}']`);
                $target.next().after(`<p class="error">${response.error}</p>`)

            }
        }
    })
}

// 点击后将文本替换为输入框
function showInputBox(sp) {
    // content可能自带空格，需要trim一下
    var content = $(sp).text().trim();
    var id = $(sp).attr('id');
    var temp = id.split('-');
    var pk = temp[temp.length - 1]
    if ($(sp).hasClass('date-display')) {
        var year = $(sp).attr('year');
        var create_date = ''
        if (content != '--') {
            create_date = year + '/' + content.trim();
            create_date = create_date.replaceAll('/', '-');
        }
        console.log('year:', year, content, create_date);
        var $input = `<input type="date" id=${id} value="${create_date}">  
            <i class="fa fa-check" pk="${pk}" onclick="fastInfoSave(this)"></i>`;
        $(sp).replaceWith($input)
    } else if ($(sp).hasClass('status-display')) {
        //  控制状态字段的显示, 分两步，获取选项的choice_list
        var choice = $(sp).attr('choice');
        // 解析json数据格式，还原为列表
        var new_choice = JSON.parse(choice);
        // 获取choice对应的序号
        var choice_sequence = undefined;
        // 构建option标签，加入数据
        var $options = ''
        for (var i in new_choice) {
            // console.log(content, new_choice[i][1])
            if (new_choice[i][1] == content) {
                $options += `<option value="${new_choice[i][0]}" selected>${new_choice[i][1]}</option>`
            } else {
                $options += `<option value="${new_choice[i][0]}" >${new_choice[i][1]}</option>`
            }
        }
        // 构建select标签，加入options，加上对钩按钮
        var $select = ` <select  id="${id}">${$options}</select> 
                        <i class="fa fa-check" pk="${pk}" onclick="fastInfoSave(this)"></i>`
        // 替换原来标签
        $(sp).replaceWith($select)

    } else if ($(sp).hasClass('invoice-amount-display')) {
        var amount = $(sp).attr('amount').trim();
        var $input = `<textarea id=${id}> ${amount} </textarea> 
                    <i class="fa fa-check" pk="${pk}" onclick="fastInfoSave(this)"></i>`;
        $(sp).replaceWith($input);
    } else {
        console.log('content:', content, id)
        // 编辑框旁边显示对钩，直接确认
        var $input = `<textarea id=${id}> ${content} </textarea> 
                    <i class="fa fa-check" pk="${pk}" onclick="fastInfoSave(this)"></i>`;

        $(sp).replaceWith($input);
    }
}


// 给编辑框旁边的小对钩绑定事件，直接指向同一行的save按钮
function fastInfoSave(btn) {
    var pk = $(btn).attr('pk');
    $(`.save-sequence[pk="${pk}"]`).trigger('click');
}


//  隐藏每行的保存按钮
$('span.hidden-xs').parent().addClass('hidden-xs');
$('span.save-sequence').parent().css('display','none');


// 已收和应收的点击弹出收款明细的方法
// function showPayDetails(tag) {
//     var href = tag.href;
//     var name = '登录'
//     // var left = window.screen.availWidth -300
//     var win = window.open(href, name, 'left=600,top=300,width=600,height=450');
//     win.focus();
//     return false
// }


// 已收和应收的点击弹出收款明细的方法
function showPayDetails(tag) {
    var href = tag.href;

    var is_fix_amount = tag.getAttribute("is_fix_amount");
    var customer_name = $(tag).attr('customer_name');
    customer_name = customer_name?customer_name:'--';
    console.log('is_fix_amount', is_fix_amount);
    var title = '收款明细';
    if (is_fix_amount == 'true') {
        console.log('fixe amount is true')
        title = '固定定金';
    }
    title = title + ` (${customer_name})`;

    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            console.log(title);
            $('#myModalLabel').text(title);
            $('#myModal .modal-body .mymodal-details').replaceWith(respond);
            $('#myModal').modal('show');
        }

    });

    return false
}

// 弹出银行水单图片，设置一个
// 的div，然后需要的时候让他显示出来，把背景设置为半透明
function popupImg(atag) {
    var img_url = atag.src;
    $('#img01').attr('src', img_url);
    $('#ImgModal').fadeIn();

    return false;

}

// 弹出固定定金转移modal
function transferFixAmount(atag) {
    var href = atag.href;
    console.log('enter into transferfix amount, atag', atag)
    $('#transferModal').modal('show');

    // 获取返回数据
    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            $('#transferModal .modal-body .transfer-details').replaceWith(respond);
        }

    });


    return false;
}


// 跟踪货物
function trackShipment(atag) {
    // alert('跟踪货物')
    var pk = $(atag).attr('pk');
    // console.log($('#clipboard-btn-'+pk));
    $('#clipboard-btn-'+pk).trigger('click');
    var win = window.open(atag.href, 'trackship', 'left=600,top=300,width=850,height=850');
    win.focus();
    return false;
}

// 弹出财务确认款项的modal框
function  showInwardpayConfirm(atag) {
    var href = atag.href;
    var pk = $(atag).attr('pk');
    $('button.confirm-pay').attr('pk',pk);
    $('button.confirm-pay').attr('link',href);

     $('#myModal').modal('show');

    // 获取返回数据
    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            console.log(respond)
            $('#myModal .modal-body .mymodal-details').replaceWith(respond);
        }

    });

    return false;

}

// 确认款项的post请求发送
function  confirmReceiptInwardpay(atag) {
    var href = $(atag).attr('link');
    var pk = $(atag).attr('pk');

    // 获取返回数据
    $.ajax({
        url: href,
        type: 'post',
        data: {'csrfmiddlewaretoken': $("[name='csrfmiddlewaretoken']").val(),},
        success: function (respond) {
            console.log(respond);
             // $('#myModal').modal('hide');
             location.reload();
        }

    });

    return false;

}


// 在订单跟踪列表新增关联任务
function addDailyPlan(atag) {
    var href = atag.href;
    var pk = $(atag).attr('pk');
    var title = '新建任务';

    $.ajax({
        url: href,
        type: 'get',
        data: '',
        success: function (respond) {
            console.log(title);
            $('#myModalLabel').text(title);
            $('#myModal .modal-body .mymodal-details').replaceWith(respond);
            // 给form的action加上url
            $('#myModal .modal-body .mymodal-details form').attr('action', href);
            var $input = `<input type="hidden" name="link_id" id="id_link_id" value='${pk}'>`
            $('#myModal .modal-body .mymodal-details form').append($input);
            $('#myModal').modal('show');
        }
    });
    return false;
}


// 给提交任务信息手动绑定一个点击事件
 $('#myModal .modal-body').on('click', 'span.dailyplan', function (e) {
     var href = $('#myModal .modal-body  form').attr('action');
     var data_obj = new Object();
    // 手动获取form中的input name和val， 存入data_obj
     $('#myModal .modal-body form [name]').each(function(i){
         data_obj[$(this).attr('name')] = $(this).val()
     })

     console.log(href, data_obj);

    $.ajax({
        url: href,
        type: 'post',
        data: data_obj,
        success: function (respond) {
            $('#myModal').modal('hide');
            ShowMsg(respond.msg)
        }
    });

 });


// 自定义消息提示框的淡入淡出
function ShowTip(tip, type) {
    var $tip = $('#tip');
    if ($tip.length == 0) {
        $tip = $(`<span id='tip' style='position:fixed; top:100px;left:50%;z-index:99;height:35px'></span>`);
        $('body').append($tip);
    }
    $tip.stop(true).prop('class', 'alert alert-' + type).text(tip).fadeIn(500).delay(2000).fadeOut(500);
}

function ShowMsg(msg) {

    ShowTip(msg, 'info')

}