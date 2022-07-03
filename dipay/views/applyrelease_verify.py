from django.shortcuts import HttpResponse, redirect, render, reverse
from datetime import datetime
from django.http import JsonResponse
from django.conf.urls import url
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory, formset_factory
from django import forms
from stark.service.starksite import StarkHandler
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.forms.forms import AddInwardPayModelForm, Inwardpay2OrdersModelForm, ConfirmInwardpayModelForm, \
    EditInwardPayModelForm
from dipay.models import ApplyOrder, FollowOrder, Payer, Pay2Orders, Inwardpay, CurrentNumber
from django.db import transaction


class ApplyReleaseVerifyHandler(PermissionHanlder, StarkHandler):

    def get_urls(self):
        patterns = [
            url("^list/$", self.wrapper(self.show_list), name= self.get_list_url_name),
            url("^verify/(?P<order_id>\d+)/$", self.wrapper(self.verify_release), name=self.get_url_name('verify_release')),
        ]
        return patterns

    # 审批项目明细和批准
    def verify_release(self,request, order_id, *args, **kwargs):
        order_obj = ApplyOrder.objects.filter(pk=order_id).first()
        applyrelease_obj = self.model_class.objects.filter(order=order_obj).first()
        pay2order_list = Pay2Orders.objects.filter(order=order_obj)
        if request.method == "GET":
            return render(request,'dipay/verify_release_order.html', locals())

        if request.method == "POST":
            print(request.POST)
            is_agree = request.POST.get('is_agree')
            remark = request.POST.get('remark')
            if is_agree == "True":
                msg = '同意放单，审批成功'
                applyrelease_obj.decision = True
                applyrelease_obj.verify_date = datetime.now()
            else:
                msg = '不同意放单，审批完成'
                applyrelease_obj.decision = False
            applyrelease_obj.remark = remark
            applyrelease_obj.save()
            return render(request,'dipay/msg_after_submit.html',locals())

    has_add_btn = False

    # 订单金额显示
    def amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return "发票金额"
        else:
            return "%s %s" % (obj.order.currency.icon, obj.order.amount)

    # 客户的显示
    def customer_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '客户'
        else:
            if obj.order.customer:
                return obj.order.customer.shortname
            return '-'

    # 订单号显示
    def order_number_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '订单号'
        else:
            if obj.order.order_number:
                return obj.order.order_number
            return '-'

    # 审批意见显示
    def verify_status_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '审批状态'
        else:
            if obj.decision is None:
                return mark_safe("<span class='wait-confirm'>等待审批</span>")
            elif obj.decision is False:
                return  mark_safe("<span class='not-agree-release'>不同意放单</span>")
            else:
                return  mark_safe("<span class='agree-release'>可以放单</span>")

    # 审批事项显示
    def apply_content_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '申请事项'
        else:
            return '申请放单'

        # 审批事项显示

    # 审批操作
    def operate_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '操作'
        else:
            if obj.decision is None:
                verify_url = self.reverse_url('verify_release', order_id=obj.order.pk)
                return mark_safe("<a href='%s'>审核</a>" % verify_url)
            else:
                return '已审'


    fields_display = [get_date_display('apply_date'), order_number_display, customer_display, 'applier',
                      'verifier',apply_content_display, verify_status_display, operate_display]

    detail_fields_display = fields_display

