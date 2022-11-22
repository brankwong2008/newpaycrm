from django.shortcuts import HttpResponse, redirect, render, reverse
from decimal import Decimal
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


class ApplyReleaseHandler(PermissionHanlder, StarkHandler):
    has_add_btn = False

    page_title = "放单管理"

    order_by_list = ['-apply_date']

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
    def decision_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '审批结果'
        else:
            if obj.decision is None:
                return mark_safe("<span class='wait-confirm-release'>等待审批</span>")
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


    fields_display = [get_date_display('apply_date'), order_number_display, customer_display, 'applier',
                      'verifier',apply_content_display, decision_display, ]

    detail_fields_display = fields_display

    def get_urls(self):
        patterns = [
            url("^list/$", self.wrapper(self.show_list), name= self.get_list_url_name),
        ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())
        return patterns
