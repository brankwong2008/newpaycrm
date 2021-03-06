from django.forms import ModelForm
from django import forms
from dipay.models import ApplyOrder, Inwardpay, Currency, FollowOrder,Pay2Orders
from datetime import datetime


class StarkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                # 给外键字段添加搜索功能，前端一定要加载bootstap-select.js
                field.widget.attrs["class"] = "selectpicker bla bli form-control"
                field.widget.attrs["style"] = "display: none;"
                field.widget.attrs["data-live-search"] = 'true'
            else:
                field.widget.attrs["class"] = " form-control"


class AddApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = ['order_type', 'customer', 'goods', 'term', 'currency', 'amount', 'remark']
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            # 'customer': forms.Select(attrs={'data-live-search': 'true',
            #                                 'style': "display: none;",
            #                                 })
        }

    # def __init__(self, *args, **kwargs):
    #     super(AddApplyOrderModelForm, self).__init__(*args, **kwargs)
    #     for name, field in self.fields.items():
    #         if name == 'customer':
    #             print('name', name)
    #             field.widget.attrs["class"] = "selectpicker bla bli form-control"
    #         else:
    #             field.widget.attrs["class"] = "form-control"


class EditApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = '__all__'
        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            'order_number': forms.TextInput(attrs={'readonly': True}),
            'customer': forms.Select(attrs={'data-live-search': 'true',
                                            'style': "display: none;",
                                            'class':'selectpicker bla bli form-control',
                                            }),
        }



class ConfirmApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = ['confirm_date','order_number','sub_sequence','customer','goods','currency','amount','remark']

        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            'confirm_date': forms.DateInput(attrs={'type': 'date'}),
            'order_number': forms.TextInput(attrs={'readonly': True}),
            'customer': forms.Select(attrs={'readonly': True}),

        }


class ManualAddApplyOrderModelForm(StarkForm):
    class Meta:
        model = ApplyOrder
        fields = ['confirm_date', 'order_number', 'salesperson','customer', 'goods', 'currency', 'amount', 'remark']

        widgets = {
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
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
        exclude = ['orders', 'status', 'torelate_amount', 'amount', 'customer', 'keyin_user', 'confirm_status']
        widgets = {
            'create_date': forms.DateInput(attrs={'type': 'date'}),
            'remark': forms.Textarea(attrs={'cols': 30, 'rows': 3}),
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
