from django.shortcuts import render, redirect, reverse
from stark.service.starksite import StarkHandler
from django.conf.urls import url
from dipay.models import Product


class ModelNumbersHandler(StarkHandler):
    page_title = "产品型号"

    def get_urls(self):
        patterns = [
            url("^list/(?P<product_id>\d+)/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^list_detail/(?P<pk>\d+)/$", self.wrapper(self.show_detail), name=self.get_url_name('show_detail')),
            url("^add/(?P<product_id>\d+)/$", self.wrapper(self.add_list), name=self.get_add_url_name),
            url("^edit/(?P<pk>\d+)/(?P<product_id>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/(?P<product_id>\d+)$", self.wrapper(self.del_list), name=self.get_del_url_name),
            url("^create/$", self.wrapper(self.create_list), name=self.get_url_name('create')),
        ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())

        return patterns

    def get_render_form(self, form, *args, **kwargs):
        # 对于add_form进行部分值的初始化
        product_id = kwargs.get("product_id")
        form.fields['product'].initial = Product.objects.get(pk=product_id)
        return form

        # 新增一条记录
    def add_list(self, request, *args, **kwargs):
        if request.method == "GET":
            form = self.get_model_form("add")()
            form = self.get_render_form(form,*args, **kwargs)
            # 当返回数据给模态框时，get_type = simple，只返回核心内容
            get_type = request.GET.get('get_type')

            # 从跟单页面直接添加关联任务时触发这个功能，以get_type来区分
            if get_type == 'simple':
                self.add_list_template = "dipay/modelnumbers_simple_change_list.html"
            return render(request, self.add_list_template or "stark/change_list.html", locals())

        if request.method == "POST":
            form = self.get_model_form(handle_type="add")(request.POST, request.FILES)
            if form.is_valid():
                result = self.save_form(form, request, False, *args, **kwargs)
                return result or redirect(reverse("stark:dipay_product_list"))
            else:
                return render(request, self.add_list_template or "stark/change_list.html", locals())

    def save_form(self, form, request, is_update=False, *args, **kwargs):
        form.save()
        backurl = request.POST.get("backurl")
        return redirect(backurl) if backurl else None
