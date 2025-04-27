import os
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import PermissionHanlder
from django.conf.urls import url
from django.shortcuts import render, HttpResponse, redirect,reverse
from openpyxl import load_workbook
from dipay.models import UserInfo
from django.utils.safestring import mark_safe
from dipay.utils.create_random_string import get_string
from paycrm import secret
from dipay.forms.forms import CustomerModelForm



class CustomerHandler(PermissionHanlder, StarkHandler):
    page_title = "客户"
    verify_similarity_list = ['title', 'shortname']
    search_list = ['title__icontains', 'owner__username__icontains']
    search_placeholder = '搜索 客户名'
    option_group = [
        Option(
            field="owner",
            control_list= [ each.nickname  for each in UserInfo.objects.filter(roles__title__in=["外销员",])]
        )]


    def get_follow_link_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return "跟单链接"
        else:
            link = self.reverse_url("get_follow_link", pk=obj.pk)
            link_btn = f"<a href='{link}' target='_blank'>获取链接</a>"
            return mark_safe(link_btn)

    fields_display = ['id', 'title', 'owner', get_follow_link_display]
    detail_fields_display = ['title','shortname', 'remark','email','owner', get_follow_link_display]

    def get_per_page(self):
        return 10

    def get_queryset_data(self, request, *args, **kwargs):
        if request.user.username == secret.ROOTUSER:
            return self.model_class.objects.all()
        if request.user.department == 8:
            return self.model_class.objects.all()
        elif request.user.department == 1:
            return self.model_class.objects.filter(owner=request.user)

    def get_extra_urls(self):
        return [
            url("^upload/$", self.wrapper(self.upload_customer), name=self.get_url_name('upload_customer')),
            url("^get_follow_link/(?P<pk>\d+)$", self.wrapper(self.get_follow_link), name=self.get_url_name('get_follow_link')),
        ]


    def get_model_form(self, handle_type=None):
        return  CustomerModelForm

    # 获取该客户的订单跟进表链接地址
    def get_follow_link(self, request,pk, *args, **kwargs):
        print("get_follow_link", pk)
        # 生成20位随机字符串
        customer_obj = self.model_class.objects.filter(pk=pk).first()
        if not customer_obj:
            return HttpResponse(f'customer number {pk} does NOT exist')
        if customer_obj.follow_id and len(customer_obj.follow_id) == 20:
            follow_id = customer_obj.follow_id
        else:
            follow_id = get_string(length=20)
            customer_obj.follow_id = follow_id
            customer_obj.save()
        link = reverse("stark:dipay_followorder_follow", kwargs={"follow_id":follow_id})
        link = secret.SITE_HEAD+link

        return render(request,'dipay/copy_customer_follow_link.html',locals())

    def upload_customer(self, request, *args, **kwargs):
        print(request.POST, request.FILES)
        if request.POST:
            customer_file = request.FILES.get('customer_file')
            print('yes upload', customer_file)
            # 存储文件
            file_path = os.path.join("media/", customer_file.name)

            # 存入media文件夹
            with open(file_path, "wb") as f:
                for line in customer_file:
                    f.write(line)

            # 读取excel文件
            excel_file = load_workbook(file_path)
            ws = excel_file.active
            count = 0

            # 遍历每行，获取每一行信息
            customer_list = []
            for row in ws.iter_rows(2):
                title = row[0].value
                owner = row[2].value
                print(title, owner)
                customer_obj = self.model_class(title=title, owner_id=owner, shortname=title)
                customer_list.append(customer_obj)
            self.model_class.objects.bulk_create(customer_list)
            return HttpResponse('upload successfully...')

        return render(request, 'dipay/upload_customer.html', locals())

    def get_render_form(self,form,*args, **kwargs):
        form.fields['owner'].initial = self.request.user
        return form