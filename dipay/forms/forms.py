from django.forms import ModelForm
from django import forms
from dipay.models import ApplyOrder, Inwardpay, Currency, FollowOrder, \
    DailyPlan, FollowChance, Chance, ChargePay, Charge
from datetime import datetime
from dipay.models import ProductPhoto



# 自定义的通用modelForm
class StarkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                # 给外键字段添加搜索功能，前端一定要加载bootstap-select.js
                field.widget.attrs["class"] = "selectpicker bla bli form-control"
                field.widget.attrs["style"] = "display: none;"
                field.widget.attrs["data-live-search"] = 'true'
                model_name = field.queryset.first()._meta.model_name
                field.help_text = model_name  # 获取关联model的名称，通过help_text传递给前端
                continue

            field.widget.attrs["class"] = " form-control"

            if isinstance(field, forms.DateField):
                # print("yes, this is datefield, field",field,field.label)
                field.widget = forms.DateInput(attrs={ "required":True,"type":"date","class":"form-control"})

    def update_choices(self,field,choices):
        self.fields[field].choices = choices


# 用于添加任务的model form
class TaskAddModelForm(forms.ModelForm):
    class Meta:
        model = DailyPlan
        fields = ["content", "remind_date",'cc']
        widgets = {
            'content': forms.TextInput(attrs={'id': 'task_input'}),
            'remind_date': forms.DateInput(attrs={ "required":False,"type":"date",}),
            'cc': forms.Select(attrs={ "required":False,
                                       "size":"3",
                                       "multiple":"",
                                       "class":"selectpicker bla bli form-control",
                                       "style":"display: none;",
                                       "data-live-search":"true",
                                       }),
        }

    def __init__(self, *args, **kwargs):
        super(TaskAddModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            print(name, field)
            if name != 'cc':
                field.widget.attrs["class"] = "form-control"

    def update_choices(self,field,choices):
        self.fields[field].choices = choices



# 用于编辑任务的model form
class TaskEditModelForm(forms.ModelForm):
    class Meta:
        model = DailyPlan
        fields = "__all__"
        exclude = ["link",  ]

    def __init__(self, *args, **kwargs):
        super(TaskEditModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"




class AddApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = ['order_type', 'customer', 'goods', 'term', 'currency', 'amount', 'remark', 'discharge_port']
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'customer': forms.Select(attrs={'required':True}),
            "amount": forms.TextInput(attrs={'oninput':'justifyNumberInput(this)'}),

        }



class EditApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = '__all__'
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            # 'create_date': forms.DateInput(attrs={'type': 'date'}),
            'order_number': forms.TextInput(attrs={'readonly': True}),
            'rcvd_amount': forms.TextInput(attrs={'readonly': True}),
            'collect_amount': forms.TextInput(attrs={'readonly': True}),
            "amount": forms.TextInput(attrs={'oninput':'justifyNumberInput(this)'}),
            'customer': forms.Select(attrs={'data-live-search': 'true',
                                            'style': "display: none;",
                                            'class':'selectpicker bla bli form-control',
                                            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name,field in self.fields.items():
            if isinstance(field,forms.ModelChoiceField):
                model_name = field.queryset.first()._meta.model_name
                field.help_text = model_name

class ConfirmApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = ['confirm_date','order_number','sub_sequence','customer','goods','discharge_port','currency','amount','remark']

        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            # 'create_date': forms.DateInput(attrs={'type': 'date'}),
            'confirm_date': forms.DateInput(attrs={'type': 'date'}),
            'order_number': forms.TextInput(attrs={'readonly': True}),
            'customer': forms.Select(attrs={'readonly': True}),
            "amount": forms.TextInput(attrs={'oninput': 'justifyNumberInput(this)'}),
        }


class ManualAddApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = ['confirm_date', 'order_number', 'salesperson','customer', 'goods', 'currency', 'amount', 'remark']

        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'customer': forms.Select(attrs={'required': True}),
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            'confirm_date': forms.DateInput(attrs={'type': 'date'}),

        }


class EditFollowOrderModelForm(StarkForm):
    class Meta:
        model = FollowOrder
        fields = "__all__"
        widgets = {
            'book_info': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'ETD': forms.DateInput(attrs={'type': 'date'}),
            'ETA': forms.DateInput(attrs={'type': 'date'}),
            # 'order':forms.TextInput(attrs={'readonly':True}),
            'customer': forms.Select(attrs={'data-live-search': 'true',
                                            'style': "display: none;",
                                            }),
        }


class AddInwardPayModelForm(StarkForm):
    class Meta:
        model = Inwardpay
        fields = "__all__"
        exclude = ['orders', 'status', 'torelate_amount', 'customer', 'keyin_user', 'confirm_status','reference']
        widgets = {
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'amount': forms.TextInput(attrs={'oninput':'justifyNumberInput(this)'}),
            'got_amount': forms.TextInput(attrs={'oninput':'justifyNumberInput(this)'}),
            'ttcopy': forms.FileInput(attrs={'required':True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["currency"].initial = Currency.objects.get(pk=1)
        self.fields["create_date"].initial = datetime.now()


class EditInwardPayModelForm(StarkForm):
    class Meta:
        model = Inwardpay
        fields = "__all__"
        widgets = {
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
        }


class ConfirmInwardpayModelForm(StarkForm):
    class Meta:
        model = Inwardpay
        fields = ['customer', 'amount', 'remark']

        widgets = {
            #  显示备注控件的长宽
            "remark": forms.Textarea(attrs={"cols": 30, "rows": 2}),
        }


class Inwardpay2OrdersModelForm(StarkForm):
    dist_amount = forms.DecimalField(label='dist_amount')
    class Meta:
        model = ApplyOrder
        # 注意只能加上你需要收集的字段，别的不用加上去
        fields = ['dist_amount',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dist_amount"].initial = 0

    # def clean_dist_amount(self):
    #     dist_amount = self.cleaned_data.get('dist_amount')
    #     collect_amount = self.cleaned_data.get('collect_amount')
    #     print(collect_amount, type(collect_amount))
    #     if dist_amount > float(collect_amount):
    #         raise forms.ValidationError('不能超出应收金额')
    #     elif dist_amount < 0:
    #         raise forms.ValidationError('关联金额必须大于0')
    #     else:
    #         return dist_amount


class ResetPwdForm(StarkForm):
    password = forms.CharField(label="密码", widget=forms.PasswordInput, )
    re_password = forms.CharField(label="确认密码", widget=forms.PasswordInput)

    def clean_re_password(self):
        password = self.cleaned_data["password"]
        re_password = self.cleaned_data["re_password"]
        if re_password != password:
            raise forms.ValidationError("两次输入密码不一样")
        else:
            return password


# 编辑跟进表
class FollowChanceEditForm(forms.ModelForm):
    opportunity = forms.CharField(required=False, label='商机',widget=forms.TextInput(attrs={"readonly":True}))

    class Meta:
        model = FollowChance
        fields = ['opportunity','remark',]

    def __init__(self, *args, **kwargs):
        super(FollowChanceEditForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = " form-control"


# 添加跟进记录
class FollowChanceAddForm(forms.ModelForm):
    class Meta:
        model = FollowChance
        fields = ['remark',]

    def __init__(self, *args, **kwargs):
        super(FollowChanceAddForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = " form-control"


class ChanceModelForm(StarkForm):
    class Meta:
        model = Chance
        fields = "__all__"
        exclude = ['owner',]


class ChargePayModelForm(StarkForm):
    class Meta:
        model = ChargePay
        fields = "__all__"
        exclude = ['status', ]
        widgets={
            "create_date":forms.DateInput(attrs={'type': 'date'}),
        }


class ForwarderChargeModelForm(StarkForm):
    class Meta:
        model = Charge
        fields = "__all__"
        exclude = ['status', 'forwarder' ]
        widgets = {
            "BL_date": forms.DateInput(attrs={'type': 'date'}),
        }

# 添加产品图片的model form
class ProductPhotoAddModelForm(StarkForm):
    class Meta:
        model = ProductPhoto
        fields = ["photo","ismain"]


class ProductPhotoEditModelForm(StarkForm):
    class Meta:
        model = ProductPhoto
        fields = "__all__"


