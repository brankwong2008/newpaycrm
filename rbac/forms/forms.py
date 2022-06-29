from rbac import models
from django.forms import ModelForm
from django import forms
from django.utils.safestring import mark_safe
import re
from django.conf import settings


# 用于角色信息编辑和添加的model form
class RoleModelForm(ModelForm):
    class Meta:
        model = models.Role
        fields = ["title", ]

    def __init__(self, *args, **kwargs):
        super(RoleModelForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    # def clean_title(self):
    #     title = self.cleaned_data.get("title")
    #     if re.match('\d+', title):
    #         return title
    #     else:
    #         raise forms.ValidationError("必须是纯数字")


# 用于用户信息添加的model form
class UserModelForm(ModelForm):
    re_pwd = forms.CharField(label="确认密码")

    class Meta:
        model = models.MyUser
        fields = ["username", "email", "password", 're_pwd']

    def __init__(self, *args, **kwargs):
        super(UserModelForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    def clean_re_pwd(self):
        re_pwd = self.cleaned_data.get("re_pwd")
        password = self.cleaned_data.get("password")
        if re_pwd == password:
            return re_pwd
        else:
            raise forms.ValidationError("确认密码与密码不一致")


# 用于用户信息编辑的model form
class UserEditModelForm(ModelForm):
    class Meta:
        model = models.MyUser
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super(UserEditModelForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class UserResetPwdModelForm(ModelForm):
    re_pwd = forms.CharField(label="确认密码")

    class Meta:
        model = models.MyUser
        fields = ["password", 're_pwd']

    def __init__(self, *args, **kwargs):
        super(UserResetPwdModelForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    def clean_re_pwd(self):
        re_pwd = self.cleaned_data.get("re_pwd")
        password = self.cleaned_data.get("password")
        if re_pwd == password:
            return re_pwd
        else:
            raise forms.ValidationError("确认密码与密码不一致")


# 用于用户信息编辑的model form
class MenuAddModelForm(ModelForm):
    choices = settings.AVATAR_CHOICES

    class Meta:
        # model = models.Menu
        # fields = ["title", "icon"]
        # widgets = {
        #     "title": forms.TextInput(attrs={"class": "form-control"}),
        #     "icon": forms.RadioSelect(choices= settings.AVATAR_CHOICES)
        # }

        model = models.Menu
        fields = ["sequence","title", "icon",]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            # "icon": forms.RadioSelect(choices=self.choice)
        }

    def __init__(self, *args, **kwargs):
        choices = []
        super(MenuAddModelForm, self).__init__(*args, **kwargs)

        menu_set = set([item['icon'] for item in models.Menu.objects.values("icon")])
        avatar_set = menu_set | set(settings.AVATAR_CHOICES)

        for item in avatar_set:
            node = (item, mark_safe(f"<i class='fa {item}'></i>"))
            choices.append(node)

        self.fields['icon'].widget = forms.RadioSelect(choices=choices)


# 用于用户信息编辑的model form
class SecondMenuModelForm(ModelForm):
    class Meta:
        model = models.Permission
        fields = ["title", "icon", "menu", "urls", "name", "parent"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "menu": forms.Select(choices=[(None, "-------"), ]),
            "parent": forms.Select(choices=[(None, "-------"), ]),
            # "icon": forms.RadioSelect(choices=self.choice)
        }

    def __init__(self, *args, **kwargs):
        icon_choices = []
        menu_choices = []
        super(SecondMenuModelForm, self).__init__(*args, **kwargs)

        menu_iconset = set(
            [item['icon'] for item in models.Permission.objects.filter(icon__isnull=False).values("icon")])
        avatar_set = menu_iconset | set(settings.AVATAR_CHOICES)

        icon_choices.append((None,'------'))
        for item in avatar_set:
            node = (item, mark_safe(f"<i class='fa {item}'></i>"))
            icon_choices.append(node)
        self.fields['icon'].widget = forms.RadioSelect(choices=icon_choices)

        # new_menu_choice = menu_choices + models.Menu.objects.values_list("id", "title")
        # print("new_menu_choice",new_menu_choice)

        # for item in models.Menu.objects.values("id", "title"):
        #     # print(item["id"],item['title'])
        #     menu_choices.append((item["id"],item['title']))

        # self.fields['menu'].choices += models.Menu.objects.values_list("id", "title")
        # self.fields['parent'].choices += models.Permission.objects.filter(menu__isnull=False).values_list("id", "title")
        #


class PermissionModelForm(ModelForm):
    class Meta:
        model = models.Permission
        fields = ["title", "urls", "name",'parent']


#
# class PermissionMultAddModelForm(forms.Form):
#     choices = models.Permission.objects.filter(menu__isnull=False, parent__isnull=True).values_list("id", "title")
#     # choices =[(0,'xx'),(1,'xxx')]
#     title = forms.CharField(max_length=30, label="权限名", widget=forms.widgets.TextInput())
#     urls = forms.CharField(max_length=30, label="URL", widget=forms.widgets.TextInput())
#     name = forms.CharField(max_length=30, label="URL别名", widget=forms.widgets.TextInput())
#     parent_id = forms.IntegerField(label="二级菜单", widget=forms.widgets.Select(choices=choices), required=False)
#

# class PermissionMultAddModelForm(ModelForm):
#    """ modelformset方法还用不好，以后再了解"""
#     class Meta:
#         model = models.Permission
#         fields = ['title', 'urls', 'name', 'parent']
#         widgets = {
#             "parent": forms.Select(
#                 # choices=models.Permission.objects.filter(menu__isnull=True).exclude(parent__isnull=False).values_list("id",
#                 #                                                                                               "title")),
#                 choices= [(1,"x1"),(2,"x2")]
#             )
#         }

#
# class PermissionMultEditModelForm(forms.Form):
#     choices = models.Permission.objects.filter(menu__isnull=False).values_list("id", "title")
#     # choices = [(0, 'xx'), (1, 'xxx')]
#     id = forms.IntegerField(label="id", widget=forms.widgets.HiddenInput())
#     title = forms.CharField(max_length=30, label="权限名", widget=forms.widgets.TextInput())
#     urls = forms.CharField(max_length=128, label="URL", widget=forms.widgets.TextInput())
#     name = forms.CharField(max_length=128, label="URL别名", widget=forms.widgets.TextInput())
#     parent_id = forms.IntegerField(label="二级菜单", widget=forms.widgets.Select(choices=choices), required=False)


# class PermissionMultEditModelForm(ModelForm):
#     class Meta:
#         model = models.Permission
#         fields = ['id','title','urls','name','parent']
#         widgets = {
#             "parent": forms.Select(choices= models.Permission.objects.filter(menu__isnull=False,parent__isnull=True).values_list("id","title")),
#             "id": forms.HiddenInput()
#         }


class AutoPermissionAddModelForm(forms.Form):
    second_menu_choices = list(models.Permission.objects.filter(menu__isnull=False).values_list("id", "title"))
    menu_choices = models.Menu.objects.values_list("id", "title")
    # second_menu_choices = [(1,"x1"),(2,"x2")]
    # menu_choices = [(1,"x1"),(2,"x2")]

    title = forms.CharField(max_length=30, label="权限名", widget=forms.widgets.TextInput())
    urls = forms.CharField(max_length=128, label="URL", widget=forms.widgets.TextInput(attrs={'style':'width:250px'}))
    name = forms.CharField(max_length=128, label="URL别名", widget=forms.widgets.TextInput())
    parent_id = forms.ChoiceField(label="二级菜单", choices=[(None, "-----"), ], required=False)
    menu_id = forms.ChoiceField(label="一级菜单", choices=[(None, "-----"), ], required=False)

    def __init__(self, *args, **kwargs):
        super(AutoPermissionAddModelForm, self).__init__(*args, **kwargs)
        self.fields["parent_id"].choices += self.second_menu_choices
        self.fields["menu_id"].choices += self.menu_choices


class AutoPermissionEditModelForm(forms.Form):
    second_menu_choices = list( models.Permission.objects.filter(menu__isnull=False).values_list("id", "title") )
    menu_choices = models.Menu.objects.values_list("id", "title")
    # second_menu_choices = [(1, "x1"), (2, "x2")]
    # menu_choices = [(1, "x1"), (2, "x2")]

    id = forms.IntegerField(label="id", widget=forms.widgets.HiddenInput())
    title = forms.CharField(max_length=30, label="权限名", widget=forms.widgets.TextInput())
    urls = forms.CharField(max_length=128, label="URL", widget=forms.widgets.TextInput())
    name = forms.CharField(max_length=128, label="URL别名", widget=forms.widgets.TextInput())
    parent_id = forms.ChoiceField(label="二级菜单", choices=[(None, "-----"), ], required=False)
    menu_id = forms.ChoiceField(label="一级菜单", choices=[(None, "-----"), ], required=False)

    def __init__(self, *args, **kwargs):
        super(AutoPermissionEditModelForm, self).__init__(*args, **kwargs)
        self.fields["parent_id"].choices += self.second_menu_choices
        print(9999999, self.second_menu_choices)
        self.fields["menu_id"].choices += self.menu_choices
