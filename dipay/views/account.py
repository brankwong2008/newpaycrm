from django.shortcuts import render, HttpResponse,redirect,reverse
from django.conf import settings
from django.utils.module_loading import import_string
from rbac.utils.common import gen_md5
from rbac.utils.permissions import init_permissions

MyUserInfo = import_string(settings.RBAC_USER_MODLE_CLASS)   # 使用import_string 增加代码的通用性

def login(request):
    if request.method == "GET":
        return render(request,"account/login.html")

    if request.method == "POST":
        username = request.POST.get("username")
        print('username', username)
        pwd = gen_md5(request.POST.get("pwd"))
        # user_obj = MyUserInfo.objects.filter(username=username,password=pwd).first()
        user_obj = MyUserInfo.objects.extra(where=['binary username=%s','binary password=%s'], params=[username,pwd]).first()

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

    roles_list = [ item.title for item in request.user.roles.all() ]
    if '财务' in roles_list:
        redirect_url = reverse('stark:dipay_inwardpay_list_account')

    if "货代" in roles_list:
        redirect_url = reverse('stark:dipay_charge_list_forwarder')

    if "国际部行政" in roles_list:
        redirect_url = reverse('stark:dipay_chance_list')

    return redirect(redirect_url)
