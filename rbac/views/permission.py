
from rbac.forms.forms import *
from django.conf import settings
from django.shortcuts import redirect,render,reverse,HttpResponse
from django.forms import formset_factory,modelformset_factory
from rbac import models
from rbac.utils.urls import memory_reverse
from django.utils.module_loading import import_string

RbacUserInfo = import_string(settings.RBAC_USER_MODLE_CLASS)

def permission_list(request):
    menus = models.Menu.objects.all()
    mid = request.GET.get('mid')
    sid = request.GET.get('sid')

    mid_exists = models.Menu.objects.filter(pk=mid).exists()
    if not mid_exists:
        mid = None
    sid_exists = models.Permission.objects.filter(pk=sid)
    if not sid_exists:
        sid = None

    if mid:
        second_menus = models.Permission.objects.filter(menu_id=mid)
    if sid:
        permissions = models.Permission.objects.filter(parent_id=sid)

    return render(request, "permission_list.html", locals())


def permission_add(request,sid):
    handle = "添加权限"
    if request.method == "GET":
        form = PermissionModelForm()
        return render(request, "role/change.html", locals())
    if request.method == "POST":
        form = PermissionModelForm(data=request.POST)
        if form.is_valid():
            second_menu_obj = models.Permission.objects.filter(pk=sid).first()
            if not second_menu_obj:
                return HttpResponse("二级菜单不存在")

            form.instance.parent = second_menu_obj
            form.save()
            return redirect(memory_reverse(request, "rbac:permission_list"))
        else:
            return HttpResponse("权限新建失败")

def permission_edit(request, pk):
    handle = "编辑权限"
    permission_obj = models.Permission.objects.filter(pk=pk).first()

    if request.method == "GET":
        if permission_obj:
            form = PermissionModelForm(instance=permission_obj)
        return render(request, "role/change.html", locals())

    if request.method == "POST":
        form = PermissionModelForm(instance= permission_obj, data=request.POST)
        form.save()

        return redirect(memory_reverse(request,"rbac:permission_list"))

def permission_del(request, pk):
    handle = "删除权限"
    cancel = memory_reverse(request,"rbac:permission_list")

    if request.method == "GET":
        return render(request, "role/delete.html", locals())

    if request.method == "POST":

        to_delete_permission = models.Permission.objects.filter(pk=pk).first()
        if not to_delete_permission:
            msg = "要删除的权限不存在"
            return render(request, "role/delete.html", locals())

        to_delete_permission.delete()
        return redirect(cancel)


# def permission_mult_add(request,sid):
#     """ 按modelformset_factory方式的添加权限 """
#
#     Formset_class = modelformset_factory(model=models.Permission,form=PermissionMultAddModelForm,extra=2)
#
#     if request.method == "GET":
#         queryset = models.Permission.objects.filter(pk=None)
#         formset = Formset_class(queryset=queryset)
#         return render(request,"permission_mult_add.html", {"formset":formset})
#
#     if request.method == "POST":
#         formset = Formset_class(data=request.POST)
#
#         if formset.is_valid():
#             valid_data = formset.cleaned_data
#             flag = True
#             for i in range(0,formset.total_form_count()):
#                 item = valid_data[i]
#                 if not item:
#                     continue
#                 new_permission = models.Permission(**item)
#
#                 try:
#                     new_permission.validate_unique()
#                     new_permission.save()
#                 except Exception as e:
#                     formset.errors[i].update(e)
#                     flag = False
#             if flag:
#                 return HttpResponse("批量添加成功")
#
#         return render(request,"permission_mult_add.html", {"formset":formset})

