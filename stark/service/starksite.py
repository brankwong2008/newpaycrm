from django.conf.urls import url
from django.db.models import QuerySet
from django.http import QueryDict
from django.db.models import Q,ForeignKey,ManyToManyField
import functools
from django.forms import ModelForm
from django import forms
from django.utils.safestring import mark_safe
from stark.service.pagination import Pagination
from types import FunctionType,MethodType
from django.shortcuts import HttpResponse,render,redirect,reverse
from dipay.forms.forms import StarkForm

class Option:
    def __init__(self,field,filter_param=None,is_multi = False,default=None):
        """
        封装choice或者foreign key字段关联的数据源，在前端展示进行组合筛选
        :param field: 字段名
        :param filter_param: 原始数据筛选条件
        :param is_multi: 是否支持多选
        """
        self.field = field
        self.filter_param = filter_param if filter_param else {}
        self.is_multi = is_multi
        self.is_choice = False
        self.default = default

    class RenderData:
        def __init__(self, data,field,verbose_name,query_dict,option):
            """
            初始化组合筛选的页面显示html的基本信息
            :param data: 筛选字段关联的数据源，可以是queryset，或者是choices
            :param field: 筛选字段名
            :param verbose_name: 筛选字段显示名称
            :param query_dict: 地址栏里面的筛选参数
            :param option: option对象
            """
            self.data = data
            self.field = field
            self.verbose_name = verbose_name
            self.query_dict = query_dict
            self.option= option

        def __iter__(self):

            yield self.verbose_name
            yield '<div class="others">'
            query_dict = self.query_dict.copy()
            query_dict._mutable = True

            # 这句话什么意思，为什么删除键值，因为全部按钮的url里面的筛选条件是空
            res = query_dict.get(self.field,None)
            default_flag = False
            # 如果筛选是全部，则该键值为空
            if not res:
                yield '<a href="?%s" class="active">全部</a>' % (query_dict.urlencode())
            else:
                query_dict.pop(self.option.field)
                yield '<a href="?%s">全部</a>' % (query_dict.urlencode())


            for item in self.data:
                query_dict = self.query_dict.copy()
                # val_list用户选择的筛选值列表
                val_list = query_dict.getlist(self.field)
                if default_flag:
                    val_list.append(self.option.default)
                query_dict._mutable = True

                text = self.option.get_text(item)
                val = self.option.get_value(item)
                if not self.option.is_multi:
                    query_dict[self.field] = val
                    if val in val_list:
                        is_active = "active"
                        query_dict.pop(self.field)
                    else:
                        is_active = ""
                else:
                    if val not in val_list:
                        print(55555,val,type(val),val_list)
                        val_list.append(val)
                        is_active = ""
                    else:
                        val_list.remove(val)
                        is_active = "active"
                    print(1233454, 'val_list',val_list)

                    # 给每个筛选按钮定制url，要考虑下次点击之后的效果
                    query_dict.setlist(self.field,val_list)

                yield '<a href="?%s" class="%s">%s</a>' % (query_dict.urlencode(), is_active,text)

            yield '</div>'

    def get_data(self,model_class,query_dict):
        field_obj = model_class._meta.get_field(self.field)
        verbose_name = field_obj.verbose_name


        if isinstance(field_obj, ForeignKey) or isinstance(field_obj, ManyToManyField):
            temp_model = field_obj.related_model
            return self.RenderData(temp_model.objects.filter(**self.filter_param),self.field,verbose_name,query_dict,self)
        else:
            self.is_choice = True
            return  self.RenderData(field_obj.choices,self.field,verbose_name,query_dict,self)

    # 获取字段的每个值的显示名称
    def get_text(self,field_obj):
        if self.is_choice:
            return field_obj[1]
        else:
            return str(field_obj)

    # 获取字段每个名称对应的数据库里面的值
    def get_value(self,field_obj):
        if self.is_choice:
            return str(field_obj[0])
        else:
            return str(field_obj.pk)

