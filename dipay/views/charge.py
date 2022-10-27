from decimal import Decimal
from django.shortcuts import redirect
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text
from django.utils.safestring import mark_safe
from django.shortcuts import reverse, render
from stark.utils.display import PermissionHanlder, get_date_display, get_choice_text, checkbox_display
from django.conf.urls import url
from django.http import JsonResponse
from dipay.utils.tools import str_width_control
from dipay.utils.displays import fees_display
from dipay.models import ChargePay, PayToCharge, Currency, FollowOrder


class ChargeHandler(StarkHandler):
    show_list_template = "dipay/show_charge_list.html"

    order_by_list = ['-followorder__ETD',]

    # 快速筛选： 货代，付费状态
    option_group = [
        Option(field='forwarder', is_multi=False),
        Option(field='status'),
    ]

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
        chargepy_obj = ChargePay(forwarder_id=forwarder_id, currency=currency, amount=total_amount)
        chargepy_obj.save()

        # 创建付款单与费用单之间的关联记录
        for ind, val in enumerate(pk_list):
            paytocharge_obj = PayToCharge(charge_id=val,
                                          chargepay=chargepy_obj,
                                          currency=currency,
                                          amount=amount_list[ind])
            paytocharge_obj.save()

        return JsonResponse({"status": True, "msg": '付费单生成成功'})

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
                res = mark_safe("<span class='status-paid' name='USD_amount'>%s</span>" % (total_amount))
            else:
                res = mark_safe("<span class='status-unpaid' pk='%s' name='USD_amount' "
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
                res = mark_safe("<span class='status-paid' name='CNY_amount'>%s</span>" % (total_amount))
            else:
                res = mark_safe("<span class='status-unpaid' pk='%s' name='CNY_amount' "
                          "onclick='addToPayCharge(this)'>%s</span>" % (obj.pk, total_amount))
            return res

    def forwarder_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "货代"
        else:
            return mark_safe("<span pk='%s' forwarder_id='%s' name='forwarder'>%s</span>" %
                             (obj.pk, obj.forwarder_id, obj.forwarder.shortname))

    def ETD_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "提单日"
        else:
            if obj.followorder.ETD:
                return obj.followorder.ETD.strftime("%Y-%m-%d")
            else:
                return "-"

    def followorder_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "跟单号"
        else:
            order_number = obj.followorder.order.order_number
            followorder_url = reverse("stark:dipay_followorder_list") + "?q=%s" % order_number
            return mark_safe(f"<a href='{followorder_url}' target='_blank'>{order_number}</a>")




    fields_display = [
        checkbox_display,
        ETD_display,
        followorder_display,
        forwarder_display,
        fees_display("seafreight"),
        fees_display("insurance"),
        fees_display("port_charge"),
        fees_display("trailer_charge"),
        fees_display("other_charge"),
        "remark",
        total_USD,
        total_CNY,
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
            print("followorder_id",followorder_id)
            if followorder_id:
                followorder_obj = FollowOrder.objects.get(pk=followorder_id)
                print("charge py: followorder_obj:", followorder_obj)
                form.fields['followorder'].initial= followorder_obj
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