def permission_mult_edit(request,sid):
    """ 批量编辑权限"""
    Formset_class = formset_factory(PermissionMultEditModelForm,extra=0)

    if request.method == "GET":
        initial = models.Permission.objects.filter(parent_id=sid).values("id","title","urls","name","parent_id")
        # initial参数接受的是一个字典，其键必须与forms里面的字段同名
        formset = Formset_class(initial=initial)
        return render(request,"permission_mult_edit.html", {"formset":formset})

    if request.method == "POST":
        formset = Formset_class(data=request.POST)

        if formset.is_valid():
            valid_data = formset.cleaned_data
            flag = True
            for i in range(0,formset.total_form_count()):
                row = valid_data[i]

                # 只能采用save方法，而不能用objects.filter().update()方法，因为这不会触发unique约束机制
                permission_id = row.pop('id')
                permission_obj = models.Permission.objects.filter(pk=permission_id).first()

                for key,value in row.items():
                    # setattr方法是一种反射方法：以字符串方式对发对象的属性进行操作的方式
                    setattr(permission_obj,key,value)
                try:
                    # orm的validate_unique()方法可以检查唯一索引约束，如违反则报错
                    permission_obj.validate_unique()
                    permission_obj.save()
                except Exception as e:
                    # formset的错误字典和form的错误字典类似，只不过是列表里面套字典。所以可以用字典的update方法
                    formset.errors[i].update(e)
                    flag = False
            if flag:
                return HttpResponse("批量修改成功")

        return render(request,"permission_mult_edit.html", {"formset":formset})


from django.urls import URLPattern, URLResolver
def get_all_url(pre_namespace,pre_url,urlpatterns,url_dict):
    """
    递归获取项目中所有url
    :param pre_namespace:
    :param pre_url:
    :param urlpattern:
    :param url_dict:
    :return:
    """
    def check_exclude_url(url):
        """检查url是否在排除名单里面"""
        exclude_list = settings.AUTO_DISCOVER_EXCLUDE
        for regex in exclude_list:
            if re.match(regex,url):
                return True

    for item in urlpatterns:
        if isinstance(item, URLPattern):
            if not item.name:
                continue

            name =  "%s:%s" % (pre_namespace,item.name) if pre_namespace else item.name

            url = pre_url+ item.pattern.regex.pattern
            url = url.replace("^","").replace("$","")

            if check_exclude_url(url):
                continue
            url_dict[name] = {"name":name,"urls":url}

        if isinstance(item,URLResolver):
            if pre_namespace:
                if item.namespace:
                    namespace ="{}:{}".format(pre_namespace,item.namespace)
                else:
                    namespace = pre_namespace
            else:
                if item.namespace:
                    namespace = item.namespace
                else:
                    namespace = None
            if item.pattern:
                url = pre_url+item.pattern.regex.pattern
            else:
                url = pre_url
            get_all_url(namespace,url, item.url_patterns,url_dict)

    return url_dict

