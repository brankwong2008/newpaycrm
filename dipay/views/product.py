from django.shortcuts import reverse
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder
from django.utils.safestring import mark_safe
from dipay.utils.tools import str_width_control
from dipay.models import Product, ProductPhoto


class ProductHandler(StarkHandler):
    page_title = "产品管理"

    search_list = ['title__icontains',"title_English__icontains" ]
    search_placeholder = "搜索 品名 英文品名"

    popup_list = ["supplier",]


    # 详情display
    def remark_display(max_length=None):
        def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
            if is_header:
                return '详情'
            else:
                remark, is_long = str_width_control(obj.remark, max_length)
                remark_origin = obj.remark.replace('"', '&quot')
                if is_long:
                    remark_text = "<span id='remark_%s' text='%s'>%s</span>" % (obj.pk, remark_origin, remark) + \
                                  "<i class='fa fa-chevron-down more' pk='%s' onclick='expandRemark(this)'></i>" % obj.pk
                else:
                    remark_text = remark

                return mark_safe(remark_text)

        return inner

        # 详情display

    def photo_display(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '图片'
        else:

            photos = obj.productphoto_set.all()
            img_tag = "--"
            if photos:
                img_url = photos.get(ismain=True).photo.url
                img_tag = f"<img class='ttcopy-small-img hidden-xs' src={img_url} " \
                                  f"onclick='return popupImg(this)' width='30px' height='30px'>"
            product_photo_url = reverse("stark:dipay_productphoto_list") + "?product_id=" + str(obj.pk)
            more_tag = f"<a href='{product_photo_url}' target='_blank' style='font-size:larger'>...</a>"

            return mark_safe(img_tag + more_tag)


    fields_display = [
        "title",
        "title_English",
        photo_display,
        remark_display(50),
    ]

    css_for_show_list = " .header-4{width:30%}"
