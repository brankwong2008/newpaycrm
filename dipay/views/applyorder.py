import os
from datetime import datetime
from django.shortcuts import HttpResponse, redirect, render, reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, get_choice_text, PermissionHanlder
from dipay.forms.forms import AddApplyOrderModelForm, EditApplyOrderModelForm,ConfirmApplyOrderModelForm,ManualAddApplyOrderModelForm
from dipay.models import CurrentNumber, Customer, FollowOrder,ApplyOrder
from openpyxl import load_workbook
from django.conf.urls import url
from django.db import transaction




class ApplyOrderHandler(PermissionHanlder, StarkHandler):
    # 自定义列表，外键字段快速添加数据，在前端显示加号
    popup_list = ['customer', ]

    # 加入一个组合筛选框
    option_group = [
        Option(field='status'),
        # Option(field='depart'),
    ]

    # 模糊搜索
    search_list = ['customer__title__icontains', 'goods__icontains', 'order_number__icontains']
    search_placeholder = '搜索 客户/货品/订单号'

    # 添加按钮
    has_add_btn = False

    # 排序字段
    order_by_list = ['-sequence', ]

    def rcvd_amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '已收款'
        else:
            payments_url_name = "%s:%s" % (self.namespace, 'dipay_pay2orders_list')
            payments_url = reverse(payments_url_name, kwargs={'order_id': obj.id})
            return mark_safe("<a href=%s target='_blank'> %s </a>" % (payments_url, obj.rcvd_amount))

    def amount_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '发票金额'
        else:
            amount_text = "%s %s" % (obj.currency.icon, obj.amount)
            return amount_text

    def order_number_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '发票号'
        else:
            if obj.status == 0:
                return obj.order_number[0] + "____"
            else:
                return obj.order_number

    def status_display(self, obj=None, is_header=False, *args, **kwargs):
        """
               显示币种和金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '状态'
        else:
            if obj.status == 0:
                return mark_safe("<span style='color:red'> %s </span>" % obj.get_status_display())
            else:
                return obj.get_status_display()

    def edit_display(self, obj=None, is_header=False, *args, **kwargs):
        """
        在列表页显示编辑按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "操作"
        else:
            edit_url = self.reverse_edit_url(pk=obj.id)
            if obj.status == 0:
                return mark_safe("<i class='fa fa-edit'></i>")
            else:
                return mark_safe("<a href='%s'><i class='fa fa-edit'></i></a>" % edit_url)

    def to_workshop_display(self, obj=None, is_header=False, *args, **kwargs):
        """
        在列表页显示编辑按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "下单"
        else:
            if obj.status == 1:
                confirm_url = self.reverse_url('to_workshop',pk=obj.id)
                return mark_safe("<a href='%s'>下单</a>" % confirm_url)
            else:
                return '-'

    fields_display = [get_date_display('create_date'),
                      'salesperson', order_number_display,
                      'customer', 'goods', amount_display,
                      status_display, to_workshop_display,
                      rcvd_amount_display]

    def get_model_form(self, handle_type=None):
        if handle_type == 'add':
            return AddApplyOrderModelForm
        if handle_type == 'edit':
            return EditApplyOrderModelForm
        else:
            return ManualAddApplyOrderModelForm

    def get_queryset_data(self, request, *args, **kwargs):
        if request.user.username == 'brank':
            return self.model_class.objects.all()
        if request.user:
            return self.model_class.objects.filter(salesperson=request.user, status__lte=3)
        return self.model_class.objects.all()

    def get_per_page(self):
        return 10

    def add_list(self, request, *args, **kwargs):
        """ 申请/添加订单号  """
        if request.method == "GET":
            form = self.get_model_form("add")()
            # 限定在客户选项里面，业务员只能看到自己的客户
            choices = [(None, '----------'), ]
            for item in Customer.objects.filter(owner=request.user).values('id', 'title'):
                choices.append((item['id'], item['title']))
            form.fields['customer'].choices = choices

            back_url = self.reverse_list_url()
            return render(request, "dipay/apply_new_order.html", locals())

        if request.method == "POST":
            form = self.get_model_form("add")(data=request.POST)

            if form.is_valid():
                result = self.save_form(form, request, False, *args, **kwargs)

                return result or redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, self.add_list_template or "stark/apply_new_order.html", locals())

    def save_form(self, form, request, is_update=False, *args, **kwargs):
        order_type = form.instance.get_order_type_display()
        # order_number 只显示订单类型
        # 编辑情况直接save
        if is_update:
            order_type = form.instance.get_order_type_display()
            sub_sequence = form.instance.sub_sequence
            order_number = "%s%s" % (order_type, form.instance.sequence)
            if sub_sequence != 0:
                order_number = "%s-%s" % (order_number, sub_sequence)
            form.instance.order_number = order_number
            form.instance.collect_amount = form.instance.amount - form.instance.rcvd_amount
            form.save()
            msg = '订单信息更新成功'
            print('msg:', msg)

            return redirect(self.reverse_list_url())

        # 新增订单的情况下

        # 获取当前最新订单序号，并把新申请订单号置为：最新单号+1
        current_num_obj = CurrentNumber.objects.get(pk=1)
        form.instance.sequence = current_num_obj.num + 1

        form.instance.order_number = "%s%s" % (order_type, form.instance.sequence)
        # 应收初始金额等于订单金额
        form.instance.collect_amount = form.instance.amount

        # 如果是添加新订单，则同步更新最新订单号
        if request.user:
            form.instance.salesperson = request.user
        else:
            return HttpResponse('请先登录')

        form.save()

        # 同步更新最新订单号
        current_num_obj.num += 1
        current_num_obj.save()
        msg = '订单号申请提交成功，等待部门经理审核'

        return render(request, 'dipay/msg_after_submit.html', {'msg': msg})

    def get_extra_urls(self):
        patterns = [
            url("^upload/$", self.wrapper(self.upload), name=self.get_url_name('upload')),
            url("^download/(?P<file_name>.*)/$", self.wrapper(self.download), name=self.get_url_name('download')),
            url("^to_workshop/(?P<pk>\d+)/$", self.wrapper(self.to_workshop), name=self.get_url_name('to_workshop')),
            url("^manual_add/$", self.wrapper(self.manual_add), name=self.get_url_name('manual_add')),
        ]
        return patterns

    #  批量上传订单信息
    def upload(self, request, *args, **kwargs):
        print(request.POST, request.FILES)

        if request.method == "GET":
            download_file_url = self.reverse_url('download', file_name='订单导入模板.xlsx')
            return render(request, 'dipay/upload_orders.html', locals())

        if request.method == "POST":
            upload_file = request.FILES.get('upload_file')
            if upload_file is None:
                return HttpResponse('文件不存在')
            print('yes upload', upload_file)
            # 存储文件
            file_path = os.path.join("media/", upload_file.name)

            # 存入media文件夹
            with open(file_path, "wb") as f:
                for line in upload_file:
                    f.write(line)

            # 读取excel文件
            excel_file = load_workbook(file_path)
            ws = excel_file.active
            count = 0

            # 遍历每行，获取每一行信息
            # 存储字段名
            field_list = []
            for i,field in enumerate(ws[1]):
                if field.value:
                    field_list.append((i,field.value))

            print('field list:',field_list)

            for row in ws.iter_rows(2):
                # 用户存储每一行的数据
                data_dict = {}
                # 查询系统里面是否有该订单号
                for num, field in field_list:
                    if row[num].value:
                        data_dict[field] = row[num].value

                invoice_number = data_dict.pop('order')
                order_obj = FollowOrder.objects.filter(order__order_number=invoice_number).first()
                if not order_obj:
                    continue

                # 把数据存入跟单对象记录
                for field,val in data_dict.items():
                    setattr(order_obj,field,val)

                # order_obj.save()
                count += 1

            return HttpResponse('成功上传 %s 条数据 ☺' % count)


    # 下载上传用的模板文件
    def download(self, request, file_name, *args, **kwargs):
        print(request.POST, request.FILES, file_name)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        with open(file_path, 'rb') as f:
            try:
                response = HttpResponse(f)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="%s"' % ('template_file.xlsx')

                return response
            except Exception as e:
                print(e)
                return HttpResponse("下载失败")

    #  下单
    def to_workshop(self, request, pk, *args, **kwargs):
        print(request.POST, )
        order_obj = self.model_class.objects.filter(pk=pk).first()
        if not order_obj:
            return HttpResponse('订单号不存在')

        if request.method == "GET":
            form = ConfirmApplyOrderModelForm(instance=order_obj,initial={'confirm_date':datetime.now()})
            return render(request, 'dipay/confirm_order.html', locals())
        else:
            form = ConfirmApplyOrderModelForm(request.POST, instance=order_obj)
            if form.is_valid():
                # 下单的动作1，把订单状态变为已下单
                form.instance.status = 2
                # 下单的动作2，把下单日期改为当日
                if not form.instance.confirm_date:
                    form.instance.confirm_date =  datetime.now()
                # 下单的动作3，创建一条新的跟单记录
                FollowOrder.objects.create(order=order_obj)

                form.save()
                msg = '下单成功, 请将PI, 生产单，水单，唛头文件等邮件发到工厂跟单'
                return render(request, 'dipay/msg_after_submit.html', locals())
            else:
                return render(request, 'dipay/confirm_order.html', locals())

    # 手动创建订单
    def manual_add(self, request, *args, **kwargs):
        """ 手动创建订单  """
        if request.method == "GET":
            form = self.get_model_form("manual_add")()

            back_url = self.reverse_list_url()
            return render(request, "dipay/manual_add_new_order.html", locals())

        if request.method == "POST":
            form = self.get_model_form("manual_add")(data=request.POST)

            if form.is_valid():
                order_number = form.instance.order_number
                raw_data = [ item.strip() for item in order_number.split('-')]
                if len(raw_data)==1:
                    order_type = raw_data[0][0]
                    sequence = raw_data[0][1:5]
                    sub_sequence = 0
                    order_number = "%s%s" % (order_type, sequence)
                else:
                    order_number,sub_sequence = raw_data
                    order_type = order_number[0]
                    sequence = order_number[1:5]
                    order_number = "%s%s-%s" % (order_type,sequence,sub_sequence)
                # 获取订单类型列表，并转换为字典
                type_choices = { item[1]:item[0] for item in self.model_class.type_choices }

                form.instance.order_type = type_choices.get(order_type)
                form.instance.order_number = order_number
                form.instance.sequence = sequence
                form.instance.sub_sequence = sub_sequence
                try:
                    # 使用事务，避免数据不一致
                    with transaction.atomic():
                        apply_obj = form.save()
                        apply_obj.validate_unique()
                        # 同时创建跟单记录
                        follow_order_obj = FollowOrder(order=apply_obj,status=1)
                        follow_order_obj.save()

                    msg = '手动创建%s成功，同时生成了跟单记录，请查看跟单表' % apply_obj
                except Exception as e:
                    print(e)
                    msg = '创建失败，可能已经存在同样的单号'
                return render(request,'dipay/msg_after_submit.html',locals())
            else:
                return render(request, "dipay/manual_add_new_order.html", locals())

    # 上传之订单号预处理
    def order_number_process(self, order_number):
        order_number = order_number.strip()
        type_choices = ApplyOrder.type_choices
        order_type = [item[0] for item in type_choices if item[1] == order_number[0]][0]
        sequence = order_number[1:5]
        sub_sequence = 0 if len(order_number.split('-')) < 2 else order_number.split('-')[-1]
        return order_type, sequence, sub_sequence