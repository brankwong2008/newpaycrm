from rbac.forms.forms import *
from django.shortcuts import redirect,render,reverse,HttpResponse
from rbac import models
from rbac.utils.common import gen_md5

def user_list(request):
    """用户列表"""
    if request.method == "GET":
        users = models.MyUser.objects.all()
        return render(request, "role/user_list.html", locals())

def user_add(request):
    """添加用户"""
    if request.method == "GET":
        form = UserModelForm()
        handle = "添加用户"
        return render(request, "role/change.html", locals())
    if request.method == "POST":
        # 通过model form直接在Role表中创建一条记录
        form = UserModelForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("rbac:user_list"))
        else:
            return render(request, "role/change.html", locals())


def user_edit(request, pk):
    """编辑用户"""
    user_obj = models.MyUser.objects.filter(pk=pk).first()
    if request.method == "GET":
        if not user_obj:
            return HttpResponse("404错误")

        form = UserEditModelForm(instance=user_obj)
        handle = "编辑用户"
        return render(request, "role/change.html", locals())
    if request.method == "POST":
        # 通过model form直接更新关联ORM中MyUser表记录
        form = UserEditModelForm(instance=user_obj, data=request.POST)
        form.save()

        return redirect(reverse("rbac:user_list"))

def user_del(request, pk):
    """删除用户"""
    if request.method == "GET":
        handle = "删除用户"
        cancel = reverse("rbac:user_list")
        return render(request, 'role/delete.html', locals())

    if request.method == "POST":
        user_obj = models.MyUser.objects.filter(pk=pk).first()
        if user_obj:
            user_obj.delete()
            msg = "删除成功"
            return redirect(reverse('rbac:user_list'))
        else:
            return HttpResponse(f"删除{pk}的记录不存在")


def user_reset_pwd(request, pk):
    """用户密码重置"""
    user_obj = models.MyUser.objects.filter(pk=pk).first()
    if request.method == "GET":
        if not user_obj:
            return HttpResponse("404错误")

        form = UserResetPwdModelForm()
        handle = "重置密码"
        return render(request, "role/change.html", locals())

    if request.method == "POST":
        # 通过model form直接更新关联ORM中MyUser表记录
        form = UserResetPwdModelForm(instance=user_obj,data=request.POST)

        if form.is_valid():
            pwd = form.cleaned_data.get("password")
            print("pwd", pwd, user_obj)
            user_obj.password = gen_md5(pwd)
            user_obj.save()

            return redirect(reverse("rbac:user_list"))
        else:
            return render(request, "role/change.html", locals())

