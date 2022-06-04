

// 点击加号新增一行同样数据
function addRow(btn) {
        // btn是加号所在单元格的td标签
        var sub_sequence = $(btn).siblings().eq(2).children(":first").val();
        var $newTr = $(btn).parent().clone();
        $newTr.children().eq(2).children(":first").val(parseInt(sub_sequence) + 1);
        $('tbody').append($newTr);
        $(btn).replaceWith('<td></td>');

    }