class StarkHandler(object):
    edit_list_template = None  # 编辑页面模板
    add_list_template = None   # 添加页面模板
    del_list_template = None   # 删除页面模板
    show_list_template = None  # 显示页面模板
    fields_display = []    # 显示的列字段
    tabs = None     # 标签导航
    has_add_btn = True
    detail_fields_display = '__all__'
    detail_extra_btn = None    # 详情页显示的额外按钮
    # 自定义列表，外键字段快速添加数据，在前端显示加号
    popup_list = []
    search_placeholder = ''

    def __init__(self, site, model_class,prev):
        self.site = site
        self.model_class = model_class
        self.app_label = model_class._meta.app_label
        self.model_name = model_class._meta.model_name
        self.prev = prev
        self.namespace = site.namespace

    # 用于控制对某一列数据的编辑权限
    def get_editable(self,field):
        # 返回true 说明可编辑
        return True

    def get_fields_display(self,request,*args,**kwargs):
        val = []
        val.extend(self.fields_display)
        if self.fields_display:
            val.extend([self.edit_del_display,])
        return val

    def get_extra_fields_display(self,request,*args,**kwargs):
        return []

    def get_detail_extra_btn(self,request,pk,*args,**kwargs):
        return self.detail_extra_btn

    def add_btn_display(self,request,*args,**kwargs):
        if self.has_add_btn:
            add_url = self.reverse_add_url(*args,**kwargs)
            return "<a href='%s' class='btn btn-primary add-record'> 添加 </a>" % (add_url)
        else:
            return None

    def get_model_form(self,type=None):
        class DynamicModelForm(StarkForm):
            class Meta:
                model = self.model_class
                fields = "__all__"
        return DynamicModelForm


    def get_per_page(self):
        return 5


    order_by_list = []

    # 模糊搜索框   search_list = ['title__contains', 'id__lt']
    search_list = []

    # 组合筛选区域
    option_group = []

    batch_process_list = []

    def get_order_by_list(self):
        if self.order_by_list:
            return self.order_by_list
        else:
            return ["-id",]

    def get_url_filter(self):
        """ 获取url中携带的查询筛选条件"""
        filter_condition = dict()
        query_dict = self.request.GET
        for option in self.option_group:
            if option.is_multi:
                if query_dict.getlist(option.field):
                    filter_condition["%s__in" % option.field] = query_dict.getlist(option.field)
            else:
                if query_dict.get(option.field):
                    filter_condition[option.field]= query_dict.get(option.field)

        return filter_condition

    def get_edit_obj(self,request,pk,*args,**kwargs):
        return self.model_class.objects.filter(pk=pk).first()

    def get_del_obj(self,request,pk,*args,**kwargs):
        return self.model_class.objects.filter(pk=pk).first()

    def save_form(self,form,request,is_update=False,*args, **kwargs):
        form.save()

    def get_queryset_data(self,request,is_search=None,*args,**kwargs):
        return self.model_class.objects.all()

    def get_tabs(self,request,*args,**kwargs):
        return self.tabs

    # 列表页面
    def show_list(self, request,*args,**kwargs):

        fields_display = self.get_fields_display(request,*args,**kwargs)
        header_list = []
        data_list = []
        tabs = self.get_tabs(request,*args,**kwargs)

        ############## 1. 批量删除或者初始化 ###############

        if self.batch_process_list:
            batch_process_dict = {}    # {"batch_del":"批量删除"，"batch_init":"批量初始化" }
            for func in self.batch_process_list:
                batch_process_dict[func.__name__] = func.text
        else:
            batch_process_dict = None

        if request.method == "POST":
            print(request.POST)
            func_name = request.POST.get("handle_type")
            if func_name in batch_process_dict:
                func = getattr(self,func_name)
                result = func(request,*args,**kwargs)
                return result

        searched_queryset = self.get_queryset_data(request,*args,**kwargs)

        ############## 1. 添加按钮############
        add_btn = self.add_btn_display(request, *args, **kwargs)
        print('add btn',add_btn)

        # 如果是空表或者数据结果为空，按空表方式显示
        if not searched_queryset:
            show_template = self.show_list_template or "stark/show_list.html"
            header_list.extend([self.model_name, "操作"])
            data_list = [[],] #  二维列表存储表体内容
            print('show_template',show_template)
            return render(request, show_template, locals())


        ############## 1. 模糊搜索 ###############
        search_list = self.search_list

        # 模糊搜索框的 placeholder
        search_placeholder = self.search_placeholder

        user_query = self.request.GET.get("q","")

        conn = Q()
        conn.connector = "OR"
        if user_query:
            for item in search_list:
                # 使用ORM的Q函数来构造OR条件的查询
                conn.children.append((item, user_query.strip()))
            # 搜索专门指定数据集，比显示的略宽一些
            searched_queryset = self.get_queryset_data(request,is_search=True).filter(conn)

        ###  获取url中的过滤条件 #############   ?depart=1&gender=2&page=123&q=999
        filter_condition = self.get_url_filter()
        print('filtercondition:', filter_condition)


        ############## 1. 组合筛选的区域显示 ###############
        if self.option_group:
            option_group_dict = {}
            group_filter = {}
            for option_obj in self.option_group:
                # print(1010101, field_filter_exists, option_obj.field,option_obj.default)
                # 这个字典的键值是可迭代对象，给出页面需要的html标签
                option_group_dict[option_obj.field] = option_obj.get_data(self.model_class,request.GET)

        """
        基本原理：
        把model里面外键字段和choice字段的内容找到，作为关键字标签显示在页面上
        点击这些标签，把字段和内容作为以get关键字参数传递到后台
        根据这些组合条件筛选数据库，然后展示在前台  
        """

        # 根据以上过滤条件过滤数据

        searched_queryset = searched_queryset.filter(**filter_condition)

        # 在由用户定义要进行筛选的字段 option_group = [option_obj, ]
        # 在option中内置方法，获取对应字段的关联值，yield给调用者

        # 前端进行显示，并把value值包含到标签中

        ############## 1. 排序 ###############
        order_by_list = self.get_order_by_list()
        ordered_queryset = searched_queryset.order_by(*order_by_list)


        ############## 1. 分页 ###############
        query_params = request.GET.copy()
        query_params._mutable = True
        #
        # print("ordered_queryset.count()",ordered_queryset.count())
        # print('request.GET.get("page")',request.GET.get("page"))

        pager = Pagination(
            current_page=request.GET.get("page"),
            all_count=ordered_queryset.count(),
            base_url=request.path,
            query_params=query_params,
            per_page=self.get_per_page(),
        )

        """
           def __init__(self, current_page, all_count, base_url, query_params, per_page=20, pager_page_count=11):
        分页初始化
        :param current_page: 当前页码
        :param per_page: 每页显示数据条数
        :param all_count: 数据库中总条数
        :param base_url: 基础URL
        :param query_params: QueryDict对象，内部含所有当前URL的原条件
        :param pager_page_count: 页面上最多显示的页码数量
        """

        data_query_set = ordered_queryset[pager.start:pager.end]


        ############## 1. 定制显示列 ############
        if fields_display:
            # 处理表头
            for k in fields_display:

                if isinstance(k,FunctionType):
                    verbose_name = k(self,obj=None,is_header=True,*args,**kwargs)
                elif isinstance(k,MethodType):
                    verbose_name = k(obj=None, is_header=True,*args,**kwargs)
                else:
                    verbose_name = self.model_class._meta.get_field(k).verbose_name
                header_list.append(verbose_name)

            # 处理表体 方式一
            for row in data_query_set:
                row_list = []
                for key in fields_display:
                    if isinstance(key,FunctionType):
                        field_val = key(self, obj = row, is_header = False,*args,**kwargs)
                    elif isinstance(key,MethodType):
                        field_val = key(obj=row, is_header=False,*args,**kwargs)
                    else:
                        field_val = getattr(row, key)
                    row_list.append(field_val)
                data_list.append(row_list)
                # 方法二
                # data_list = self.model_class.objects.values_list(*self.fields_display)

        else:
            header_list.extend([self.model_name,"操作"])
            data_list = [ [str(row), self.edit_del_display(row,False,*args,**kwargs)] for row in data_query_set]

        #
        show_template = self.show_list_template or "stark/show_list.html"

        return render(request,show_template,locals())

    # 新增一条记录
    def add_list(self, request,*args,**kwargs):
        if request.method =="GET":
            form = self.get_model_form("add")()

            return render(request,self.add_list_template or "stark/change_list.html",locals())

        if request.method == "POST":
            form = self.get_model_form("add")(data = request.POST)

            if form.is_valid():
                result = self.save_form(form,request,False,*args, **kwargs)

                return result or redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, self.add_list_template or "stark/change_list.html", locals())

    # 编辑一条记录
    def edit_list(self, request, pk, *args,**kwargs):
        form_class = self.get_model_form("edit")
        edit_obj = self.get_edit_obj(request,pk,*args,**kwargs)

        if not edit_obj:
            return HttpResponse("编辑的记录不存在")

        if request.method == "GET":
            form = form_class(instance=edit_obj)
            back_url = self.reverse_list_url()
            namespace = self.namespace
            app_label = self.app_label
            # 自定义列表，外键字段快速添加数据，在前端显示加号
            popup_list = self.popup_list
            return render(request,self.edit_list_template or "stark/change_list.html",locals())

        if request.method == "POST":
            form = form_class(instance=edit_obj,data=request.POST)
            if request.FILES:
                form = form_class(request.POST,request.FILES,instance=edit_obj)
            if form.is_valid():
                responds = self.save_form(form,request,True,*args,**kwargs)

                return responds or redirect(self.reverse_list_url(*args,**kwargs))
                # return responds
            else:
                return render(request, self.edit_list_template or "stark/change_list.html", locals())

    # 删除一条记录
    def del_list(self, request, pk, *args,**kwargs):
        del_obj = self.get_del_obj(request,pk,*args,**kwargs)

        if not del_obj:
            return HttpResponse("将要删除的记录不存在")
        back_url = self.reverse_list_url(*args,**kwargs)

        if request.method == "GET":
            return render(request, self.del_list_template or "stark/del_list.html", locals())

        if request.method == "POST":
            del_obj.delete()
            return redirect(back_url)

    # 显示一条记录详情
    def show_detail(self, request, pk, *args,**kwargs):
        # print('pk',pk)
        obj = self.model_class.objects.filter(pk=pk).first()
        data_list = []

        if self.detail_fields_display == '__all__':
            for field in self.model_class._meta.fields:
                print('verbose name:', field.verbose_name)
                data_list.append({'label':field.verbose_name,
                                  'data':getattr(obj,field.name)})
        else:
            for field in self.detail_fields_display:
                if isinstance(field,MethodType):
                    label = field(obj=None, is_header=True,*args,**kwargs)
                    data =  field(obj=obj, is_header= False,*args,**kwargs)
                elif isinstance(field,FunctionType):
                    label =  field(self, obj = None, is_header = True,*args,**kwargs)
                    data =  field(self, obj = obj, is_header = False,*args,**kwargs)
                else:
                    field_obj = self.model_class._meta.get_field(field)
                    label = field_obj.verbose_name
                    data = getattr(obj,field_obj.name)
                data_list.append({'label':label, 'data':data})

            # 自定义button的预留接口
            detail_extra_btn = self.get_detail_extra_btn(request,pk,*args,**kwargs)

        return render(request,'stark/show_detail.html',locals())

    # 外键字段中，popup窗口快速添加一条记录
    def create_list(self,request, *args, **kwargs):
        form = self.get_model_form()(request.POST or None)
        # 如果有数据，说明是post请求，如果没有数据说明是get请求
        if form.is_valid():
            # 如果数据校验合格，存在数据库，返回instance
            instance = form.save()
            ## Change the value of the "#id_author". This is the element id in the form
            # 把下面这段js代码返回给前端，关键是author_id，这个值必须来自于数据库
            # 我们看前端怎么处理这段代码
            # 下面’%s‘要加引号，因为这段要显示在前端的时候，不加引号视为变量

            id_name = self.model_name
            return HttpResponse(
                '<script>opener.closePopup(window, "%s", "%s", "#id_%s");</script>' % (instance.pk, instance,id_name))

        return  render(request,'dipay/create_record.html', locals())


    def get_query_param(self):

        query_param = self.request.GET.get("_filter",None)
        return query_param

    def save_query_param(self):
        if self.request.GET:
            query_dict = QueryDict(mutable=True)
            query_dict["_filter"] = self.request.GET.urlencode()

            return query_dict.urlencode()
        return None

    def reverse_list_url(self,*args,**kwargs):
        url_name = self.get_url_name("list")
        if self.namespace:
            url_name = "%s:%s" % (self.namespace, url_name)
        url = reverse(url_name, args=args, kwargs=kwargs)

        query_params = self.get_query_param()
        print(9999,query_params,type(query_params) )
        if query_params:
            url =  "%s?%s" % (url,query_params)
        return url

    def reverse_url(self,view_name,*args,**kwargs):
        url_name = self.get_url_name(view_name)
        if self.namespace:
            url_name = "%s:%s" % (self.namespace,url_name)

        url = reverse(url_name, args=args, kwargs=kwargs)
        if self.save_query_param():
            url = "%s?%s" % (url, self.save_query_param())
        return url

    def reverse_resetpwd_url(self,*args,**kwargs):
        return self.reverse_url("reset_pwd",*args,**kwargs)

    def reverse_add_url(self,*args,**kwargs):
        return self.reverse_url("add",*args,**kwargs)

    def reverse_edit_url(self,*args,**kwargs):
        return self.reverse_url("edit",*args,**kwargs)

    def reverse_del_url(self,*args,**kwargs):
        return self.reverse_url("del",*args,**kwargs)

    # 获取url别名的公共方法
    def get_url_name(self,view_name):
        url_name = "%s_%s_%s" % (self.app_label, self.model_name,view_name)
        if self.prev:
            url_name = "%s_%s" %(url_name, self.prev)
        return url_name

    # 获取url别名的方法独立出来，在模板渲染的时候可以用于反向生成url
    @property
    def get_list_url_name(self):
        return self.get_url_name("list")

    @property
    def get_reset_pwd_url_name(self):
        return self.get_url_name("reset_pwd")

    @property
    def get_add_url_name(self):
        return self.get_url_name("add")

    @property
    def get_edit_url_name(self):
        return self.get_url_name("edit")

    @property
    def get_del_url_name(self):
        return self.get_url_name("del")

    # 闭包函数传进来的func = self.show_list, 相当于self已作为第一个参数传递了，所以inner()的参数不能再接收self
    def wrapper(self,func):
        @functools.wraps(func)
        def inner(request,*args,**kwargs):
            self.request = request
            return func(request,*args,**kwargs)
        return inner

    def get_urls(self):
        patterns = [
            url("^list/$", self.wrapper(self.show_list), name= self.get_list_url_name),
            url("^list_detail/(?P<pk>\d+)/$", self.wrapper(self.show_detail), name= self.get_url_name('show_detail')),
            url("^add/$", self.wrapper(self.add_list), name=self.get_add_url_name),
            url("^edit/(?P<pk>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/$", self.wrapper(self.del_list), name=self.get_del_url_name),
            url("^create/$", self.wrapper(self.create_list), name=self.get_url_name('create')),
        ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())

        return patterns

    # 预留的扩展自定义urls的方法
    def get_extra_urls(self):
        return []

    # 列的编辑删除按钮显示

    def edit_del_display(self, obj=None, is_header=False,*args,**kwargs):
        """
        在列表页显示编辑按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "操作"
        else:
            edit_url = self.reverse_edit_url(pk=obj.id,*args,**kwargs)
            del_url = self.reverse_del_url(pk=obj.id,*args,**kwargs)
            # 下面这句话重复了，在self.reverse里面已经把查询参数带上了
        return mark_safe("<a href='%s'><i class='fa fa-edit'></i></a> <a href='%s'><i class='fa fa-trash'></i></a>" % (
        edit_url, del_url))

class StarkSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = "stark"
        self.namespace = "stark"

    def register(self, model_class, handler_class=StarkHandler, prev=None):
        """
        在site单例中注册app信息
        :param module_class:  ORM表的类
        :param handler_class: 处理请求的视图函数
        :return:
        """
        hander = handler_class(self,model_class,prev)

        self._registry.append({
            "model_class": model_class,
            "handler":hander,
            "prev": prev,
        })

        return hander

    def get_urls(self):
        patterns = []
        for item in self._registry:
            model_class = item["model_class"]
            prev = item["prev"]
            app_label = model_class._meta.app_label
            model_name = model_class._meta.model_name
            handler = item["handler"]

            # 方式一
            # patterns.extend([
            #     url(r"%s/%s/list/" % (app_label, model_name), item["handler"].show_list),
            #     url(r"%s/%s/add/" % (app_label, model_name), item["handler"].add_list),
            #     url(r"%s/%s/edit/(\d+)" % (app_label, model_name), item["handler"].edit_list),
            #     url(r"%s/%s/del/(\d+)" % (app_label, model_name), item["handler"].del_list),
            # ])

            # 方式二
            # stark是一级路由，相当于二级路由r"app01/customer/， 而 /list/相当于三级分发
            if prev:
                patterns.append(url(r"%s/%s/%s/" % (app_label, model_name,prev), (handler.get_urls(),None,None)))
            else:
                patterns.append(url(r"%s/%s/" % (app_label, model_name), (handler.get_urls(),None,None)))

            # pattern = url(r"x1",lambda request: HttpResponse("x1") )
            # patterns.append(pattern)
        return patterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace

site = StarkSite()
