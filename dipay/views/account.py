from django.shortcuts import render, HttpResponse,redirect,reverse
from django.conf import settings
from django.utils.module_loading import import_string
from stark.utils.common import gen_md5
from django.utils.safestring import mark_safe
from rbac.utils.permissions import init_permissions
from dipay import models

MyUserInfo = import_string(settings.RBAC_USER_MODLE_CLASS)   # 使用import_string 增加代码的通用性

def login(request):
    if request.method == "GET":
        return render(request,"account/login.html")

    if request.method == "POST":
        username = request.POST.get("username")
        pwd = gen_md5(request.POST.get("pwd"))
        user_obj = MyUserInfo.objects.filter(username=username,password=pwd).first()
        if user_obj:
            request.session[settings.LOGIN_KEY] = {"username":user_obj.username, "id":user_obj.id}
            request.user = user_obj
            init_permissions(request,user_obj)

            return redirect(reverse("index"))
        else:
            return render(request,"account/login.html",{"msg":"用户名密码错误"})

def logout(request):
    del request.session[settings.LOGIN_KEY]
    url = reverse("login")
    return redirect(url)


def index(request):
    # print(888888, request.navi_list)
    payment_header_list=['日期','金额','付款人','收款银行','确认状态','关联状态']
    payment_queryset = models.Inwardpay.objects.filter(status=0)
    payment_data_list = []

    for obj in payment_queryset:
        create_date =obj.create_date.strftime('%Y-%m-%d')
        got_amount = '%s %s' % ( obj.currency.icon , obj.got_amount)
        payer = obj.payer.title[:20]
        bank = obj.bank.title
        if obj.confirm_status == 0:
            confirm_url = reverse('stark:dipay_inwardpay_confirm_pay',kwargs=dict(inwardpay_id=obj.pk))
            confirm_status = mark_safe("<a href='%s'> 请认领 </a>" % confirm_url)
            status = '待关联'
        if obj.confirm_status == 1:
            confirm_url = reverse('stark:dipay_inwardpay_confirm_pay', kwargs=dict(inwardpay_id=obj.pk))
            confirm_status = '已认领待确认'
            relate2order_url =  reverse('stark:dipay_inwardpay_relate2order',
                                        kwargs=dict(inwardpay_id=obj.pk,payer_id=obj.payer_id))
            status = mark_safe("<a href='%s'> 待关联 </a>" % relate2order_url )
        else:
            confirm_status = '跟单确认'
            status = '已关联'

        payment_data_list.append((create_date,got_amount,payer,bank,confirm_status, status))

    return render(request,"account/index.html",locals())


from django import forms
class BookAddForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['title',]

def book_create(request):

    form =  BookAddForm(request.POST or None)
    print(request.POST)
    if form.is_valid():
        book_obj = form.save()
        return HttpResponse("<script> opener.closePopup(window,'%s','%s','#id_book') </script>"
                            % (book_obj.pk, book_obj))

    return render(request,'dipay/create_record.html',locals())
