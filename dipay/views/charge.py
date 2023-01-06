from decimal import Decimal
from datetime import datetime
from django.shortcuts import redirect
from stark.service.starksite import StarkHandler, Option
from django.utils.safestring import mark_safe
from django.shortcuts import reverse, render
from stark.utils.display import PermissionHanlder, get_date_display, get_choice_text, checkbox_display_func
from django.conf.urls import url
from django.http import JsonResponse
from dipay.utils.tools import str_width_control
from dipay.utils.displays import fees_display, forwarder_display
from dipay.models import ChargePay, PayToCharge, Currency, FollowOrder, Forwarder


class ChargeHandler(PermissionHanlder,StarkHandler):
    show_list_template = "dipay/show_charge_list.html"

    page_title = '货代费用'

    order_by_list = ['-BL_date',]

    # 快速筛选： 货代，付费状态
    option_group = [
        Option(field='forwarder',
               is_multi=False,
               # control_list=['汇昌','迪斯泰','誉洲','永鑫海','惠和','深圳鑫顺源',]  # 静态指定
               ),
        Option(field='status'),
    ]

    # 动态指定
    def get_filter_control_list(self):
        return {"forwarder": [each.shortname for each in Forwarder.objects.filter(is_option=True)]}


    search_list = ['followorder__order__order_number__icontains',]

    search_placeholder = '搜索 订单号'

    # 添加和修改ModelForm的外键字段快速添加记录
    popup_list = ['forwarder', ]

    # 生成付费单
    def batch_pay(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')

        print('batch pay args:', request.POST, args, kwargs)
        pk_list = request.POST.getlist("pk")
        forwarder_id = request.POST.get("forwarder_id")
        USD_amount = request.POST.getlist("USD_amount")
        CNY_amount = request.POST.getlist("CNY_amount")
        if not USD_amount and not CNY_amount:
            return JsonResponse({"status": False, "msg": '至少选择一项费用金额'})


        # 创建付款单记录， 水单，银行等字段后续再填写
        amount_list = USD_amount or CNY_amount
        total_amount = sum([Decimal(each) for each in amount_list])
        currency = Currency.objects.get(title='美元') if USD_amount else Currency.objects.get(title='人民币')

        # 生成付费单(草稿)
        chargepay_obj = ChargePay(create_date=datetime.now(),forwarder_id=forwarder_id, currency=currency, amount=total_amount)


        paytocharge_list = []
        for ind, val in enumerate(pk_list):
            # 第一步需要查重，并告知前端哪笔是重复的
            if PayToCharge.objects.filter(charge_id=val,currency=currency).exists():
                order_number = self.model_class.objects.get(pk=val).followorder.order.order_number
                msg = f"订单{order_number}的{currency.title}费用有可能重复支付"
                return JsonResponse({"status": False, "msg": msg,})

            # 创建付费单-费用单关联记录
            paytocharge_obj = PayToCharge(
                                          charge_id=val,
                                          chargepay=chargepay_obj,
                                          currency=currency,
                                          amount=amount_list[ind])
            paytocharge_list.append(paytocharge_obj)

        chargepay_obj.save()
        PayToCharge.objects.bulk_create(paytocharge_list)

        chargepay_url = reverse("stark:dipay_chargepay_list")
        return JsonResponse({"status": True, "msg": '付费单生成成功','url': chargepay_url})

    batch_pay.text = "生成付费单"

    batch_process_list = [batch_pay, ]

    def check_pay_status(self, obj, currency_code):
        """  检查某项费用是否已付，并标识状态  """
        if obj.status == 0:
            return False
        if obj.status == 3:
            return True
        return obj.status % 2 == currency_code


    def total_USD(self, obj=None, is_header=None, *args, **kwargs):
        """  美元金额合计显示  """
        if is_header:
            return "美元合计"
        else:
            is_paid = self.check_pay_status(obj,1)
            total_amount = obj.seafreight + obj.insurance
            if total_amount == 0:
                return "-"
            if is_paid:
                res = mark_safe("<span class='money status-paid'>$</span><span class='status-paid' name='USD_amount'>%s</span>" % (total_amount))
            else:
                res = mark_safe("<span class='money status-unpaid'>$</span><span class='status-unpaid' pk='%s' name='USD_amount' "
                          "onclick='addToPayCharge(this)'>%s</span>" % (obj.pk, total_amount))
            return res

    def total_CNY(self, obj=None, is_header=None, *args, **kwargs):
        """  美元金额合计显示  """
        if is_header:
            return "人民币合计"
        else:
            is_paid = self.check_pay_status(obj, 0)
            total_amount = obj.port_charge + obj.trailer_charge + obj.other_charge
            if total_amount == 0:
                return "-"

            if is_paid:
                res = mark_safe("<span class='money status-paid'>￥</span><span class='status-paid' name='CNY_amount'>%s</span>" % (total_amount))
            else:
                res = mark_safe("<span class='money status-unpaid'>￥</span><span class='status-unpaid' pk='%s' name='CNY_amount' "
                          "onclick='addToPayCharge(this)'>%s</span>" % (obj.pk, total_amount))
            return res

    def ETD_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "提单日"
        else:
            if obj.BL_date:
                return obj.BL_date.strftime("%Y-%m-%d")
            else:
                return "-"

    def followorder_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "跟单号"
        else:
            order_number = obj.followorder.order.order_number
            followorder_url = reverse("stark:dipay_followorder_list") + "?q=%s" % order_number
            return mark_safe(f"<a href='{followorder_url}' target='_blank' class='normal-a'>{order_number}</a>")


    def related_chargepay_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "关联付款单"
        else:
            chargepay_queryset = ChargePay.objects.filter(charge=obj)
            data_list = []

            for item in chargepay_queryset:
                chargepay_url = reverse("stark:dipay_chargepay_list")+f"?q={item.pk}"
                tag = f"<a href='{chargepay_url}' target='_blank'>F{str(item.pk).zfill(5)}</a>"
                data_list.append(tag)

            return mark_safe(" ,".join(data_list))


    fields_display = [
        checkbox_display_func(hidden_xs="hidden-md hidden-lg"),
        ETD_display,
        followorder_display,
        forwarder_display,
        # fees_display("seafreight"),
        # fees_display("insurance"),
        # fees_display("port_charge"),
        # fees_display("trailer_charge"),
        # fees_display("other_charge"),
        "remark",
        total_USD,
        total_CNY,
        related_chargepay_display,
        get_choice_text("status"),
    ]

    def get_extra_urls(self):
        patterns = [
            url("^pop_detail/(?P<followorder_id>\d+)/$", self.wrapper(self.pop_detail),
                name=self.get_url_name('pop_detail')),
        ]

        return patterns

    # 跟单页面弹出费用明细的view
    def pop_detail(self, request, followorder_id, *args, **kwargs):
        data_list = self.model_class.objects.filter(followorder_id=followorder_id)
        charge_list = []
        # 添加按钮
        add_url = self.reverse_add_url() + "?followorder_id=%s" % followorder_id
        add_btn = mark_safe("<a href='%s' target='_blank' class='btn btn-primary add-record'> + </a>" % add_url)

        for each in data_list:
            row = {}
            row["forwarder"] = each.forwarder.shortname
            row["data"] = []
            row["total"]=[]
            total_USD, total_CNY = Decimal(0), Decimal(0)
            total_USD, total_CNY = 0, 0
            for name in ['seafreight', 'insurance', 'port_charge', 'trailer_charge', 'other_charge']:
                if getattr(each, name):
                    verbose_name = self.model_class._meta.get_field(name).verbose_name
                    if verbose_name.endswith('$'):
                        total_USD += Decimal(getattr(each, name))
                        print('total_USD',total_USD)
                    else:
                        total_CNY += Decimal(getattr(each, name))
                        print('total_CNY', total_USD)

                    status = getattr(each, "status")
                    is_paid = ""
                    if status == 1 and verbose_name.endswith('$'):
                        is_paid = 'paid'
                    if status == 2 and verbose_name.endswith('￥'):
                        is_paid = 'paid'
                    if status == 3:
                        is_paid = 'paid'
                    row["data"].append({"label": verbose_name, "text": getattr(each, name), "is_paid": is_paid})
            row["total"].extend([{"label":"美元合计:","text":total_USD},{"label":"人民币合计:","text":total_CNY}])
            print("row['total']",row["total"])
            charge_list.append(row)

        return render(request, 'dipay/simple_charges_list.html', locals())

    # 新增一条记录
    def add_list(self, request, *args, **kwargs):
        if request.method == "GET":
            followorder_id = request.GET.get("followorder_id")
            form = self.get_model_form("add")()
            print("form",form)
            if followorder_id:
                followorder_obj = FollowOrder.objects.get(pk=followorder_id)
                form.fields['followorder'].initial= followorder_obj
                if followorder_obj.ETD:
                    form.fields['BL_date'].initial = followorder_obj.ETD
            namespace = self.namespace
            app_label = self.app_label
            popup_list = self.popup_list
            return render(request, self.add_list_template or "stark/change_list.html", locals())

        if request.method == "POST":
            form = self.get_model_form("add")(request.POST, request.FILES)

            if form.is_valid():
                result = self.save_form(form, request, False, *args, **kwargs)
                return result or redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, self.add_list_template or "stark/change_list.html", locals())

