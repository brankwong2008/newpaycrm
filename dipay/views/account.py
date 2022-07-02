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
        print(username,pwd,user_obj)
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

    redirect_url = reverse('stark:dipay_inwardpay_list')
    return redirect(redirect_url)
#
# from django import forms
# class BookAddForm(forms.ModelForm):
#     class Meta:
#         model = models.Book
#         fields = ['title',]
#
# def book_create(request):
#
#     form =  BookAddForm(request.POST or None)
#     print(request.POST)
#     if form.is_valid():
#         book_obj = form.save()
#         return HttpResponse("<script> opener.closePopup(window,'%s','%s','#id_book') </script>"
#                             % (book_obj.pk, book_obj))
#
#     return render(request,'dipay/create_record.html',locals())
