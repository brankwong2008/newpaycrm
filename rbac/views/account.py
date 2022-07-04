from django.views import View
from django.shortcuts import redirect,render,reverse,HttpResponse
from django.contrib import auth
from rbac.forms.forms import *
from rbac.utils.permissions import init_permissions


class LoginView(View):
    """登录"""

    def get(self, request):
        if request.path == '/logout/':
            auth.logout(request)
            return redirect("/login/")

        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        user = auth.authenticate(username=username, password=password)

        if user:
            auth.login(request, user)

            # 这个跨表查询有几个要点：
            # 1. user.roles 从ORM对象查其多对多query_set
            # 2. permission__isnull 跨表查询permission表，并过滤permissions为空的记录
            # 3. distinct() 去重

            # 初始化权限和菜单字典
            init_permissions(request,user)

            print(22222, request.session[settings.PERMISSION_KEY])

            return redirect("/index/")
        else:
            return render(request, "login.html", {"msg": "用户名密码错误"})


def register(request):
    if request.method == "GET":
        return render(request, "register.html")

    username = request.POST.get("username")
    password = request.POST.get("pwd")
    user = models.MyUser.objects.create_user(username=username, password=password)

    if user:
        return render(request, "register.html", {"msg": "注册成功"})

