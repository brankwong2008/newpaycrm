
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder


class ForwarderHandler(PermissionHanlder,StarkHandler):

    search_list = ["title__icontains",]
    search_placeholder = "搜索 货代名"

