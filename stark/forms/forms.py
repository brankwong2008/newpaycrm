from django import forms

class StarkModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(StarkModelForm,self).__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

class StarkForm(forms.Form):
    def __init__(self,*args,**kwargs):
        super(StarkForm,self).__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class ResetPwdForm(StarkForm):
    password = forms.CharField(label="密码", widget = forms.PasswordInput,)
    re_password = forms.CharField(label="确认密码", widget = forms.PasswordInput)

    def clean_re_password(self):
        password = self.cleaned_data["password"]
        re_password = self.cleaned_data["re_password"]
        if re_password != password:
            raise forms.ValidationError("两次输入密码不一样")
        else:
            return password