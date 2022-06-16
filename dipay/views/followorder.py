from django.shortcuts import HttpResponse, redirect, render, reverse
from django.conf import settings
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder, checkbox_display
from dipay.utils.displays import status_display,  info_display, save_display, \
    follow_date_display,order_number_display, sales_display, port_display, goods_display, customer_display, \
    term_display, amount_display,confirm_date_display

from dipay.forms.forms import AddApplyOrderModelForm, EditFollowOrderModelForm
from django.db import models
from django.conf.urls import url
from dipay.models import ApplyOrder


class FollowOrderHandler(PermissionHanlder, StarkHandler):
    show_list_template = 'dipay/show_follow_order_list.html'

    # 自定义列表，外键字段快速添加数据，在前端显示加号
    # popup_list = ['customer',]

    # 加入一个组合筛选框, default是默认筛选的值，必须是字符串
    option_group = [
        Option(field='status',is_multi=False),
        Option(field='salesman',filter_param={'roles__title':'外销员'}, verbose_name='业务'),
        # Option(field='depart'),
    ]

    """ [(0, '备货'), (1, '发货'), (2, '单据'),   (3, '等款'), (4, '完成'),"""

    search_list = ['order__order_number__icontains', 'order__goods__icontains', 'order__customer__shortname__icontains']
    search_placeholder = '搜索 订单号/客户/货物'

    # 模糊搜索
    # search_list = ['customer__title__contains', 'goods__contains','order_number__contains']
    # search_placeholder = '搜索 客户/货品/订单号'

    # 添加按钮
    has_add_btn = False

    # 排序字段
    order_by_list = ['-order__sequence', ]

    # 批量排产
    def batch_to_produce(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            order_obj = self.model_class.objects.filter(pk=pk).first()
            order_obj.status = 1
            order_obj.save()
        return redirect(self.reverse_list_url())

    batch_to_produce.text = '批量排产'

    # 批量拆分订单的选项卡
    def batch_split_order(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        if len(pk_list) > 1:
            msg = '只能选择一个订单'
            return render(request, 'dipay/msg_after_submit.html', locals())
        data_list = []
        for pk in pk_list:
            follow_order_obj = self.model_class.objects.filter(pk=pk).first()
            order_pk = follow_order_obj.order.pk
            # 订单号只取前五位，如J3879-1, order_number: J3879
            order_number = follow_order_obj.order.order_number[:5]
            customer = follow_order_obj.order.customer.shortname
            sub_sequence_num = follow_order_obj.order.sub_sequence
            if sub_sequence_num == 0:
                sub_sequence_num = 1
            sub_sequence = mark_safe(
                "<input name='sub_sequence' type='text' value='%s'>" % (sub_sequence_num))
            goods = mark_safe(
                '<input name="goods" type="text" value="%s"> ' % (follow_order_obj.order.goods))
            amount = mark_safe(
                '<input  name="amount"  type="text" value="%s" > ' % (follow_order_obj.order.amount))

            data_list.append([order_number, customer, sub_sequence, goods, amount])
            sub_sequence = mark_safe(
                "<input name='sub_sequence' type='text' value='%s'>" % (sub_sequence_num+1))

            data_list.append([order_number, customer, sub_sequence, goods, amount])

            return render(request, 'dipay/split_order.html', locals())

    # 拆分订单的view
    def split_record(self, request, pk, *args, **kwargs):

        fields_list =  ['sub_sequence','goods','amount']
        length = len(request.POST.getlist(fields_list[0]))
        # 初始化数据列表，含n个字典
        data_list = [{} for i in range(length)]
        # 整理成列表套字典的格式，方便后续添加到ORM
        for field in fields_list:
            for n, item in enumerate(request.POST.getlist(field)):
                data_list[n][field] = item

        order_obj = ApplyOrder.objects.filter(pk=pk).first()
        followorder_obj = order_obj.followorder
        count = 0
        splited_order_list = []
        for i in range(length):
            # 更新已有订单

            for key, val in data_list[i].items():
                setattr(order_obj, key, val)
            order_obj.order_number = "%s%s-%s" % (order_obj.get_order_type_display(),order_obj.sequence,order_obj.sub_sequence)
            splited_order_list.append( order_obj.order_number)
            if i != 0:
                try:
                    # 新增拆分的订单, 把id置为None即可
                    order_obj.pk = None
                    order_obj.save()
                    # 同时创建跟单记录, 清空ETD  ETA, Status =0
                    followorder_obj.pk = None
                    followorder_obj.order_id = order_obj.pk
                    followorder_obj.ETD = None
                    followorder_obj.ETA = None
                    followorder_obj.status = 0
                    followorder_obj.book_info = '订舱'
                    followorder_obj.salesman = order_obj.salesperson
                    followorder_obj.save()
                except Exception as e:
                    msg = '订单号可能重复，请检查。 错误内容：%s' % e
                    return render(request,'dipay/msg_after_submit.html',locals())
            else:
                order_obj.save()
            count += 1
            list_url = self.reverse_list_url()
            order_list = [ f"<a href='{list_url}?q={order_number[:5]}'> {order_number} </a>" for order_number in splited_order_list]

        msg = mark_safe('成功拆分%s个订单: %s ' % (count, ' '.join(order_list)))
        return render(request,'dipay/msg_after_submit.html',locals())

    batch_split_order.text = '拆分订单'

    # 批量处理列表
    batch_process_list = [batch_to_produce, batch_split_order]

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
    fields_display = [checkbox_display, order_number_display, customer_display,sales_display, status_display, goods_display,
                      port_display('discharge_port'), term_display, confirm_date_display,
                      follow_date_display('ETD', time_format='%m/%d'),
                      follow_date_display('ETA', time_format='%m/%d'),
                      info_display('load_info'), info_display('book_info'), info_display('produce_info'),
                      amount_display,
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
        if request.user.username == 'brank':
            return self.model_class.objects.all()
        if request.user:
            return self.model_class.objects.all()
        return self.model_class.objects.all()

    def get_per_page(self):
        return 20

    def get_model_form(self, type=None):
        return EditFollowOrderModelForm

    def get_extra_urls(self):
        patterns = [
            url("^save/$", self.wrapper(self.save_record), name=self.get_url_name('save')),
            url("^split/(?P<pk>\d+)/$", self.wrapper(self.split_record), name=self.get_url_name('split')),
            url("^neating/$", self.wrapper(self.neating), name=self.get_url_name('neating')),
        ]

        return patterns

    # 每行数据保存的方法，使用ajax
    def save_record(self, request, *args, **kwargs):
        if request.is_ajax():
            data_dict = request.POST.dict()
            pk = data_dict.get('pk')
            data_dict.pop('csrfmiddlewaretoken')

            followorder_obj = self.model_class.objects.filter(pk=pk).first()
            if not followorder_obj:
                res = {'status': False, 'msg': 'obj not found'}
            else:
                for item, val in data_dict.items():
                    # 金额要保存到applyorder表
                    if item == 'amount':
                        applyorder_obj = followorder_obj.order
                        try:
                            val = float(val)
                        except Exception as e:
                            data_dict['status'] = False
                        else:
                            applyorder_obj.amount = val
                            applyorder_obj.save()
                    else:
                        setattr(followorder_obj, item, val)
                followorder_obj.save()
                data_dict['status'] = True
                res = data_dict
            return JsonResponse(res)

    # 预留的接口，用户批量整理数据资料
    def neating(self, request, *args, **kwargs):
        count=0
        for obj in self.model_class.objects.all():
            obj.salesman = obj.order.salesperson
            obj.save()
            count += 1
        return HttpResponse('整理成功%s条数据' % count)