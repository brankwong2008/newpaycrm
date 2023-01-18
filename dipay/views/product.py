
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder
from django.utils.safestring import mark_safe
from dipay.utils.tools import str_width_control

class ProductHandler(StarkHandler):
    page_title = "产品管理"

    search_list = ['title__icontains',]
    search_placeholder = "搜索 品名"

    # 详情display
    def remark_display(max_length = None):
        def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
            if is_header:
                return '详情'
            else:
                remark, is_long = str_width_control(obj.remark,max_length)
                remark_origin = obj.remark.replace('"','&quot')
                if is_long:
                    remark_text = "<span id='remark_%s' text='%s'>%s</span>" % (obj.pk, remark_origin, remark) + \
                                  "<i class='fa fa-chevron-down more' pk='%s' onclick='expandRemark(this)'></i>" % obj.pk
                else:
                    remark_text = remark

                return mark_safe(remark_text)
        return inner


    fields_display = ["title",
                      "spec",
                      "thick",
                      remark_display(50),
                      ]


    css_for_show_list = " .header-4{width:30%}"


