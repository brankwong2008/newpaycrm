from stark.service.starksite import StarkHandler
from django.shortcuts import render,redirect
from django.http import JsonResponse
from dipay.forms.forms import ProductPhotoAddModelForm,ProductPhotoEditModelForm
from rbac.utils.common import compress_image
import threading

class ProductPhotoHandler(StarkHandler):
    page_title = "产品图片"

    def get_queryset_data(self, request, is_search=None, *args, **kwargs):
        product_id = request.GET.get("product_id")
        photos = self.model_class.objects.filter(product_id = product_id).order_by("-ismain")
        return photos


    def show_list(self, request, *args, **kwargs):
        show_template = "dipay/product_photo_show_list.html"

        product_id = request.GET.get("product_id")
        if product_id:
            add_url = self.reverse_add_url(*args, **kwargs) + "&product_id=" + product_id
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
            product_id = request.GET.get("product_id")
            form.instance.product_id =  product_id
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

