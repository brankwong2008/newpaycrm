import os
from django.conf import settings
from stark.service.starksite import StarkHandler
from django.shortcuts import render,redirect
from django.conf.urls import url
from django.http import JsonResponse, HttpResponse
from dipay.forms.forms import ProductPhotoAddModelForm,ProductPhotoEditModelForm
from rbac.utils.common import compress_image
import threading
from dipay.models import ProductPhoto

class ProductPhotoHandler(StarkHandler):
    page_title = "产品图片"

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

    def get_queryset_data(self, request, is_search=None, *args, **kwargs):
        product_id = kwargs.get("product_id")
        photos = self.model_class.objects.filter(product_id = product_id).order_by("-ismain")
        return photos


    def show_list(self, request, *args, **kwargs):
        show_template = "dipay/product_photo_show_list.html"

        product_id = kwargs.get("product_id")
        if product_id:
            add_url = self.reverse_add_url(*args, **kwargs)
        else:
            add_url = self.reverse_add_url(*args, **kwargs)
        add_btn = "<a href='%s' class='btn btn-primary add-record'> + </a>" % (add_url)

        photos = self.get_queryset_data(request, is_search=None, *args, **kwargs)
        product_name = photos.first().product.title_English if photos else ""

        return render(request, show_template, locals())

    def get_model_form(self, handle_type=None):
        if handle_type == "add":
            return ProductPhotoAddModelForm
        else:
            return ProductPhotoEditModelForm

    def save_form(self, form, request, is_update=False, *args, **kwargs):
        if is_update == False:
            product_id = kwargs.get("product_id")
            form.instance.product_id =  product_id
            # 如果是第一张照片，自动设为主图
            if not ProductPhoto.objects.filter(product_id=product_id):
                form.instance.ismain = True
            # 压缩图片
            if form.instance.photo:
                t = threading.Thread(target=compress_image, args=(form.instance.photo.path, 900))
                t.start()

        product_id = form.instance.product_id
        if form.instance.ismain == True:
            self.model_class.objects.filter(product_id=product_id,ismain=True).update(ismain=False)

        form.save()
        productphoto_list_url = self.reverse_list_url(*args, **kwargs)
        return redirect(productphoto_list_url)

    # 删除一条记录
    def del_list(self, request, pk, *args, **kwargs):
        del_obj = self.get_del_obj(request, pk, *args, **kwargs)

        if not del_obj:
            return HttpResponse("将要删除的记录不存在")
        back_url = self.reverse_list_url(*args, **kwargs)

        if request.method == "GET":
            return render(request, self.del_list_template or "stark/del_list.html", locals())

        if request.method == "POST":
            try:
                del_obj.delete()
                # 同时删除对应的图片
                file_path = del_obj.photo.path
                os.remove(file_path)
            except Exception as e:
                msg = '存在关联记录，不能删除，错误：%s ' % e
                return render(request, 'dipay/msg_after_submit.html', locals())

            return redirect(back_url)
