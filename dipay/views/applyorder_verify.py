from django.shortcuts import HttpResponse, redirect, render, reverse
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text, checkbox_display, PermissionHanlder
from dipay.models import ApplyOrder, Customer, FollowOrder
from django.conf.urls import url
from datetime import datetime


class ApplyOrderVerifyHandler(PermissionHanlder, StarkHandler):
    has_add_btn =  False
    # 加入一个组合筛选框
    option_group = [
        Option(field='status'),
        # Option(field='depart'),
    ]

    # 模糊搜索
    search_list = ['customer__title__contains', 'goods__contains', 'order_number__contains']
    search_placeholder = '搜索 客户/货品/订单'

    def collect_amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '已收款'
        else:
            payments_url_name = "%s:%s" % (self.namespace, 'dipay_pay2orders_list')
            payments_url = reverse(payments_url_name)+'?order_id=%s' % obj.pk
            return mark_safe("<a href=%s target='_blank'> %s </a>" % (payments_url, obj.rcvd_amount))

    def batch_verify(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            order_obj = ApplyOrder.objects.filter(pk=pk).first()
            sequence = str(order_obj.sequence)
            if len(sequence) < 4:
                sequence = sequence.zfill(4)
            order_obj.order_number = "%s%s" % (order_obj.get_order_type_display(), sequence)
            order_obj.status = 1
            order_obj.save()

        return redirect(self.reverse_list_url())

    batch_verify.text = '批量审核'

    def batch_to_workshop(self, request, *args, **kwargs):
        """批量下单"""
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            order_obj = ApplyOrder.objects.filter(pk=pk).first()

            order_obj.status = 2
            if not order_obj.confirm_date:
                order_obj.confirm_date = datetime.now()
            order_obj.save()
            # 生成跟单记录
            # 判断是否以存在跟单记录, 是则略过
            if not FollowOrder.objects.filter(order=order_obj).exists():
                FollowOrder.objects.create(order=order_obj)
                print('生成跟单记录<%s>' % order_obj)

        return redirect(self.reverse_list_url())

    batch_to_workshop.text = '批量下单'

    batch_process_list = [batch_verify, batch_to_workshop]

    def amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '发票金额'
        else:
            amount_text = "%s %s" % (obj.currency.icon, obj.amount)
            return amount_text

    def status_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '状态'
        else:
            if obj.status == 0 :
                return mark_safe("<span style='color:red'> %s </span>" % obj.get_status_display())
            else:
                return obj.get_status_display()

    def get_queryset_data(self, request, *args, **kwargs):
        return self.model_class.objects.filter(status__in=[0, 1,2])

    def get_per_page(self):
        return 10

    fields_display = [checkbox_display, get_date_display('create_date'), 'salesperson', 'order_number',
                      'customer', 'goods', amount_display, status_display, collect_amount_display]

    def save_form(self,form,request,is_update=False, *args, **kwargs):
        """编辑时save form需要更新order_number"""
        # print(123213, form.instance.sub_sequence, type(form.instance.sub_sequence))
        order_type = form.instance.get_order_type_display()
        sub_sequence = form.instance.sub_sequence
        sequence = str(form.instance.sequence)
        sequence = sequence.zfill(4) if len(sequence) < 4 else sequence
        order_number = "%s%s" % (order_type, sequence)
        if sub_sequence != 0:
            order_number = "%s-%s" % (order_number, sub_sequence)
        form.instance.order_number = order_number
        msg = f'订单信息更新成功'
        try:
            form.save()
        except Exception as e:
            print(e)
            msg = f'出现下列错误{e}'

        return render(request,'dipay/msg_after_submit.html',{'msg':msg})

    def get_extra_urls(self):
        patterns = [
            url("^neating/$", self.wrapper(self.neating), name=self.get_url_name('neating')),
        ]
        return patterns

    def neating(self,request, *args, **kwargs):
        count = 0
        choice = [item[0] for item in self.model_class.status_choices if item[1] == '已下单'][0]
        # for obj in self.model_class.objects.filter(customer__isnull=True):
        #     customer_title = obj.remark
        #     customer_obj = Customer.objects.filter(title__contains=customer_title ).first()
        #     if customer_obj:
        #         obj.customer = customer_obj
        #         obj.status = choice
        #         print(customer_obj,choice)
        #         count += 1
        #         obj.save()

        for obj in self.model_class.objects.filter(status=0):
            obj.status = 2
            obj.save()
            count += 1

        return HttpResponse('neating okay (%s) records updated ' % count)