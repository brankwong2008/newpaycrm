
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder
from django.utils.safestring import mark_safe
from dipay.utils.tools import str_width_control

class CurrentNumberHandler(PermissionHanlder, StarkHandler):
    page_title = "编号管理"

    fields_display = "__all__"


