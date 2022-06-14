
function showAPP(tag) {
    var href = tag.href;
    var name = '登录'
    var win = window.open(href, name, 'left=500,top=300,width=400,height=300');
    win.focus();
    return false

}

function closePopup(win, newID, newRepr, id) {
    $(id).children().attr('selected',false);
    $(id).prepend('<option value=' + newID + ' selected >' + newRepr + '</option>')
    win.close();
     // 必须要刷新picker，否则不显示也搜不到
    $(id).selectpicker('refresh');
    $(id).selectpicker('render');
}
