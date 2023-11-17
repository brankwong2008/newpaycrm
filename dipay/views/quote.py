from django.shortcuts import reverse
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder
from django.utils.safestring import mark_safe
from dipay.utils.tools import str_width_control
from dipay.models import Product, ProductPhoto, Quote, ModelNumbers
from django.conf.urls import url

class QuoteHandler(StarkHandler):
    page_title = "报价管理"

    search_list = ['modelnumbers__product__title__icontains']
    search_placeholder = "搜索 品名"

    popup_list = ["supplier",]

    order_by_list = ["-id"]

    def get_urls(self):
        patterns = [
            url("^list/(?P<modelnumber_id>\d+)/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^list_detail/(?P<pk>\d+)/(?P<modelnumber_id>\d+)/$", self.wrapper(self.show_detail), name=self.get_url_name('show_detail')),
            url("^add/(?P<modelnumber_id>\d+)/$", self.wrapper(self.add_list), name=self.get_add_url_name),
            url("^edit/(?P<pk>\d+)/(?P<modelnumber_id>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/(?P<modelnumber_id>\d+)/$", self.wrapper(self.del_list), name=self.get_del_url_name),
            url("^create/(?P<modelnumber_id>\d+)/$", self.wrapper(self.create_list), name=self.get_url_name('create')),
        ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())

        return patterns


    def get_render_form(self, form, *args, **kwargs):
        # 对于add_form进行部分值的初始化
        modelnumber_id = kwargs.get("modelnumber_id")
        modelnumber_obj = ModelNumbers.objects.get(pk=modelnumber_id)
        form.fields['modelnumbers'].initial = modelnumber_obj
        form.fields['supplier'].initial = modelnumber_obj.product.supplier.all().first()
        print("the supplier is:", modelnumber_obj.product.supplier.all().first())
        return form

    def get_queryset_data(self, request, is_search=None, *args, **kwargs):
        modelnumber_id = kwargs.get("modelnumber_id")
        return self.model_class.objects.filter(modelnumbers_id=modelnumber_id )