def auto_crawle_permission(request):
    """ 自动收集项目中所有的url，name和title"""
    add_formset_class = formset_factory(AutoPermissionAddModelForm, extra=0)
    update_formset_class = formset_factory(AutoPermissionEditModelForm, extra=0)

    post_type = request.GET.get("type")
    add_formset_list = None
    to_update_name_list = None
    to_update_url_list = None

    # 处理批量添加提交的数据
    if request.method == "POST" and post_type == "add":
        formset = add_formset_class(data=request.POST)

        if formset.is_valid():
            row_data = formset.cleaned_data
            failure = False
            for i in range(0,formset.total_form_count()):
                new_obj = models.Permission(**row_data[i])
                try:
                    new_obj.validate_unique()
                    new_obj.save()
                except Exception as e:
                    print('exception ....',e,type(e))
                    formset.errors[i].update(e)
                    failure = True
            if failure:
                add_formset_list = formset
        else:
            add_formset_list = formset

    # 批量更新urlname,提交的数据
    if request.method == "POST" and post_type == "update_urlname":
        formset = update_formset_class(data=request.POST)

        if formset.is_valid():
            row_data = formset.cleaned_data
            failure = False
            for i in range(0, formset.total_form_count()):
                pk = row_data[i].pop("id")
                new_obj = models.Permission.objects.filter(pk=pk).first()

                try:
                    # new_obj.title = row_data[i]["title"]
                    # new_obj.urls = row_data[i]["urls"]
                    # new_obj.name = row_data[i]["name"]
                    # new_obj.menu_id = row_data[i]["menu_id"]
                    # new_obj.parent_id = row_data[i]["parent_id"]
                    # 采用反射来写上面的五行，省点纸
                    for key,value in row_data[i].items():
                        setattr(new_obj,key,value)

                    new_obj.validate_unique()
                    new_obj.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    failure = True
            if failure:
                to_update_name_list = formset

        else:
            to_update_name_list = formset

    # 批量更新url,提交的数据
    if request.method == "POST" and post_type == "update_url":
        formset = update_formset_class(data=request.POST)

        if formset.is_valid():
            row_data = formset.cleaned_data
            failure = False
            for i in range(0, formset.total_form_count()):
                pk = row_data[i].pop("id")
                new_obj = models.Permission.objects.filter(pk=pk).first()
                try:
                    new_obj.title = row_data[i]["title"]
                    new_obj.urls = row_data[i]["urls"]
                    new_obj.name = row_data[i]["name"]
                    new_obj.menu_id = row_data[i]["menu_id"]
                    new_obj.parent_id = row_data[i]["parent_id"]
                    new_obj.validate_unique()
                    new_obj.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    failure = True
            if failure:
                to_update_url_list = formset

        else:
            to_update_url_list = formset

    # 导入跟路由模块
    from django.utils.module_loading import import_string
    root_url_md = import_string(settings.ROOT_URLCONF)
    url_dict = {}

    # 调用递归函数获取项目中所有的urls
    all_urls = get_all_url(None,'/',root_url_md.urlpatterns,url_dict)
    """ all_urls = { 'rbac：role_list'：
                               { 'name': 'rbac:role_list', 
                                'url':  '/rbac/role/list/',}
                    'rbac:role_add':
                            { 'name': 'rbac:role_add', 
                                'url':  '/rbac/role/add/',}
    }    
    """

    # 项目中所有的权限name的集合
    project_urlname_set = set(all_urls.keys())

    # 以权限为键以权限name为值的反向字典
    project_url_dict = {item['urls']:item['name'] for item in all_urls.values()}

    # 从数据库Permission表中获取所有的权限，做成字典{name:{name:"", title:"", url:"", menu_id:"", parent_id:""}, }
    permission_url_dict = {}

    #数据库中权限表的权限name集合
    permission_urlname_set = set()
    to_update_url_dict = {}
    to_update_url_set = set()
    to_update_menu_n_pid_list = []

    for item in models.Permission.objects.values("id","name","title","urls","menu_id","parent_id"):
        permission_urlname_set.add(item["name"])
        permission_url_dict[item['name']]= item
        # 如果权限表中的name存在于项目中，但是url不一样，需要更新数据中的url
        if item['name'] in project_urlname_set and item['urls'] != all_urls[item['name']]['urls']:
            item['urls'] = f"数据库和项目中的url不一致-{all_urls[item['name']]['urls']}"
            to_update_url_set.add(item['name'])
        # 如果权限表中的url与项目中一致，但是权限name不一样，需要更新数据库或者项目中的权限名
        if item['urls'] in project_url_dict and item['name'] != project_url_dict[item['urls']]:
            item['name'] = "数据库和项目中的name不一致"
            to_update_url_dict[item['urls']] = item
        if not item['menu_id'] and not item['parent_id']:
            to_update_menu_n_pid_list.append(item)


    ##### 使用自动获取的项目中的url路由信息批量更新数据库

    ## 1. 需要添加的set集合: 项目中有，数据库没有的（使用差集方法，可以直接获得需要添加的权限name集合）
    to_add_url_set = project_urlname_set - permission_urlname_set

    # 获取需要添加的列表，数据格式 [{'name':'rbac:role_list','url':'/rbac/role/list/'},{},{}], 添加列表只需要这两个数据
    to_add_url_list = [ item for name,item in all_urls.items() if name in to_add_url_set]
    if add_formset_list is None:
        add_formset_list = add_formset_class(initial= to_add_url_list)

    # 2. 需要删除的set集合: 数据库中有，项目中没有的
    to_del_url_set = permission_urlname_set - project_urlname_set
    to_del_url_list = [item for name,item in permission_url_dict.items() if name in to_del_url_set]

    # 3. 需要更新的set集合：数据库和项目中name相同的，url不相同的
    # to_update_url_set = permission_urlname_set & project_urlname_set
    if to_update_url_list is None:
        to_update_url_list = update_formset_class(initial=[item for name,item in permission_url_dict.items() if name in to_update_url_set])

    # 4. 需要更新的set集合： 数据库和项目中url相同，而name不同的, 或者一级菜单和二级菜单字段皆为空的记录
    if to_update_name_list is None:
        to_update_name_list = update_formset_class(initial =[ item for name,item in to_update_url_dict.items()])

    # 5. mid和pid都为空的权限集合
    to_update_menu_n_pid_list = update_formset_class(initial= to_update_menu_n_pid_list)

    return render(request,"auto_permission_update.html",{
        "add_formset_list":add_formset_list,
        "to_update_name_list":to_update_name_list,
        "to_update_url_list":to_update_url_list,
        "to_del_url_list":to_del_url_list,
        "to_update_menu_n_pid_list":to_update_menu_n_pid_list,

    })


