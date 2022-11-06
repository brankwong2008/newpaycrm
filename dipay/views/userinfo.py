
from django.shortcuts import render,HttpResponse,redirect
from django.conf.urls import url
from django.conf import settings
from django import forms
from stark.service.starksite import StarkHandler
from django.utils.module_loading import import_string
from stark.utils.display import manytomany_display,get_choice_text,reset_pwd_display
from stark.forms.forms import StarkModelForm,ResetPwdForm
from rbac.utils.common import gen_md5

MyUserInfo = import_string(settings.RBAC_USER_MODLE_CLASS)

class MyUserInfoHandler(StarkHandler):
    fields_display = ["username","nickname",manytomany_display("roles"), reset_pwd_display, get_choice_text('department')]

    def get_model_form(self,type=None):
        class UserAddModelForm(StarkModelForm):
            re_password = forms.CharField(max_length=30,label="确认密码",widget=forms.PasswordInput())
            class Meta:
                model = MyUserInfo
                fields = ["username","nickname","password","re_password","department"]
                widgets = {
                    "password": forms.PasswordInput,
                }

            def clean_re_password(self):
                password = self.cleaned_data.get("password")
                re_password = self.cleaned_data.get("re_password")
                if password != re_password:
                    raise forms.ValidationError("两次密码输入不一致")
                else:
                    return re_password

        class FowarderUserEditModelForm(StarkModelForm):
            class Meta:
                model = MyUserInfo
                exclude = ["password"]

        class UserEditModelForm(StarkModelForm):
            class Meta:
                model = MyUserInfo
                exclude = ["password",'forwarder']

        if type == "add":
            return UserAddModelForm

        if type == "edit":
            return UserEditModelForm

        if type == "forwarder":
            return FowarderUserEditModelForm

    def save_form(self,form,request,is_update=False,*args, **kwargs):
        form.instance.password = gen_md5(form.instance.password)
        form.save()

    def get_extra_urls(self):
        patterns =  [url("^resetpwd/(\d+)/$", self.wrapper(self.reset_pwd), name=self.get_reset_pwd_url_name),]

        return patterns

    def reset_pwd(self,request,pk):
        if request.method == "GET":
            form = ResetPwdForm()
            return render(request,"stark/change_list.html",locals())
        else:
            user_obj = MyUserInfo.objects.filter(pk=pk).first()
            if not user_obj:
                return HttpResponse("重置失败，用户不存在")

            form = ResetPwdForm(request.POST)
            if form.is_valid():
                user_obj.password = gen_md5(request.POST.get("password"))
                user_obj.save()
                return redirect(self.reverse_list_url())
            else:
                return render(request,"stark/change_list.html",locals())


    # 编辑一条记录
    def edit_list(self, request, pk, *args,**kwargs):
        edit_obj = self.get_edit_obj(request, pk, *args, **kwargs)

        if not edit_obj:
            return HttpResponse("编辑的记录不存在")

        if edit_obj.roles.filter(title='货代').exists():
            print("这是货代的用户")
            form_class = self.get_model_form("forwarder")
        else:
            form_class = self.get_model_form("edit")


        if request.method == "GET":
            form = form_class(instance=edit_obj)
            back_url = self.reverse_list_url()
            namespace = self.namespace
            app_label = self.app_label
            # 自定义列表，外键字段快速添加数据，在前端显示加号
            popup_list = self.popup_list
            return render(request,self.edit_list_template or "stark/change_list.html",locals())

        if request.method == "POST":
            form = form_class(instance=edit_obj,data=request.POST)
            if request.FILES:
                form = form_class(request.POST,request.FILES,instance=edit_obj)
            if form.is_valid():
                responds = self.save_form(form,request,True,*args,**kwargs)

                return responds or redirect(self.reverse_list_url(*args,**kwargs))
                # return responds
            else:
                return render(request, self.edit_list_template or "stark/change_list.html", locals())
