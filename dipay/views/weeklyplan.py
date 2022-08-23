from django.shortcuts import HttpResponse, redirect, render, reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.utils.displays import status_display,  info_display, save_display, follow_date_display,  \
    port_display,order_number_display, sales_display,goods_display, confirm_date_display,\
    customer_display, basic_info_display, customer_goods_port_display
from dipay.models import CurrentNumber, Customer, FollowOrder
from django.conf.urls import url
from django.http import JsonResponse
from django.http import QueryDict


class WeekelyPlanHandler(PermissionHanlder, StarkHandler):
    show_list_template = 'dipay/weekly_plan_list.html'

    # 标签导航显示， active有值的是默认激活的标签
    tab_list = [('装箱','装箱','active'), ('发货','排产中',""),]
    status_dict = {item[1]: item[0] for item in FollowOrder.follow_choices}
    def get_tabs(self,request,*args,**kwargs):
        tabs = []

        for status in self.tab_list:
            status_val = str(self.status_dict.get(status[0]))
            row = {
                'url': '?status=%s' % status_val,
                'label': status[1],
                'active': status[2],
            }
            if request.GET:
                query_dict = request.GET.copy()
                query_dict._mutable = True
                if query_dict.get('status'):
                    if query_dict.get('status')==status_val:
                        row['active'] = 'active'
                    else:
                        row['active'] = ''
                query_dict["status"] = status_val
                row['url'] = '?%s' % query_dict.urlencode()

            tabs.append(row)
        return tabs

    # 按状态筛选
    option_group = [Option(field='status'),]

    # 自定义列表，外键字段快速添加数据，在前端显示加号
    # popup_list = ['customer',]

    search_list = ['order__order_number__contains', 'order__goods__icontains', 'order__customer__shortname__icontains']
    search_placeholder = '搜索 订单号/客户/货物'

    # 模糊搜索
    # search_list = ['customer__title__contains', 'goods__contains','order_number__contains']
    # search_placeholder = '搜索 客户/货品/订单号'

    # 添加按钮
    has_add_btn = False

    # 排序字段
    order_by_list = ['produce_sequence', ]

    def edit_display(self, obj=None, is_header=False, *args, **kwargs):
        """
        在列表页显示编辑按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "操作"
        else:
            edit_url = self.reverse_edit_url(pk=obj.id)
            if obj.status == 0:
                return mark_safe("<i class='fa fa-edit'></i>")
            else:
                return mark_safe("<a href='%s'><i class='fa fa-edit'></i></a>" % edit_url)

    role_edit_dict = {
        '外销员':['sales_remark',],
        '外贸部经理':"__all__",
        '外贸跟单':"__all__",
        '总经理':"__all__",
        '工厂跟单':['produce_info',],
    }
    def get_editable(self,field):
        user = self.request.user
        for role in user.roles.all():
            editable_list = self.role_edit_dict.get(role.title)
            if not editable_list :
                return False
            if editable_list == '__all__':
                return True
            if field in editable_list:
                print(field, '在可编辑列表中',role)
                return True


    # 跟单列表显示的字段内容   hidden_xs指定的列在手机版式下不显示
    fields_display = [basic_info_display, customer_goods_port_display, status_display,
                      info_display('produce_sequence',hidden_xs='hidden-xs'),
                      follow_date_display('ETD', time_format='%m/%d',),
                      follow_date_display('ETA', time_format='%m/%d',hidden_xs='hidden-xs'),
                      info_display('load_info',hidden_xs='hidden-xs'), info_display('book_info',hidden_xs='hidden-xs'), info_display('produce_info',title='生产',hidden_xs='hidden-xs'),
                      info_display('sales_remark',title='业务', hidden_xs='hidden-xs'),
                      ]

    # 自定义按钮的权限控制
    def get_extra_fields_display(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        save_url_name = '%s:%s' % (self.namespace, self.get_url_name('save'))

        if save_url_name in permission_dict:
            return [save_display, ]
        else:
            return []

    def get_queryset_data(self, request, is_search=None, *args, **kwargs):
        # 搜索所用的数据另行指定范围
        if is_search:
            return  self.model_class.objects.exclude(order__order_type=2).exclude(status=4)
        # status 1 排产  5 货好
        if not request.GET.get('status'):
            for item in self.tab_list:
                if item[2] == 'active':
                    return self.model_class.objects.filter(status=self.status_dict.get(item[0])).exclude(order__order_type=2)
        else:
            return self.model_class.objects.filter(status__in=[1,5]).exclude(order__order_type=2)

    def get_per_page(self):
        return 30

    def get_extra_urls(self):
        patterns = [
            url("^save/$", self.wrapper(self.save_plan), name=self.get_url_name('save')), ]

        return patterns

    def save_plan(self, request, *args, **kwargs):
        # ajax 方式直接修改produce_sequence的值
        if request.is_ajax():
            data_dict = request.POST.dict()
            pk = data_dict.get('pk')
            data_dict.pop('csrfmiddlewaretoken')

            followorder_obj = FollowOrder.objects.filter(pk=pk).first()
            if not followorder_obj:
                res = {'status': False, 'msg': 'obj not found'}
            else:
                for item, val in data_dict.items():
                    setattr(followorder_obj, item, val)
                # 如果follow_order完结，更新applyorder的status
                print(9999999, followorder_obj.status,type(followorder_obj.status))
                if followorder_obj.status == '4' or followorder_obj.status == 4:
                    followorder_obj.order.status = 3
                    followorder_obj.order.save()
                followorder_obj.save()
                data_dict['status'] = True
                res = data_dict
            return JsonResponse(res)