def multi_permission_del(request,pk):
    handle = "删除批量权限"
    cancel = reverse("rbac:auto_crawle_permission")

    if request.method == "GET":
        return render(request, "role/delete.html", locals())

    if request.method == "POST":
        permission_obj = models.Permission.objects.filter(pk=pk).first()
        if not permission_obj:
            msg = "要删除的权限不存在"
            return render(request, "role/delete.html", locals())
        else:
            permission_obj.delete()
            return redirect(reverse("rbac:auto_crawle_permission"))


def permission_distribute(request):
    uid = request.GET.get("uid")
    rid = request.GET.get("rid")

    if request.method == "POST":
        post_type = request.GET.get("type") or request.POST.get("type")

        if post_type == "add_role_to_user":
            rid_list = request.POST.getlist("rid")
            print("rid_list",rid_list)
            user = RbacUserInfo.objects.filter(pk=uid).first()
            if user:
                user.roles.set(rid_list)


        if post_type == "add_permission_to_role":

            permission_id_list = request.POST.getlist("p_id")
            role = models.Role.objects.filter(pk=rid).first()
            print(role)
            print(permission_id_list)
            if role:
                role.permissions.set(permission_id_list)

    users = RbacUserInfo.objects.all()
    roles = models.Role.objects.all()

    if uid:
        role_queryset = RbacUserInfo.objects.filter(pk=uid).first().roles.all()
        role_list =[row.id for row in role_queryset]
        has_permission_dict ={}
        for role in role_queryset:
            has_permission_dict.update({ item.id:None for item in role.permissions.all()})

    if rid:
        role_obj = models.Role.objects.filter(pk=rid).first()
        if role_obj:
            has_permission_dict = { item.id:None for item in role_obj.permissions.all()}


    permission_dict = {}
    for menu in models.Menu.objects.all():
        permission_dict[menu.id]={"title": menu.title,"children":[]}
        queryset = models.Permission.objects.filter(menu=menu)
        for i in range(0, queryset.count()):
            permission_dict[menu.id]['children'].append({"title":queryset[i].title,"id":queryset[i].id,"children":[]},)
            permission_dict[menu.id]["children"][i]["children"]=[{"title":permission.title,"id":permission.id} for permission in models.Permission.objects.filter(parent=queryset[i]) ]

    permission_list = permission_dict.values()

    return render(request,"permission_distribute.html",locals())



