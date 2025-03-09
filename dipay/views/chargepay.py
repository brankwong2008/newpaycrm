
import os
import threading
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler,Option
from django.shortcuts import render, HttpResponse,redirect
from stark.utils.display import PermissionHanlder, get_date_display,get_choice_text
from dipay.utils.displays import ttcopy_display,forwarder_display,fee_invoice_display
from django.http import JsonResponse
from dipay.models import PayToCharge,Charge,Forwarder
from dipay.forms.forms import ChargePayModelForm
from django.conf import settings
from django.conf.urls import url
from openpyxl import load_workbook
from rbac.utils.common import compress_image


def update_related_charges(edit_obj):
    currency_code = 1 if edit_obj.currency.title == '美元' else 2
    for item in Charge.objects.filter(chargepay=edit_obj):
        # 如果currency与费用表中的状态值相等，说明已经更新过了
        if item.status < 3 and item.status != currency_code:
            item.status += currency_code
            # 如果只有美元账单或者人民币账单，则结清的要求小于3
            total_USD = item.insurance + item.seafreight

            total_CNY = item.port_charge + item.trailer_charge + item.other_charge
            status_ceiling = 3
            if total_USD <= 0 and total_CNY > 0:
                status_ceiling = 2
            elif total_USD > 0 and total_CNY <= 0:
                status_ceiling = 1
            item.status = 3 if item.status >= status_ceiling else item.status
            item.save()

