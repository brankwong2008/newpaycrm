from rbac.forms.forms import *
from django.shortcuts import redirect,render,reverse,HttpResponse
from rbac import models

def role_list(request):
    """角色列表"""
    if request.method == "GET":
        roles = models.Role.objects.all()
        return render(request, "role/role_list.html", locals())


def role_add(request):
    """添加角色"""
    if request.method == "GET":
        form = RoleModelForm()
        handle = "添加角色"
        return render(request, "role/change.html", locals())
    if request.method == "POST":
        # 通过model form直接在Role表中创建一条记录
        form = RoleModelForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("rbac:role_list"))
        else:
            return render(request, "role/change.html", locals())


def role_edit(request, pk):
    """编辑角色"""
    role_obj = models.Role.objects.filter(pk=pk).first()
    if request.method == "GET":
        if not role_obj:
            return HttpResponse("404错误")

        form = RoleModelForm(instance=role_obj)
        handle = "编辑角色"
        return render(request, "role/change.html", locals())
    if request.method == "POST":
        # 通过model form直接更新关联ORM中Role表记录
        form = RoleModelForm(instance=role_obj, data=request.POST)
        form.save()

        return redirect(reverse("rbac:role_list"))


def role_del(request, pk):
    """删除角色"""
    if request.method == "GET":
        handle = "删除角色"
        cancel = reverse("rbac:role_list")

        return render(request, 'role/delete.html', locals())

    if request.method == "POST":
        role = models.Role.objects.filter(pk=pk).first()
        if role:
            role.delete()
            msg = "删除成功"
            roles = models.Role.objects.all()
            return render(request, "role/role_list.html", locals())
        else:
            return HttpResponse(f"删除{pk}的记录不存在")
