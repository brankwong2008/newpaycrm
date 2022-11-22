from django.shortcuts import HttpResponse, redirect, render
from django.conf.urls import url
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.utils.displays import related_orders_display, ttcopy_display
from dipay.forms.forms import AddInwardPayModelForm, EditInwardPayModelForm
from django.db import transaction

class InwardPayAccountHandler(PermissionHanlder, StarkHandler):
    has_add_btn = False
    show_list_template = 'dipay/show_inwardpay_account.html'
    page_title = "收款管理(财务版)"

    search_list = ['create_date','amount','customer__title__icontains',]
    search_placeholder = '搜索 日期 金额 客户名 '

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
            return "水单金额"
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
        if is_header:
            return "状态"
        else:
            confirm_display_choices = [(0, '请认领'),
                                       (1, '已认领-待确认'),
                                       (2, '待业务-财务确认'),
                                       (4, '待跟单-业务确认'),
                                       (3, '待财务确认'),
                                       (5, '待跟单确认'),
                                       (6, '待业务确认'),
                                       (7, '全部确认'),
                                       ]
            display_text = [item[1] for item in confirm_display_choices if item[0] == obj.confirm_status][0]
            return display_text

    # 财务确认款是否收到
    def receipt_confirm_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '操作'
        else:
            if obj.confirm_status <= 3:
                confirm_url = self.reverse_url('confirm_receipt', pk=obj.pk)
                return mark_safe(
                    "<a href= '%s' class='account-confirm-status-%s btn btn-success btn-sm' pk='%s' "
                    "onclick='return showInwardpayConfirm(this)' > "
                    "确认 </a>" % (confirm_url,obj.pk,obj.pk))
            else:
                return '已收讫'


    # 列显示控制
    fields_display = [get_date_display('create_date'), 'bank', payer_display, customer_display, amount_display,got_amount_display,
                      ttcopy_display, related_orders_display,receipt_confirm_display]

    def get_urls(self):
        patterns = [
            url("^list/$", self.wrapper(self.show_list), name= self.get_list_url_name),
            url("^confirm_receipt/(?P<pk>\d+)/$", self.wrapper(self.confirm_receipt), name=self.get_url_name('confirm_receipt')),
        ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())

        return patterns


    def get_queryset_data(self, request, *args, **kwargs):
        pk = request.GET.get('pk')
        if pk:
            return self.model_class.objects.filter(pk=pk)
        else:
            # return self.model_class.objects.all()
            # 跨表查询就是如此简单，强大的SQL
            return  self.model_class.objects.exclude(orders__order_type=2)


    def confirm_receipt(self, request, pk,  *args, **kwargs):
        obj = self.model_class.objects.filter(pk=pk).first()

        if not obj:
            return render(request, 'dipay/msg_after_submit.html', {'msg': '没有找到收款id'})

        if request.method == 'GET':
            data_list = []
            data_list.append({"label":"编号","data":obj.id})
            data_list.append({"label":"汇入日期","data":obj.create_date.strftime("%Y-%m-%d")})
            data_list.append({"label":"收款银行","data":str(obj.bank)})
            data_list.append({"label":"付款人","data":str(obj.payer)})
            data_list.append({"label":"客户","data":obj.customer})
            data_list.append({"label":"水单金额","data":obj.currency.icon+str(obj.amount)})
            data_list.append({"label":"到账金额","data":obj.currency.icon+str(obj.got_amount)})
            data_list.append({"label":"中间行扣费","data":obj.currency.icon+str(obj.amount-obj.got_amount)})
            data_list.append({"label": "备注", "data": str(obj.remark)})
            return render(request, 'dipay/inwardpayment_detail.html', {'data_list': data_list})

        if request.method == 'POST':
            obj.confirm_status = 7
            obj.save()
            return redirect(self.reverse_list_url())