class ChargePayHandler(PermissionHanlder,StarkHandler):
    page_title = "付费记录"
    show_detail_template = "dipay/show_chargepay_detail.html"
    show_list_template = "dipay/show_chargepay_list.html"

    option_group = [Option(field="forwarder")]
    # 动态指定
    def get_filter_control_list(self):
        return {"forwarder": [each.shortname for each in Forwarder.objects.filter(is_option=True)]}


    search_list = ['id', "create_date"]
    search_placeholder = '搜索 付费单号 日期'

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
            download_url = self.reverse_url("download",pk=obj.pk)
            bills_download_btn = f"<a href='{download_url}'>下载明细</a>"
            return mark_safe( "   ".join([ str(item.charge.followorder)
                                 +"( "+item.currency.icon+str(item.amount or '.') +")  "
                                 for item in queryset]) + bills_download_btn)

    def charge_id_display(self,obj=None, is_header=None,*args,**kwargs):
        if is_header:
            return "付费单号"
        else:

            return  "F%s" % str(obj.pk).zfill(5)

    fields_display = [
        charge_id_display,
        get_date_display("create_date"),
        'bank',
        forwarder_display,
        amount_display,
        get_choice_text("status"),
        ttcopy_display,
        fee_invoice_display,
        related_charges_display,
        "remark",

    ]

    def get_extra_urls(self):
        return [
            url("^download/(?P<pk>\d+)/$", self.wrapper(self.download), name=self.get_url_name('download')),
        ]

    def save_form(self, form, request, is_update=False, *args, **kwargs):
        # 上传水单说明实际付款了，可以更新相关表的状态
        if form.instance.ttcopy:
            # 更新付款表时，如果上传水单，则把付款状态改为已出账
            form.instance.status = 1

            # 更新支付日期为传水单的当日, 这个地方不应该自动，有可能第二天或者第三天传水单，还是应允许用户修改
            # form.instance.create_date = datetime.now()
            # 且同时要把相关联的付费单的状态改变美元已付，人民币已付，或者结清
            update_related_charges(edit_obj=form.instance)

        form.save()

        # 压缩图片ttcopy
        if form.instance.ttcopy:
            t = threading.Thread(target=compress_image, args=(form.instance.ttcopy.path, 800))
            t.start()

        # 压缩图片fee invoice
        if form.instance.fee_invoice:
            t = threading.Thread(target=compress_image, args=(form.instance.fee_invoice.path, 800))
            t.start()

    def get_model_form(self,handle_type=None):
        return ChargePayModelForm

    # 显示一条记录详情
    def show_detail(self, request, pk, *args, **kwargs):
        # print('pk',pk)
        obj = self.model_class.objects.filter(pk=pk).first()
        data_list = []

        edit_detail_url = self.reverse_edit_url(pk=pk)

        return render(request, self.show_detail_template, locals())

    # 下载这笔付款所覆盖的费用单的明细，财务需要打出来做账
    def download(self, request, pk, *args, **kwargs):
        chargepay_obj = self.model_class.objects.filter(pk=pk).first()
        if not chargepay_obj:
            return HttpResponse("付费单号不存在")

        sample_file = os.path.join(settings.MEDIA_ROOT,"paybills", "charge_list_sample.xlsx")

        # 读入sample_file

        wb = load_workbook(sample_file,data_only=True)
        ws = wb.active
        ws["B1"].value = chargepay_obj.forwarder.title
        ws["E1"].value = "F" + str(pk).zfill(5)

        USD_total, CNY_total = 0,0
        for item in PayToCharge.objects.filter(chargepay_id=pk):
            USD_amount,CNY_amount  = 0,0
            print("currency.title:",item.currency.title)
            if item.currency.title =="美元":
                USD_amount = item.amount
                USD_total += USD_amount
            else:
                CNY_amount = item.amount
                CNY_total += CNY_amount
            BL_date = item.charge.BL_date.strftime("%Y-%m-%d")
            remark = item.charge.remark.replace("\n"," ").replace("\t"," ")
            order_number = str(item.charge.followorder)
            row = [BL_date,remark,order_number,USD_amount or "-", CNY_amount or "-"]
            ws.append(row)
        ws.append(["合计","","", USD_total or "-", CNY_total  or "-"])

        file_name = "F%s.xlsx" % (str(pk).zfill(5))
        file_path = os.path.join(settings.MEDIA_ROOT,"paybills", file_name)
        wb.save(file_path)

        with open(file_path, 'rb') as f:
            try:
                response = HttpResponse(f)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="%s"' % (file_name)

                return response
            except Exception as e:
                print(e)
                return HttpResponse("下载失败")

    def edit_list(self, request, pk, *args, **kwargs):
        page_title = self.page_title
        form_class = self.get_model_form("edit")
        edit_obj = self.get_edit_obj(request, pk, *args, **kwargs)
        name_control_list = ["ttcopy","bank","remark"]

        if not edit_obj:
            return HttpResponse("编辑的记录不存在")

        if request.method == "GET":
            form = form_class(instance=edit_obj)
            back_url = self.reverse_list_url(*args, **kwargs)
            namespace = self.namespace
            app_label = self.app_label
            # 自定义列表，外键字段快速添加数据，在前端显示加号
            popup_list = self.popup_list

            # 用户点击水单图标直接上传时，指定get_type为simple，此时只给出上传水单和银行以及备注三个信息即可，其他非必要信息不展示
            get_type = request.GET.get('get_type')
            print("get_type request.method == GET", get_type)
            if get_type == 'simple':
                link = self.reverse_edit_url(pk=edit_obj.pk)
                return render(request, "dipay/upload_payslip_chargepay.html", locals())
            return render(request, "stark/change_list.html", locals())

        if request.method == "POST":
            print("request.POST, request.FILES",request.POST, request.FILES)
            # 列表页面直接上传fee invoice时，前端发起ajax POST，首先由ajax来处理返回JsonResponse
            if request.is_ajax():
                queryparams = self.get_query_param()
                get_type = request.GET.get("get_type")
                if queryparams:
                    querylist = queryparams.split("=")
                    querydict = {querylist[0]:querylist[1]}
                    get_type = querydict.get("get_type")

                if get_type == "simple":
                    edit_obj.bank_id = request.POST.get("bank")
                    edit_obj.remark = request.POST.get("remark")
                    edit_obj.ttcopy = request.FILES.get("ttcopy")
                    # 更新为已付
                    edit_obj.status = 1
                    try:
                        edit_obj.save()
                        update_related_charges(edit_obj)
                        t = threading.Thread(target=compress_image, args=(edit_obj.ttcopy.path, 800))
                        t.start()
                        response = {"status": True, "msg": "水单上传成功"}
                    except:
                        response = {"status": False, "msg": "水单保存失败"}
                    return JsonResponse(response)


                fee_invoice_file = request.FILES.get("fee_invoice")
                if fee_invoice_file:
                    edit_obj.fee_invoice = fee_invoice_file
                    edit_obj.save()
                    response = {"status": True, "msg": "发票信息更新成功"}
                    # 压缩图片
                    t = threading.Thread(target=compress_image, args=(edit_obj.fee_invoice.path, 800))
                    t.start()
                else:
                    response = {"status": False, "msg": "发票信息更新失败"}
                return JsonResponse(response)

            if request.FILES:
                form = form_class(request.POST, request.FILES, instance=edit_obj)
            else:
                form = form_class(instance=edit_obj, data=request.POST)

            if form.is_valid():
                responds = self.save_form(form, request, True, *args, **kwargs)
                return responds or redirect(self.reverse_list_url(*args, **kwargs))
            else:
                print("Form errors:", form.errors)  # 打印表单验证错误信息
                return render(request, self.edit_list_template or "stark/change_list.html", locals())

