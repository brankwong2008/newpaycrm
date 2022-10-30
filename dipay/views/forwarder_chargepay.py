

from stark.service.starksite import StarkHandler,Option
from django.shortcuts import render
from stark.utils.display import PermissionHanlder, get_date_display,get_choice_text
from dipay.utils.displays import ttcopy_display
from django.http import JsonResponse
from dipay.models import PayToCharge,Charge
from dipay.forms.forms import ChargePayModelForm

class ForwarderChargePayHandler(StarkHandler):

    show_detail_template = "dipay/show_chargepay_detail.html"

    has_add_btn =  False

    order_by_list = ['-id','-create_date']

    search_list = ["id__contains", 'create_date']
    search_placeholder = '付费单号 支付日期'

    def amount_display(self, obj=None, is_header=None,*args,**kwargs):
        """  美元金额合计显示  """
        if is_header:
           return "金额"
        else:
            return "%s %s" % (obj.currency.icon , obj.amount)

    def related_charges_display(self,obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "关联账单"
        else:
            queryset = PayToCharge.objects.filter(chargepay_id=obj.pk)
            return  "   ".join([ str(item.charge.followorder)
                                 +"("+item.currency.icon+str(item.amount or '.') +")  "
                                 for item in queryset])

    def charge_id_display(self,obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "付费单号"
        else:

            return  "F%s" % str(obj.pk).zfill(5)

    fields_display = [
        charge_id_display,
        get_date_display("create_date"),
        'bank',
        'forwarder',
        amount_display,
        ttcopy_display,
        related_charges_display,
        "remark",
        get_choice_text("status")
    ]

    def save_form(self, form, request, is_update=False, *args, **kwargs):
        # 上传水单说明实际付款了，可以更新相关表的状态
        if form.instance.ttcopy:
            # 更新付款表时，如果上传水单，则把付款状态改为已出账
            form.instance.status = 1
            # 且同时要把相关联的付费单的状态改变美元已付，人民币已付，或者结清
            print('form.instance:',form.instance.pk)
            # charges_queryset = PayToCharge.objects.filter(chargepay_id=form.instance.pk)
            print(form.instance.currency.title,"currency.title")
            currency_code = 1 if form.instance.currency.title == '美元' else 2
            for item in Charge.objects.filter(chargepay=form.instance):
                # 如果currency与费用表中的状态值相等，说明已经更新过了
                if item.status < 3 and item.status != currency_code:
                    item.status += currency_code
                    item.save()
        form.save()


    def get_model_form(self,type=None):
        return ChargePayModelForm

    # 显示一条记录详情
    def show_detail(self, request, pk, *args, **kwargs):
        # print('pk',pk)
        obj = self.model_class.objects.filter(pk=pk).first()
        data_list = []

        edit_detail_url = self.reverse_edit_url(pk=pk)

        return render(request, self.show_detail_template, locals())


    def get_queryset_data(self,request,is_search=None,*args,**kwargs):
        if request.user.forwarder:
            return self.model_class.objects.filter(forwarder=request.user.forwarder)