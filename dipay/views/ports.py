
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder

class PortsHandler(StarkHandler):
    page_title = "港口管理"

    search_list = ['title__icontains',]
    search_placeholder = '搜索 港口名'

    verify_similarity_list = ['title', ]

    fields_display = "__all__"


