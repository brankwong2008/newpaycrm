from django.utils.safestring import mark_safe
from django.forms import DateInput
from django.conf import settings
from django.db import models

class MyDateInput(DateInput):
    input_type = "date"

def manytomany_display(field,title=None):
    def inner(handler_obj ,obj=None ,is_header=None,*args,**kwargs):
        """
        功能：显示manytomany字段的数值
        :param xself: show_list处理需要的第一个占位参数，hander对象
        :param obj: 一条queryset记录，有get_field_display方法
        :param is_header: 是否表头
        :return:
        """
        if is_header:
            if title:
                return title
            return handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            field_obj = getattr(obj,field)
            queryset = field_obj.all()
            return ','.join([ str(row) for row in queryset])
    return inner

def get_date_display(field, title=None, time_format="%Y-%m-%d"):
    def inner(handler_obj, obj=None, is_header=None,*args,**kwargs):
        """
        功能：日期字段的文本格式
        :param handler_obj: handler对象
        :param obj: 一条queryset记录，有get_field_display方法
        :param is_header: 是否表头
        :return:
        """
        if is_header:
            if title:
                return title
            return handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            datetime = getattr(obj, field)
            if not datetime:
                return ""
            try:
                create_date = datetime.strftime(time_format)
            except:
                create_date = '日期格式错误'
            return create_date

    return inner

def reset_pwd_display(handler_obj ,obj=None ,is_header=None,title=None,*args,**kwargs):
    if is_header:
        if title:
            return title
        else:
            return "重置密码"
    else:
        url = handler_obj.reverse_resetpwd_url(obj.id,**kwargs)
        # url = "/stark/"
        return mark_safe("<a href='%s' target='_blank'>重置密码</a>" % url)

def get_choice_text(field, title=None):
    def inner(handler_obj ,obj=None ,is_header=None,*args,**kwargs):
        """
        功能：显示choice字段的数值对应的title
        :param xself: show_list处理需要的第一个占位参数，hander对象
        :param obj: 一条queryset记录，有get_field_display方法
        :param is_header: 是否表头
        :return:
        """

        if is_header:
            if title:
                return title
            return handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            method_func = getattr(obj ,"get_%s_display" % field)
            return method_func()
    return inner

def checkbox_display(hander_obj,obj=None,is_header=None,*args,**kwargs):
    """在列里面显示checkbox"""
    if is_header:
        return "选择"
    else:
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % obj.pk )

def record_display(title=None):
    def inner(handler_obj, obj=None, is_header=None):
        """
        功能：日期字段的文本格式
        :param handler_obj: handler对象
        :param obj: 一条queryset记录，有get_field_display方法
        :param is_header: 是否表头
        :return:
        """
        if is_header:
            return title

        else:
            url = "/stark/work/customer/public/record/%s" % obj.id
            return  mark_safe("<a href='%s' target='_blank'> 跟进记录 </a>" %  url)

    return inner


def port_display(field, title=None):
    def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
        """功能：ETD ETA日期字段的显示 """
        if is_header:
            if title:
                return title
            return handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            port_name = getattr(obj, field)
            if not port_name or port_name=='-':
                 port_name = "---"

            return mark_safe("<span class='text-display'  onclick='showInputBox(this)' "
                             "id='%s-id-%s' > %s </span>" % (field, obj.pk, port_name))
    return inner

def info_display(field, title=None, time_format="%Y-%m-%d"):
    def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
        """
        功能：显示装箱，订舱，生产等字段的方法，并结合前端js提供双击然后ajax修改信息的功能
        :param handler_obj: handler对象
        :param obj: 一条queryset记录，有get_field_display方法
        :param is_header: 是否表头
        :return:
        """
        if is_header:
            if title:
                return title
            return handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            field_val = getattr(obj, field)
            if field_val is None:
                return "-"
            if isinstance(field_val, models.DateTimeField):
                print('the instance is date')

            return mark_safe("<span class='text-display' onclick='showInputBox(this)' "
                             "id='%s-id-%s'> %s </span>" % (field, obj.pk, field_val))
            # return info_field

    return inner

def follow_date_display(field, title=None, time_format="%Y-%m-%d"):
    def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
        """
        功能：ETD ETA日期字段的显示
        """
        if is_header:
            if title:
                return title
            return handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            datetime_obj = getattr(obj, field)
            year = ''
            if not datetime_obj:
                create_date =  "--"
            else:
                try:
                    create_date = datetime_obj.strftime(time_format)
                    year = datetime_obj.year
                except:
                    create_date = '日期格式错误'
            return mark_safe("<span class='date-display' year='%s' onclick='showInputBox(this)' "
                             "id='%s-id-%s' > %s </span>" % (year, field, obj.pk, create_date))

    return inner



# 页面直接修改日期字段的显示
def change_date_display(field, title=None, time_format="%Y-%m-%d", hidden_xs=""):
    def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
        """
        功能：ETD ETA日期字段的显示
        """
        if is_header:
            if title:
                name = title
            else:
                name = handler_obj.model_class._meta.get_field(field).verbose_name

            return mark_safe("<span class='%s'> %s </span>" % (hidden_xs, name))
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            datetime_obj = getattr(obj, field)
            year = ''
            if not datetime_obj:
                create_date = "--"
            else:
                try:
                    create_date = datetime_obj.strftime(time_format)
                    year = datetime_obj.year
                except:
                    create_date = '日期格式错误'
            return mark_safe("<span class='date-display %s' year='%s' onclick='showInputBox(this)' "
                                 "id='%s-id-%s' > %s </span>" % (hidden_xs, year, field, obj.pk, create_date))
    return inner


# 保存跟单列表每行数据
def save_display(handler, obj=None, is_header=False, *args, **kwargs):
    """  显示 保存当条跟单记录 """
    if is_header:
        return '保存'
    else:
        save_url = handler.reverse_url('save')
        return mark_safe("<span class='save-sequence' pk='%s' url='%s' onclick='savePlan(this)'>"
                         " <i class='fa fa-check-square-o'></i> </span>" % (obj.pk, save_url))





class PermissionHanlder:

    def del_display(self, obj=None, is_header=False, *args, **kwargs):
        """
        在列表页显示删除按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "操作"
        else:
            del_url = self.reverse_del_url(*args, **kwargs)
            return mark_safe("<a href='%s'><i class='fa fa-trash'></i></a>" % del_url)

    # 编辑按钮的权限控制
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

        return mark_safe("<a href='%s'><i class='fa fa-edit'></i></a>" % edit_url)

    # 如果删除编辑按钮在权限里面，加入字段列表
    def get_fields_display(self, request, *args, **kwargs):
        val = []
        val.extend(self.fields_display)

        extra_fields = self.get_extra_fields_display(request, *args, **kwargs)
        if extra_fields:
            val.extend(extra_fields)

        permission_dict = request.session.get(settings.PERMISSION_KEY)
        get_edit_url_name = '%s:%s' % (self.namespace, self.get_edit_url_name)
        get_del_url_name = '%s:%s' % (self.namespace, self.get_del_url_name)

        if get_edit_url_name in permission_dict and get_del_url_name in permission_dict:
            val.extend([self.edit_del_display, ])
        elif get_edit_url_name in permission_dict:
            val.extend([self.edit_display, ])
        elif get_del_url_name in permission_dict:
            val.extend([self.del_display, ])
        return val

    # 添加按钮的权限控制
    def add_btn_display(self,request,*args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        get_add_url_name = '%s:%s' % (self.namespace, self.get_add_url_name)
        if get_add_url_name in permission_dict and self.has_add_btn:
            return self.get_add_btn(request,*args, **kwargs)


