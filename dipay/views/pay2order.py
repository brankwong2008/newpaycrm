
from django.shortcuts import HttpResponse,redirect,render,reverse
from django.conf.urls import url
from django.utils.safestring import mark_safe
from django import forms
from stark.service.starksite import StarkHandler
from stark.utils.display import get_date_display,get_choice_text, PermissionHanlder
from dipay.models import Pay2Orders, CurrentNumber

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


    def get_urls(self):
        patterns = [
            #url("^order_related_paylist/(?P<order_id>\d+)/$", self.wrapper(self.order_related_paylist), name=self.get_url_name('order_related_paylist')),
            # url("^list/(?P<order_id>\d+)/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^list/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^edit/(?P<pk>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/$", self.wrapper(self.del_list), name=self.get_del_url_name),
            url("^add/$", self.wrapper(self.add_list), name=self.get_add_url_name),

        ]

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


    def save_form(self,form,request,is_update=False,*args, **kwargs):
        if is_update:
            form.save()
        else:
            current_number_obj = CurrentNumber.objects.get(pk=1)
            # 给每一个新增的分配记录自动的加上分配编号，同时更新currentnumber_obj
            new_dist_ref = current_number_obj.dist_ref + 1
            while Pay2Orders.objects.filter(dist_ref=new_dist_ref).exists():
                new_dist_ref += 1
            form.instance.dist_ref = new_dist_ref
            form.save()
            current_number_obj.dist_ref = new_dist_ref
            current_number_obj.save()

        # 同时更新订单和收款记录
        order_obj = form.instance.order
        order_obj.rcvd_amount = sum([item.amount for item in Pay2Orders.objects.filter(order=order_obj)])
        order_obj.collect_amount = order_obj.amount - order_obj.rcvd_amount
        order_obj.save()

        payment_obj = form.instance.payment
        related_amount = sum([item.amount for item in Pay2Orders.objects.filter(payment=payment_obj)])
        payment_obj.torelate_amount = payment_obj.amount - related_amount
        payment_obj.save()

