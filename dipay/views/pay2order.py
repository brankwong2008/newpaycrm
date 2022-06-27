
from django.shortcuts import HttpResponse,redirect,render,reverse
from django.conf.urls import url
from django.utils.safestring import mark_safe
from django.forms.models import modelformset_factory
from django import forms
from stark.service.starksite import StarkHandler
from stark.utils.display import get_date_display,get_choice_text, PermissionHanlder
from dipay.forms.forms import AddInwardPayModelForm, Inwardpay2OrdersModelForm
from dipay.models import ApplyOrder, Customer, Payer, Pay2Orders

class  Pay2OrdersHandler(PermissionHanlder, StarkHandler):

    def get_del_display(self, obj=None, is_header=False,*args,**kwargs):
        """
        在列表页显示删除按钮，因为多传了一个关键字参数order_id，所以要改一改
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "操作"
        else:
            del_url = self.reverse_del_url(pk=obj.id,*args)

        return mark_safe(" <a href='%s'><i class='fa fa-trash'></i></a>" % (
         del_url))


    def get_relate_amount_display(self, obj=None, is_header=False,*args,**kwargs):
        """
        在列表页显示删除按钮，因为多传了一个关键字参数order_id，所以要改一改
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "关联金额"
        else:
            return "%s %s" % (obj.order.currency.icon, obj.amount )

    def get_payment_display(self, obj=None, is_header=False,*args,**kwargs):
        """
        在列表页显示删除按钮，因为多传了一个关键字参数order_id，所以要改一改
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "款项来源"
        else:
            param = 'pk=%s' % (obj.payment.id)
            payment_origin_url = reverse(self.namespace+":dipay_inwardpay_list")

        return mark_safe(" <a href='%s?%s' target='_blank'> %s </a>" % (payment_origin_url,param, obj.payment ))

    fields_display = ['order',get_relate_amount_display, get_payment_display, get_date_display('relate_date'),]

    has_add_btn = False

    def get_urls(self):
        patterns = [
            #url("^order_related_paylist/(?P<order_id>\d+)/$", self.wrapper(self.order_related_paylist), name=self.get_url_name('order_related_paylist')),
            # url("^list/(?P<order_id>\d+)/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^list/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^edit/(?P<pk>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/$", self.wrapper(self.del_list), name=self.get_del_url_name), ]

        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())

        return patterns


    def get_queryset_data(self, request, *args, **kwargs):
        order_id = request.GET.get('order_id')
        print(self.model_class)
        if order_id:
            return self.model_class.objects.filter(order_id=order_id)
        else:
            return self.model_class.objects.all()