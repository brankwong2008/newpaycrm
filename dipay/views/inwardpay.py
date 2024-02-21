from django.shortcuts import HttpResponse, redirect, render, reverse
from decimal import Decimal
from django.http import JsonResponse
from django.conf.urls import url
from django.db.models import F, Q, Max, Min, Avg, Sum, Count
from django.utils.safestring import mark_safe
from django import forms
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.utils.displays import related_orders_display, ttcopy_display, info_display
from dipay.forms.forms import AddInwardPayModelForm, ConfirmInwardpayModelForm, \
    EditInwardPayModelForm
from dipay.models import ApplyOrder, Pay2Orders, Inwardpay, CurrentNumber, Currency, ExchangeRate
import threading
from rbac.utils.common import compress_image_task
from datetime import datetime
from dipay.utils.order_updates import order_payment_update


class InwardPayHandler(PermissionHanlder, StarkHandler):
    has_add_btn = False
    filter_hidden = "hidden"

    page_title = "收款管理"

    show_list_template = "dipay/inwardpay_show_list.html"

    #  这是一个静态数据，只在第一次初始化的时候运行，这个不会随着时间动态更新
    # extra_render_data_show_list = {"exchangerate":{},"today":datetime.now().strftime("%Y/%m/%d")}

    # 给额外动态数据准备的一个func，把func传给handler，让其每次取数据时执行一次
    def get_exchangerate(self):
        extra_render_data = {"exchangerate": {}}
        for currency in Currency.objects.exclude(title="人民币"):
            exchangerate_obj = currency.exchangerate_set.all().order_by("-id").first()
            rate = exchangerate_obj.rate
            extra_render_data["today"] = exchangerate_obj.update_date.strftime("%Y/%m/%d")
            extra_render_data["exchangerate"][currency.icon] = rate
        return extra_render_data

    # 改为一个动态数据，给render_data初入一个func
    extra_render_func_show_list = {"func":get_exchangerate}


    # 加入一个组合筛选框, default是默认筛选的值，必须是字符串
    option_group = [
        Option(field='bank'),
        Option(field='confirm_status'),

    ]

    popup_list = ['payer', 'bank']

    search_list = ['create_date', 'amount', 'customer__title__icontains', ]
    search_placeholder = '搜索 日期 金额 客户名 '

    def add_btn_display(self, request, *args, **kwargs):

        add_url = self.reverse_add_url(*args, **kwargs)
        add_btn = "<span><a href='%s' class='btn btn-primary inwardpay-add-record'> + </a></span>" % (add_url)
        return add_btn+ "<span class='btn btn-default' onclick='toggleOptionSection()'> 筛选 </span>"

    def get_model_form(self, handle_type=None):
        if handle_type == 'add':
            return AddInwardPayModelForm
        if handle_type == 'edit':
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
            details_url = self.reverse_url("show_detail",pk=obj.pk)
            return mark_safe('<a href="%s" target="_blank" style="color:black">%s %s</a>'  % (details_url,obj.currency.icon, obj.got_amount))

    def to_relate_amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return mark_safe("<span class='hidden-xs'>待关联金额</span>")
        else:

            related_url = self.reverse_url('relate2order', inwardpay_id=obj.pk)
            torelate_amount = obj.torelate_amount if obj.torelate_amount else '已关联'
            status = 0 if obj.torelate_amount else 1
            return mark_safe(
                "<a href= '%s' class='torelate-status-%s hidden-xs' > %s </a>" % (related_url, status, torelate_amount))

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
            return mark_safe("<span class='hidden-xs'>确认状态</span>")
        else:
            confirm_url = self.reverse_url('confirm_pay', inwardpay_id=obj.pk)
            confirm_display_choices = Inwardpay.confirm_choices
            display_text = [item[1] for item in confirm_display_choices if item[0] == obj.confirm_status][0]
            if obj.confirm_status == 0:
                return mark_safe("<a href='%s' class='hidden-xs' target='_blank'> %s </a>" % (confirm_url, display_text))
            else:
                return mark_safe("<span class='hidden-xs'>%s</span>" % display_text)

    fields_display = [get_date_display('create_date'),
                      info_display('payer', hidden_xs="hidden-xs", max_width=20, editable=False),
                      customer_display,
                      info_display('bank', hidden_xs="hidden-xs",editable=False),
                      got_amount_display,
                      to_relate_amount_display,
                      related_orders_display,
                      ttcopy_display,
                      got_confirm_status_display,
                      ]

    detail_fields_display = fields_display + ['remark', 'keyin_user',]

    # 自定义添加记录view
    def add_list(self, request, *args, **kwargs):
        """新增一笔收款"""
        page_title = self.page_title
        #  外键字段快速添加一条记录，弹窗式
        fast_add_list = ['payer', 'bank', ]

        if request.method == "GET":
            form = self.get_model_form("add")()
            for field in form:
                print(field.name)
                if field.name in fast_add_list:
                    field_obj = self.model_class._meta.get_field(field.name)
                    related_model_name = field_obj.related_model._meta.model_name
                    related_url = '/%s/%s/%s/create/' % (self.namespace, self.app_label, related_model_name)
                    # 把快速添加的url绑定到field对象中
                    setattr(field, 'url', related_url)
            form.instance.create_date = datetime.now()

            return render(request, "dipay/inwardpay_add.html", locals())

        if request.method == "POST":
            # 如果要上传文件，必须加上request.FILES, 再试试
            # print('request files ttcopy', request.POST, request.FILES.get('ttcopy'))
            form = self.get_model_form("add")(request.POST, request.FILES)
            if form.is_valid():
                # 添加新的款项时，需要把待关联款项设为与收款金额一致
                form.instance.torelate_amount = form.instance.amount
                form.instance.keyin_user = request.user
                currentnumber_obj = CurrentNumber.objects.get(pk=1)
                new_reference = currentnumber_obj.reference + 1
                while Inwardpay.objects.filter(reference=new_reference).exists():
                    new_reference += 1
                form.instance.reference = new_reference
                currentnumber_obj.reference = new_reference
                # 记录手续费
                charge_fee = form.instance.amount - form.instance.got_amount
                form.instance.remark += f"手续费:{form.instance.currency.icon}{charge_fee}"
                # 记录汇率
                if form.instance.currency.title != "人民币":
                    create_date = form.instance.create_date
                    exchangerate_obj = ExchangeRate.objects.filter(
                        update_date=create_date,currency=form.instance.currency).first() or ExchangeRate.objects.filter(
                        currency=form.instance.currency
                    ).order_by("-id").first()

                form.instance.remark += f" 参考汇率 {exchangerate_obj.rate}"

                form.save()
                currentnumber_obj.save()
                # 检查水单文件，如果过大的话，进行压缩处理，新开一个线程来处理
                t = threading.Thread(target=compress_image_task, args=(form.instance.ttcopy.path,))
                t.start()

                return redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, 'dipay/inwardpay_add.html', locals())

    def save_form(self, form, request, is_update=False, *args, **kwargs):
        if is_update:
            form.save()

        else:
            form.save()
            # 压缩图片
            t = threading.Thread(target=compress_image_task, args=(form.instance.ttcopy.path, 550))
            t.start()

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
        page_title = "收款关联订单"

        inwardpay_obj = self.model_class.objects.filter(pk=inwardpay_id).first()

        # 第一步先判断用户是否已经确认过该款项，如果状态是"未确认"，直接跳转到确认页面
        confirm_status_dict = {item[1]: item[0] for item in Inwardpay.confirm_choices}
        if inwardpay_obj.confirm_status == confirm_status_dict.get("未确认"):
            confirm_url = self.reverse_url("confirm_pay", inwardpay_id=inwardpay_id)
            return redirect(confirm_url)


        # 已分配金额合计
        total_dist_amounts =  Pay2Orders.objects.filter(payment=inwardpay_obj).aggregate(sumup = Sum("amount"))["sumup"]
        if not total_dist_amounts:
            total_dist_amounts = 0

        inwardpay_obj.torelate_amount = inwardpay_obj.amount - total_dist_amounts
        inwardpay_obj.save()

        customer_obj = inwardpay_obj.customer or inwardpay_obj.payer.customer

        torelate_amount = inwardpay_obj.torelate_amount
        # torelate_queryset = ApplyOrder.objects.filter(status__lt=3, customer=customer_obj)
        torelate_queryset = ApplyOrder.objects.filter(customer=customer_obj, status__gte=2)
        torelate_order_list = []

        # 检查其中的应收金额，确保一致性, 整理可关联订单数据
        for order_obj in torelate_queryset:
            order_obj.collect_amount = order_obj.amount - order_obj.rcvd_amount
            order_obj.save()
            row = {}
            for each in ['order_number', 'customer', 'currency', 'amount', 'rcvd_amount', 'collect_amount']:
                row[each] = getattr(order_obj, each)
            pay2order_obj = Pay2Orders.objects.filter(payment=inwardpay_obj, order=order_obj).first()
            if not pay2order_obj:
                dist_amount = 0
            else:
                dist_amount =pay2order_obj.amount
            display_dist_amount = '%s%s' % (order_obj.currency.icon,  round(pay2order_obj.amount * pay2order_obj.rate,2)) if dist_amount else '--'

            # 判断是否固定定金
            is_fix_amount = 'true' if order_obj.order_number.startswith('L') else 'false'
            row['is_fix_amount'] = is_fix_amount

            # 发票号直接关联跟单记录的url
            row['followorder_url'] = reverse('stark:dipay_followorder_list') + '?q=' + order_obj.order_number

            # 分配金额加上span标签和class，便于js操作，链接showinputbox,点击直接编辑
            currency_order = order_obj.currency.title
            currency_inward = inwardpay_obj.currency.title

            # # 可关联订单中，显示每个订单分配的转换汇率，默认为1的不显示
            rate_tag = ""
            rate = pay2order_obj.rate if pay2order_obj else 0
            if pay2order_obj and pay2order_obj.rate != 1:
                rate_tag = f"<span style='margin-left:6px'> " \
                           f" (分配: {inwardpay_obj.currency.icon}{pay2order_obj.amount} x " \
                           f"汇率:{pay2order_obj.rate}) <span>"

            # 可关联订单中，显示每个订单已分配的金额的tag
            amount_tag = "<span class='invoice-amount-display' " \
                         "id='%s-id-%s' " \
                         "currency_order='%s' " \
                         "currency_inward='%s'  " \
                         "amount='%s' " \
                         "rate='%s' " \
                         "onclick='showDistInput(this)'" \
                         ">%s</span>" % (
                'amount', order_obj.pk, currency_order,currency_inward, dist_amount,rate,display_dist_amount
            )

            row['dist_amount'] = mark_safe(amount_tag + rate_tag)
            row['dist_value'] = dist_amount
            row['pk'] = order_obj.pk

            save_url = self.reverse_url('relate2order', inwardpay_id=inwardpay_obj.pk)
            save_btn = mark_safe(
                "<span><span class='save-sequence hidden-xs' pk='%s' url='%s' onclick='savePlan(this)'>"
                " <i class='fa fa-check-square-o'></i> </span></span>" % (order_obj.pk, save_url))
            row['save_btn'] = save_btn
            if pay2order_obj:
                del_url = reverse('stark:dipay_pay2orders_del', kwargs={'pk': pay2order_obj.pk})
                row['del_btn'] = mark_safe("<a href=%s><i class='fa fa-trash'></i></a>" % del_url)
            else:
                row['del_btn'] = ''

            # 处理固定定金的转移按钮
            row['transfer_btn'] = ''
            if order_obj.order_number.startswith('L'):
                print('transfer btn  order_number ', order_obj.order_number)
                transfer_url = self.reverse_url('transfer', order_id=order_obj.pk)
                row['transfer_btn'] = mark_safe(
                    "<a href='%s' order_id='%s' onclick='return transferFixAmount(this)' ><i class='fa fa-exchange'></i></a>" % (
                    transfer_url, order_obj.pk))
                # 固定定金条目不能删除
                row['del_btn'] = ''

            # print('row data:', row)

            torelate_order_list.append(row)

        # 先按订单号排序
        torelate_order_list.sort(key=lambda x: x['order_number'][1:], reverse=True)
        # 按关联金额大小排序
        torelate_order_list.sort(key=lambda x: x['dist_value'], reverse=True)

        # 整理已关联订单数据
        related_order_list = Pay2Orders.objects.filter(payment=inwardpay_obj)

        if request.method == "GET":
            return render(request, 'dipay/related_to_orders.html', locals())

        if request.is_ajax():
            order_id = request.POST.get('pk')
            amount = request.POST.get('amount')  # 从收款中分出的金额，币种比如是人民币
            rate = Decimal(request.POST.get('rate',1))     # 分出的金额关联到订单上的计算汇率 实际关联结果 = amount*rate, 按常识来处理

            try:
                dist_amount = Decimal(amount)      # 从款中来的金额
                dist_to_amount = Decimal(amount)*Decimal(rate)   #分配到订单中的金额
            except Exception as e:
                return JsonResponse({'status': False, 'field': 'amount', 'error': '必须填数值'})

            # if dist_amount <= 0:
            #     return JsonResponse({'status': False, 'field': 'amount', 'error': '必须填大于0的数值'})

            order_obj = ApplyOrder.objects.filter(pk=order_id).first()
            if not order_obj:
                res = {'status': False, 'field': 'amount', 'error': '没找到订单号'}
                return JsonResponse(res)

            pay2order_obj = Pay2Orders.objects.filter(payment=inwardpay_obj, order=order_obj).first()

            if pay2order_obj:
                # 如果是更新已经关联记录，看看关联金额的差异，只处理差异部分即可 pay2order中记载的是 dist_amount
                diff_amount = dist_amount - Decimal(pay2order_obj.amount)
                if diff_amount > inwardpay_obj.torelate_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于可分配的金额'})
                if diff_amount*rate > order_obj.collect_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于订单应收金额'})

                pay2order_obj.amount = dist_amount
                pay2order_obj.rate = rate
                order_obj.rcvd_amount = order_obj.rcvd_amount + diff_amount*rate
                inwardpay_obj.torelate_amount = inwardpay_obj.torelate_amount - diff_amount
            else:
                # 如果是新增关联记录
                if dist_amount > inwardpay_obj.torelate_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于可分配的金额'})
                if dist_amount*rate > order_obj.collect_amount:
                    return JsonResponse({'status': False, 'field': 'amount', 'error': '不能大于订单应收金额'})

                pay2order_obj = Pay2Orders(payment=inwardpay_obj, order=order_obj, amount=dist_amount,rate=rate)
                current_number_obj = CurrentNumber.objects.get(pk=1)

                # 给每一个新增的分配记录自动的加上分配编号，同时更新currentnumber_obj
                new_dist_ref = current_number_obj.dist_ref + 1
                while Pay2Orders.objects.filter(dist_ref=new_dist_ref).exists():
                    new_dist_ref += 1
                pay2order_obj.dist_ref = new_dist_ref
                current_number_obj.dist_ref = new_dist_ref
                current_number_obj.save()

                order_obj.rcvd_amount = order_obj.rcvd_amount + dist_amount*rate
                inwardpay_obj.torelate_amount = inwardpay_obj.torelate_amount - dist_amount
            try:
                order_obj.save()

                if inwardpay_obj.torelate_amount == 0:
                    inwardpay_obj.status = 1
                inwardpay_obj.save()
                pay2order_obj.save()

                # 更新订单的已收和应收
                order_payment_update(order_obj=order_obj)

            except Exception as e:
                return JsonResponse({'status': False, 'field': 'amount', 'error': '分配收款失败'})

            return JsonResponse({'status': True, 'msg': '分配收款成功'})

    def transfer(self, request, order_id, *args, **kwargs):
        order_obj = ApplyOrder.objects.filter(pk=order_id).first()

        return render(request, 'dipay/transfer_fix_amount.html', locals())
