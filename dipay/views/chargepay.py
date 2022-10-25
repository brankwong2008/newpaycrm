

from stark.service.starksite import StarkHandler,Option
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from stark.utils.display import PermissionHanlder, get_date_display
from dipay.utils.displays import ttcopy_display
from django.conf import settings
from django.http import JsonResponse
from dipay.utils.tools import str_width_control
from dipay.models import PayToCharge

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

    ]

