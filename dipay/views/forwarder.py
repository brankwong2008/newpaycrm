
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder


class ForwarderHandler(PermissionHanlder,StarkHandler):

    page_title = '货代'
    search_list = ["title__icontains","contact__icontains"]
    search_placeholder = "搜索 货代名 联系人"
    show_list_template = "dipay/show_forwarder_list.html"

