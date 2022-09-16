from django.shortcuts import HttpResponse, redirect, render
from django.conf.urls import url
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.utils.displays import related_orders_display
from dipay.forms.forms import AddInwardPayModelForm, EditInwardPayModelForm
from django.db import transaction

class InwardPayAccountHandler(PermissionHanlder, StarkHandler):
    has_add_btn = False
    show_list_template = 'dipay/show_inwardpay_account.html'

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

    def ttcopy_display(self,obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '水单'
        else:
            if obj.ttcopy:
                img_tag = f"<img class='ttcopy-small-img' src={obj.ttcopy.url} " \
                          f"onclick='return popupImg(this)' width='30px' height='30px'>"
            else:
                img_tag = '<i class="fa fa-minus-square"></i>'


            return mark_safe(img_tag)

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
            # url("^list_detail/(?P<pk>\d+)/$", self.wrapper(self.show_detail), name= self.get_url_name('show_detail')),
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
        inwardpay_obj = self.model_class.objects.filter(pk=pk).first()
        if not inwardpay_obj:
            return render(request, 'dipay/msg_after_submit.html', {'msg': '没有找到收款id'})

        if request.method == 'GET':
            return render(request, 'dipay/inwardpayment_detail.html', {'inwardpay_obj': inwardpay_obj})

        if request.method == 'POST':
            inwardpay_obj.confirm_status = 7
            inwardpay_obj.save()
            return redirect(self.reverse_list_url())
