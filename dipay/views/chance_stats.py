
from stark.service.starksite import StarkHandler,Option
from stark.utils.display import get_date_display,get_choice_text
from django.utils.safestring import mark_safe
from django.shortcuts import reverse,render
from stark.utils.display import PermissionHanlder, info_display, save_display
from django.conf.urls import url
from django.conf import settings
from django.http import JsonResponse
from dipay.utils.tools import str_width_control
from dipay.forms.forms import ChanceModelForm
from dipay.models import Chance
from types import FunctionType,MethodType
from stark.service.pagination import Pagination
from django.db.models import Q,ForeignKey,ManyToManyField, TextField

class ChanceStatsHandler(PermissionHanlder,StarkHandler):

    show_list_template = "dipay/show_chance_list.html"


    # 月份的display
    def month_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '月份'
        else:
            month = obj["month"].strftime("%Y年%m月")
            return month

    def owner_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '外销员'
        else:
            return obj["owner__nickname"]

    def count_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '询盘数'
        else:
            return obj["c"]


    fields_display = [month_display,owner_display,count_display]

    def get_queryset_data(self,request,is_search=None,*args,**kwargs):
        from django.db.models.functions import TruncMonth
        from django.db.models import Count
        ret = Chance.objects.annotate(month=TruncMonth("create_date")).values(
            "month","owner").annotate(c=Count("id")).values("month","owner__nickname", "c")
        for each in ret:
            print(each)

        return ret

    def get_urls(self):
        patterns = [
            url("^list/$", self.wrapper(self.show_list), name=self.get_list_url_name),
        ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())

        return patterns

        # 列表页面

    def show_list(self, request, *args, **kwargs):

        fields_display = self.get_fields_display(request, *args, **kwargs)

        header_list = []
        data_list = []
        filter_hidden = self.filter_hidden
        batch_process_hidden = self.batch_process_hidden
        guideline = self.guideline

        tabs = self.get_tabs(request, *args, **kwargs)

        searched_queryset = self.get_queryset_data(request, *args, **kwargs)

        ############## 1. 添加按钮############
        add_btn = self.add_btn_display(request, *args, **kwargs)
        # print('add btn',add_btn)

        # 如果是空表或者数据结果为空，按空表方式显示
        if not searched_queryset:
            show_template = self.show_list_template or "stark/show_list.html"
            header_list.extend([self.model_name, "操作"])
            data_list = [[], ]  # 二维列表存储表体内容
            return render(request, show_template, locals())

        ############## 1. 模糊搜索 ###############
        search_list = self.search_list

        # 模糊搜索框的 placeholder
        search_placeholder = self.search_placeholder

        user_query = self.request.GET.get("q", "")

        if user_query:
            user_query = user_query.strip()
            queryset_data = self.get_queryset_data(request, is_search=True)
            conn = Q()
            conn.connector = "OR"
            for item in search_list:
                # 使用ORM的Q函数来构造OR条件的查询
                conn.children.append((item, user_query))
            try:
                # 测试filter的条件是否会出错
                searched_queryset = queryset_data.filter(conn)

            except Exception as e:
                # 如果出错，则逐一查询，将查询到的有效queryset的查询条件放入conn_good
                conn_good = Q()
                for child in conn.children:
                    try:
                        q1 = Q(child)
                        queryset_data.filter(q1)
                        conn_good.add(q1, "OR")
                    except:
                        continue
                # 按合法的查询条件再次查询，这要重复消耗查询资源，暂时没有找到更好的办法。
                searched_queryset = queryset_data.filter(conn_good)

        ###  获取url中的过滤条件 #############   ?depart=1&gender=2&page=123&q=999
        filter_condition = self.get_url_filter()

        ############## 1. 组合筛选的区域显示 ###############
        if self.option_group:
            option_group_dict = {}
            group_filter = {}
            for option_obj in self.option_group:
                query_dict = self.request.GET.copy()
                query_dict._mutable = True

                # query_dict.update({'status':0})
                # 为了实现默认筛选的功能进行的判断，注意默认筛选要使用字符串形式，否则容易匹配失败
                # 只有在不q搜索时才进行默认筛选
                # query_dict 是QueryDict对象，像字典但不是字典，有些字典的方法不可用货不一样，比如update
                if option_obj.default is not None and query_dict.get('q') is None and query_dict.get(
                        option_obj.field) is None:
                    query_dict.update({option_obj.field: option_obj.default})
                    # 在筛选条件中加入默认筛选
                    filter_condition.update({option_obj.field: option_obj.default})

                # 这个字典的键值是可迭代对象，给出页面需要的html标签
                option_group_dict[option_obj.field] = option_obj.get_data(self.model_class, query_dict)

        """
        基本原理：
        把model里面外键字段和choice字段的内容找到，作为关键字标签显示在页面上
        点击这些标签，把字段和内容作为以get关键字参数传递到后台
        根据这些组合条件筛选数据库，然后展示在前台  
        """

        # 根据以上过滤条件过滤数据, 如果筛选条件为'all'的要去掉这个条件
        filter_condition = {k: v for k, v in filter_condition.items() if v != 'all'}
        print(filter_condition)
        searched_queryset = searched_queryset.filter(**filter_condition)

        # 在由用户定义要进行筛选的字段 option_group = [option_obj, ]
        # 在option中内置方法，获取对应字段的关联值，yield给调用者

        # 前端进行显示，并把value值包含到标签中



        ############## 1. 分页 ###############
        query_params = request.GET.copy()
        query_params._mutable = True
        #
        # print("ordered_queryset.count()",ordered_queryset.count())
        # print('request.GET.get("page")',request.GET.get("page"))

        pager = Pagination(
            current_page=request.GET.get("page"),
            all_count=searched_queryset.count(),
            base_url=request.path,
            query_params=query_params,
            per_page=self.get_per_page(),
        )

        data_query_set = searched_queryset[pager.start:pager.end]

        ############## 1. 定制显示列 ############
        if fields_display:
            # 处理表头
            for k in fields_display:
                if isinstance(k, FunctionType):
                    verbose_name = k(self, obj=None, is_header=True, *args, **kwargs)
                elif isinstance(k, MethodType):
                    verbose_name = k(obj=None, is_header=True, *args, **kwargs)
                else:
                    verbose_name = self.model_class._meta.get_field(k).verbose_name
                header_list.append(verbose_name)

            # 处理表体 方式一
            for row in data_query_set:
                row_list = []
                for key in fields_display:
                    if isinstance(key, FunctionType):
                        field_val = key(self, obj=row, is_header=False, *args, **kwargs)
                    elif isinstance(key, MethodType):
                        field_val = key(obj=row, is_header=False, *args, **kwargs)
                    else:
                        field_val = getattr(row, key)
                    row_list.append(field_val)
                data_list.append(row_list)
                # 方法二
                # data_list = self.model_class.objects.values_list(*self.fields_display)

        else:
            header_list.extend([self.model_name, "操作"])
            data_list = [[str(row), self.edit_del_display(row, False, *args, **kwargs)] for row in data_query_set]

        #
        show_template = self.show_list_template or "stark/show_list.html"

        return render(request, show_template, locals())

