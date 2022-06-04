from rbac.forms.forms import *
from django.shortcuts import redirect,render
from rbac import models
from rbac.utils.urls import memory_reverse


def menu_list(request):
    """角色列表"""
    if request.method == "GET":
        menus = models.Menu.objects.all()
        return render(request, "role/menu_list.html", locals())


def menu_add(request):
    handle = "添加一级菜单"
    if request.method == "GET":
        form = MenuAddModelForm()
        return render(request, "role/change_menu.html", locals())
    if request.method == "POST":
        form = MenuAddModelForm(data=request.POST)
        form.save()

        return redirect(memory_reverse(request,"rbac:permission_list"))

def menu_edit(request, pk):
    handle = "编辑一级菜单"
    menu_obj = models.Menu.objects.filter(pk=pk).first()

    if request.method == "GET":
        if menu_obj:
            form = MenuAddModelForm(instance=menu_obj)
        return render(request, "role/change.html", locals())

    if request.method == "POST":
        form = MenuAddModelForm(instance= menu_obj, data=request.POST)
        form.save()

        return redirect(memory_reverse(request,"rbac:permission_list"))


def menu_del(request, pk):
    handle = "删除一级菜单"
    cancel = memory_reverse(request,"rbac:permission_list")

    if request.method == "GET":
        return render(request, "role/delete.html", locals())

    if request.method == "POST":
        second_menu_exists = models.Permission.objects.filter(menu_id=pk)
        if second_menu_exists:
            msg = "存在关联的权限，无法删除"
            return render(request, "role/delete.html", locals())
        else:
            to_delete_menu = models.Menu.objects.filter(pk=pk).first()
            if not to_delete_menu:
                msg = "要删除的菜单不存在"
                return render(request, "role/delete.html", locals())

            to_delete_menu.delete()
            return redirect(cancel)


def second_menu_add(request):
    handle = "添加二级菜单"
    if request.method == "GET":
        form = SecondMenuModelForm()
        return render(request, "role/change.html", locals())
    if request.method == "POST":
        form = SecondMenuModelForm(data=request.POST)
        form.save()

        return redirect(memory_reverse(request,"rbac:permission_list"))

def second_menu_edit(request, pk):
    handle = "编辑二级菜单"
    menu_obj = models.Permission.objects.filter(pk=pk).first()

    if request.method == "GET":
        if menu_obj:
            form = SecondMenuModelForm(instance=menu_obj)
        return render(request, "role/change.html", locals())

    if request.method == "POST":
        form = SecondMenuModelForm(instance= menu_obj, data=request.POST)
        form.save()

        return redirect(memory_reverse(request,"rbac:permission_list"))


def second_menu_del(request, pk):
    handle = "删除二级级菜单"
    cancel = memory_reverse(request,"rbac:permission_list")

    if request.method == "GET":
        return render(request, "role/delete.html", locals())

    if request.method == "POST":
        permission_exists = models.Permission.objects.filter(parent_id=pk)
        if permission_exists:
            msg = "存在关联的权限，无法删除"
            return render(request, "role/delete.html", locals())
        else:
            to_delete_second_menu = models.Permission.objects.filter(pk=pk).first()
            if not to_delete_second_menu:
                msg = "要删除的菜单不存在"
                return render(request, "role/delete.html", locals())

            to_delete_second_menu.delete()

            return redirect(cancel)
