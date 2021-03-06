from django.shortcuts import HttpResponse, redirect, render, reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.utils.displays import status_display,  info_display, save_display, follow_date_display,  \
    port_display,order_number_display, sales_display,goods_display, confirm_date_display,\
    customer_display
from dipay.models import CurrentNumber, Customer, FollowOrder
from django.conf.urls import url
from django.http import JsonResponse



class WeekelyPlanHandler(PermissionHanlder, StarkHandler):
    show_list_template = 'dipay/weekly_plan_list.html'

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


    # 跟单列表显示的字段内容
    fields_display = [order_number_display, customer_display, sales_display, status_display,
                      info_display('produce_sequence'), goods_display,
                      port_display('discharge_port'), confirm_date_display,
                      follow_date_display('ETD', time_format='%m/%d'),
                      follow_date_display('ETA', time_format='%m/%d'),
                      info_display('load_info'), info_display('book_info'), info_display('produce_info'),
                      ]

    # 自定义按钮的权限控制
    def get_extra_fields_display(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        save_url_name = '%s:%s' % (self.namespace, self.get_url_name('save'))

        if save_url_name in permission_dict:
            return [save_display, ]
        else:
            return []

    def get_queryset_data(self, request, *args, **kwargs):

        return self.model_class.objects.filter(status=1)

    def get_per_page(self):
        return 20

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
                followorder_obj.save()
                data_dict['status'] = True
                res = data_dict
            return JsonResponse(res)
