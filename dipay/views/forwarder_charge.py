from decimal import Decimal
from django.shortcuts import redirect
from stark.service.starksite import StarkHandler, Option
from django.utils.safestring import mark_safe
from django.shortcuts import reverse, render
from stark.utils.display import PermissionHanlder, get_choice_text, checkbox_display
from dipay.utils.displays import fees_display
from dipay.models import ChargePay, PayToCharge, Currency, FollowOrder
from dipay.forms.forms import ForwarderChargeModelForm


class ForwarderChargeHandler(PermissionHanlder,StarkHandler):
    show_list_template = "dipay/show_charge_list.html"

    page_title = '港杂费用(货代版)'

    order_by_list = ['-BL_date',]

    # 快速筛选： 付费状态
    option_group = [
        Option(field='status'),
    ]

    guideline = mark_safe("<h5>货代费用表的使用：</h5>"
                          "<p>1. 点击右上角蓝色加号添加费用单</p>"
                          "<p>2. 一个订单一条记录</p>"
                          "<p>3. 合计的金额，红色表示没有付，黑色表示已付</p>"
                          "<p>4. 除了保险费，其他费用不能带小数</p>")

    search_list = ['followorder__order__order_number__icontains', "remark__icontains"]

    search_placeholder = '搜索 订单号 费用说明'

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
            return order_number


    def related_chargepay_display(self, obj=None, is_header=None, *args, **kwargs):
        """  显示货代  """
        if is_header:
            return "关联费用单"
        else:
            chargepay_queryset = ChargePay.objects.filter(charge=obj)
            data_list = []

            for item in chargepay_queryset:
                chargepay_url = reverse("stark:dipay_chargepay_list_forwarder") + f"?q={item.pk}"
                tag = f"<a href='{chargepay_url}' target='_blank'>F{str(item.pk).zfill(5)}</a>"
                data_list.append(tag)

            return mark_safe(" ,".join(data_list))


    fields_display = [
        followorder_display,
        ETD_display,
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

    def get_model_form(self,type=None):
        return ForwarderChargeModelForm


    def save_form(self,form,request,is_update=False,*args, **kwargs):
        forwarder_obj = request.user.forwarder
        form.instance.forwarder = forwarder_obj
        form.save()


    # 限定每个货代只能看到只能的费用单记录
    def get_queryset_data(self,request,is_search=None,*args,**kwargs):
        if request.user.forwarder:
            return self.model_class.objects.filter(forwarder=request.user.forwarder)
