from django.shortcuts import HttpResponse, redirect, render, reverse
from decimal import Decimal
from django.http import JsonResponse
from django.conf.urls import url
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory, formset_factory
from django import forms
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.utils.displays import related_orders_display
from dipay.forms.forms import AddInwardPayModelForm, Inwardpay2OrdersModelForm, ConfirmInwardpayModelForm, \
    EditInwardPayModelForm
from dipay.models import ApplyOrder, FollowOrder, Payer, Pay2Orders, Inwardpay, CurrentNumber
from django.db import transaction
import threading
from rbac.utils.common import compress_image_task
from datetime import datetime


class InwardPayHandler(PermissionHanlder, StarkHandler):
    has_add_btn = False
    filter_hidden = "hidden"

    # 加入一个组合筛选框, default是默认筛选的值，必须是字符串
    option_group = [
        Option(field='bank'),
        Option(field='confirm_status'),

    ]

    popup_list = ['payer','bank']

    search_list = ['create_date','amount','customer__title__icontains',]
    search_placeholder = '搜索 日期 金额 客户名 '

    def add_btn_display(self, request, *args, **kwargs):

        add_url = self.reverse_add_url(*args, **kwargs)
        return "<div class='btn btn-default' onclick='toggleOptionSection()'> 筛选 </div>"

    def get_model_form(self, type=None):
        if type == 'add':
            return AddInwardPayModelForm
        if type == 'edit':
            return EditInwardPayModelForm

    def amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return "客户水单金额"
        else:
            return "%s %s" % (obj.currency.icon, obj.amount)

    def got_amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return "实收金额"
        else:
            return "%s %s" % (obj.currency.icon, obj.got_amount)

    def status_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '待关联金额'
        else:

            related_url = self.reverse_url('relate2order', inwardpay_id=obj.pk)
            torelate_amount = obj.torelate_amount if obj.torelate_amount else '已关联'
            status = 0 if obj.torelate_amount  else 1
            return mark_safe("<a href= '%s' class='torelate-status-%s' > %s </a>" % (related_url, status, torelate_amount))

    # 付款人的显示
    def payer_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '付款人'
        else:
            if obj.payer:
                return obj.payer.title[:20]
            return '-'

    # 客户的显示
    def customer_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '客户'
        else:
            if obj.customer:
                return obj.customer.shortname
            return '-'

    def got_confirm_status_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return "确认状态"
        else:
            confirm_url = self.reverse_url('confirm_pay', inwardpay_id=obj.pk)
            confirm_display_choices = Inwardpay.confirm_choices
            display_text = [item[1] for item in confirm_display_choices if item[0] == obj.confirm_status][0]
            if obj.confirm_status == 0:
                return mark_safe("<a href='%s' target='_blank'> %s </a>" % (confirm_url, display_text))
            else:
                return display_text

    fields_display = [get_date_display('create_date'),
                      payer_display,
                      customer_display,
                      got_amount_display,
                      'bank',
                      got_confirm_status_display,
                      status_display,
                      related_orders_display ]

    detail_fields_display = fields_display + ['remark','keyin_user','ttcopy']

    # 自定义添加记录view
    def add_list(self, request, *args, **kwargs):
        fast_add_list = ['payer','bank', ]

        if request.method == "GET":
            form = self.get_model_form("add")()
            for field in form:
                print(field.name)
                if field.name in fast_add_list:
                    field_obj = self.model_class._meta.get_field(field.name)
                    related_model_name = field_obj.related_model._meta.model_name
                    related_url = '/%s/%s/%s/create/' % (self.namespace,self.app_label,related_model_name)
                    print(related_url)
                    setattr(field,'url',related_url)
            form.instance.create_date = datetime.now()
            # print('inwardpay datetime now',datetime.now())
            # 控制应显示快速添加按钮的字段名
            return render(request, "dipay/inwardpay_add.html", locals())

        if request.method == "POST":
            # 如果要上传文件，必须加上request.FILES, 再试试
            print('request files ttcopy', request.POST, request.FILES.get('ttcopy'))
            form = self.get_model_form("add")(request.POST,request.FILES)
            if form.is_valid():
                # 添加新的款项时，需要把待关联款项设为与收款金额一致
                form.instance.torelate_amount = form.instance.got_amount
                currentnumber_obj = CurrentNumber.objects.get(pk=1)
                new_reference = currentnumber_obj.reference + 1
                while Inwardpay.objects.filter(reference=new_reference).exists():
                    new_reference += 1
                form.instance.reference = new_reference
                currentnumber_obj.reference = new_reference
                form.save()
                currentnumber_obj.save()
                # 检查水单文件，如果过大的话，进行压缩处理，新开一个线程来处理
                t = threading.Thread(target=compress_image_task,args=(form.instance.ttcopy.path,))
                t.start()

                return redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, 'dipay/inwardpay_add.html', locals())

    def save_form(self,form,request,is_update=False,*args, **kwargs):
        if is_update:
            form.save()
            # 压缩图片
            t = threading.Thread(target=compress_image_task, args=(form.instance.ttcopy.path,))
            t.start()
        else:
            form.save()

    # def get_detail_extra_btn(self, request, pk, *args, **kwargs):
    #     detail_confirm_url = self.reverse_url('confirm_pay', inwardpay_id=pk)
    #     return "<a href='%s' class='btn btn-warning'> 确认 </a>" % detail_confirm_url

    def get_extra_urls(self):
        """ 收款关联订单的url  """
        extra_pattern = [
            url("^relate2orders/(?P<inwardpay_id>\d+)/$", self.wrapper(self.relate2order),
                name=self.get_url_name('relate2order')),
            url("^confirm/(?P<inwardpay_id>\d+)/$", self.wrapper(self.confirm_pay),
                name=self.get_url_name('confirm_pay')),
            url("^transfer/(?P<order_id>\d+)/$", self.wrapper(self.transfer),
                name=self.get_url_name('transfer')),
        ]
        return extra_pattern

    def get_queryset_data(self, request, *args, **kwargs):
        pk = request.GET.get('pk')
        if pk:
            return self.model_class.objects.filter(pk=pk)
        else:
            return self.model_class.objects.all()

    # 认领款项
    def confirm_pay(self, request, inwardpay_id, *args, **kwargs):
        obj = Inwardpay.objects.filter(pk=inwardpay_id).first()
        payer = '-'
        if obj.payer:
            customer = obj.payer.customer
            payer = obj.payer.title
        elif obj.customer:
            customer = obj.customer
        else:
            return render(request, 'dipay/msg_after_submit.html', {'msg': '付款人和客户都没填，请先补充完整任何一项'})
        data_list = []
        # fields_display = [get_date_display('create_date'), 'payer', got_amount_display,
        #                   'bank', status_display, got_confirm_status_display]
        data_list.append({'label': '收款日期',
                          'data': obj.create_date.strftime('%Y-%m-%d')})
        data_list.append({'label': '付款人',
                          'data': payer})
        data_list.append({'label': '实收款',
                          'data': '%s %s' % (obj.currency.icon, obj.got_amount)})
        data_list.append({'label': '收款行',
                          'data': obj.bank.title})
        data_list.append({'label': '关联状态',
                          'data': obj.get_status_display})
        data_list.append({'label': '确认状态',
                          'data': obj.get_confirm_status_display})

        return_url = self.reverse_url('list')

        if request.method == "GET":
            form = ConfirmInwardpayModelForm(instance=obj, initial={'customer': customer})
            form.instance.customer_id = customer.pk

            return render(request, 'dipay/confirm_pay.html', locals())

        if request.method == "POST":
            customer_id = request.POST.get('customer')
            amount = Decimal(request.POST.get('amount'))
            form = ConfirmInwardpayModelForm(request.POST, instance=obj)

            if form.is_valid():
                try:
                    if not customer_id:
                        form.errors.update({'customer': ['客户不能为空', ]})
                        raise forms.ValidationError()
                    # customer_obj = Customer.objects.filter(pk=customer_id).first()
                    # payers = customer_obj.payer_set.all()

                    # 校验客户和付款人的关系
                    if customer.pk != int(customer_id):
                        form.errors.update({'customer': ['客户和付款人关联不正确', ]})
                        raise forms.ValidationError()

                    # 校验水单金额和实收金额
                    if amount < obj.got_amount:
                        form.errors.update({'amount': ['水单金额应不小于实收金额', ]})
                        raise forms.ValidationError()

                except Exception as e:
                    print('error', e)
                    return render(request, 'dipay/confirm_pay.html', locals())
                else:
                    form.instance.confirm_status += 1
                    form.instance.torelate_amount = amount
                    form.save()
                    torelate_url = self.reverse_url('relate2order', inwardpay_id=obj.pk)
                    return redirect(torelate_url)
            else:
                return render(request, 'dipay/confirm_pay.html', locals())


    # 关联款项 第二版设计，不用formset，改为一个一个订单的关联，采用阿里的模式
    def relate2order(self, request, inwardpay_id, *args, **kwargs):
        inwardpay_obj = self.model_class.objects.filter(pk=inwardpay_id).first()

        # 第一步先判断用户是否已经确认过该款项，如果状态是"未确认"，直接跳转到确认页面
        confirm_status_dict = { item[1]:item[0]  for item in Inwardpay.confirm_choices}
        if inwardpay_obj.confirm_status == confirm_status_dict.get("未确认"):
            confirm_url = self.reverse_url("confirm_pay",inwardpay_id=inwardpay_id)
            return redirect(confirm_url)

        total_dist_amounts = sum([each.amount for each in Pay2Orders.objects.filter(payment=inwardpay_obj)])
        inwardpay_obj.torelate_amount = inwardpay_obj.amount - total_dist_amounts
        inwardpay_obj.save()

        if inwardpay_obj.customer:
            customer_obj = inwardpay_obj.customer
        else:
            customer_obj = inwardpay_obj.payer.customer

        torelate_amount = inwardpay_obj.torelate_amount
        # torelate_queryset = ApplyOrder.objects.filter(status__lt=3, customer=customer_obj)
        torelate_queryset = ApplyOrder.objects.filter(customer=customer_obj)
        torelate_order_list = []
        # 检查其中的应收金额，确保一致性, 整理可关联订单数据
        for order_obj in torelate_queryset:
            order_obj.collect_amount = order_obj.amount - order_obj.rcvd_amount
            order_obj.save()
            row = {}
            for each in [ 'order_number','customer', 'currency', 'amount', 'rcvd_amount','collect_amount']:
                row[each] = getattr(order_obj, each)
            pay2order_obj = Pay2Orders.objects.filter(payment=inwardpay_obj, order=order_obj).first()
            dist_amount = pay2order_obj.amount if pay2order_obj else 0
            display_dist_amount = '%s%s' % (order_obj.currency.icon, dist_amount) if dist_amount else '--'

            # 判断是否固定定金
            is_fix_amount = 'true' if order_obj.order_number.startswith('L') else 'false'
            row['is_fix_amount'] = is_fix_amount

            # 发票号直接关联跟单记录的url
            row['followorder_url'] = reverse('stark:dipay_followorder_list')+'?q='+ order_obj.order_number

            # 分配金额加上span标签和class，便于js操作，链接showinputbox,点击直接编辑
            amount_tag = "<span class='invoice-amount-display' id='%s-id-%s' amount='%s' onclick='showInputBox(this)'>%s</span>" % (
                 'amount', order_obj.pk, dist_amount, display_dist_amount
            )
            row['dist_amount'] = mark_safe(amount_tag)
            row['dist_value'] = dist_amount
            row['pk'] = order_obj.pk

            save_url = self.reverse_url('relate2order', inwardpay_id=inwardpay_obj.pk)
            save_btn = mark_safe("<span><span class='save-sequence hidden-xs' pk='%s' url='%s' onclick='savePlan(this)'>"
                                 " <i class='fa fa-check-square-o'></i> </span></span>" % (order_obj.pk, save_url))
            row['save_btn'] = save_btn
            if pay2order_obj:
                del_url = reverse('stark:dipay_pay2orders_del', kwargs={'pk':pay2order_obj.pk})
                row['del_btn'] = mark_safe("<a href=%s><i class='fa fa-trash'></i></a>" % del_url)
            else:
                row['del_btn'] = ''

            # 处理固定定金的转移按钮
            row['transfer_btn'] = ''
            if order_obj.order_number.startswith('L'):
                print('transfer btn  order_number ',order_obj.order_number)
                transfer_url = self.reverse_url('transfer', order_id=order_obj.pk)
                row['transfer_btn'] = mark_safe("<a href='%s' order_id='%s' onclick='return transferFixAmount(this)' ><i class='fa fa-exchange'></i></a>" % (transfer_url,order_obj.pk))
                # 固定定金条目不能删除
                row['del_btn'] = ''

            print('row data:',row)

            torelate_order_list.append(row)

        # 先按订单号排序
        torelate_order_list.sort(key=lambda x: x['order_number'], reverse=True)
        # 按关联金额大小排序
        torelate_order_list.sort(key=lambda x: x['dist_value'], reverse=True)

        # 整理已关联订单数据
        related_order_list = Pay2Orders.objects.filter(payment=inwardpay_obj)

        if request.method == "GET":
            return render(request, 'dipay/related_to_orders.html', locals())

        if request.is_ajax():
            order_id = request.POST.get('pk')
            dist_amount = request.POST.get('amount')
            try:
                dist_amount = Decimal(dist_amount)
            except Exception as e:
                return JsonResponse({'status': False, 'field': 'amount', 'error': '必须填数值'})

            if dist_amount <= 0:
                return JsonResponse({'status': False, 'field': 'amount', 'error': '必须填大于0的数值'})

            order_obj = ApplyOrder.objects.filter(pk=order_id).first()
            if not order_obj:
                res = {'status': False, 'field': 'amount', 'error': '没找到订单号'}
                return JsonResponse(res)


            pay2order_obj = Pay2Orders.objects.filter(payment=inwardpay_obj, order=order_obj).first()

            if pay2order_obj:
                # 如果是更新已经关联记录，看看关联金额的差异，只处理差异部分即可
                diff_amount = dist_amount- Decimal(pay2order_obj.amount)
                if diff_amount > inwardpay_obj.torelate_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于可分配的金额'})
                if diff_amount > order_obj.collect_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于订单应收金额'})

                pay2order_obj.amount = dist_amount
                order_obj.rcvd_amount = order_obj.rcvd_amount + diff_amount
                order_obj.collect_amount =  order_obj.collect_amount -diff_amount
                inwardpay_obj.torelate_amount = inwardpay_obj.torelate_amount - diff_amount
            else:
                # 如果是新增关联记录
                if dist_amount > inwardpay_obj.torelate_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于可分配的金额'})
                if dist_amount > order_obj.collect_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于订单应收金额'})

                pay2order_obj = Pay2Orders(payment=inwardpay_obj, order=order_obj, amount=dist_amount)
                current_number_obj = CurrentNumber.objects.get(pk=1)

                # 给每一个新增的分配记录自动的加上分配编号，同时更新currentnumber_obj
                new_dist_ref = current_number_obj.dist_ref + 1
                while Pay2Orders.objects.filter(dist_ref=new_dist_ref).exists():
                    new_dist_ref += 1
                pay2order_obj.dist_ref = new_dist_ref
                current_number_obj.dist_ref = new_dist_ref
                current_number_obj.save()

                order_obj.rcvd_amount = order_obj.rcvd_amount + dist_amount
                inwardpay_obj.torelate_amount = inwardpay_obj.torelate_amount - dist_amount
            try:
                order_obj.save()
                if inwardpay_obj.torelate_amount == 0:
                    inwardpay_obj.status = 1
                inwardpay_obj.save()
                pay2order_obj.save()

            except Exception as e:
                return JsonResponse({'status': False, 'field': 'amount', 'error': '分配收款失败'})

            return JsonResponse({'status': True, 'msg': '分配收款成功'})


    def transfer(self, request, order_id, *args, **kwargs):
        order_obj = ApplyOrder.objects.filter(pk=order_id).first()

        return render(request, 'dipay/transfer_fix_amount.html',locals())


