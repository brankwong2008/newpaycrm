

from stark.service.starksite import StarkHandler,Option
from stark.utils.display import PermissionHanlder, get_date_display,get_choice_text
from dipay.utils.displays import ttcopy_display
from django.http import JsonResponse
from dipay.models import PayToCharge
from dipay.forms.forms import ChargePayModelForm

class ChargePayHandler(StarkHandler):

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


    fields_display = [
        "id",
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
        # 更新付款表时，如果上传水单，则把付款状态改为已出账
        if form.instance.ttcopy:
            form.instance.status = 1
        form.save()


    def get_model_form(self,type=None):
        return ChargePayModelForm

