from django.utils.safestring import mark_safe
from django.forms import DateInput
from django.conf import settings
from django.db import models
from stark.utils.tools import  str_width_control

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

def get_date_display(field, title=None, time_format="%Y-%m-%d",hidden_xs=''):
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
            verbose_name = handler_obj.model_class._meta.get_field(field).verbose_name
            return mark_safe("<span class='%s'>%s<span>" % (hidden_xs, verbose_name))
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            datetime = getattr(obj, field)
            if not datetime:
                create_date = '-'
            try:
                create_date = datetime.strftime(time_format)
            except:
                create_date = '日期格式错误'
            return mark_safe("<span class='%s'>%s<span>" % (hidden_xs, create_date))

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
        model_name = handler_obj.model_class._meta.model_name
        if is_header:
            return title or handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            method_func = getattr(obj ,"get_%s_display" % field)
            val = getattr(obj ,field)
            return mark_safe(f"<span class={model_name}-{field}-{val}>{method_func()}</span>")
    return inner

def checkbox_display(hander_obj,obj=None,is_header=None,*args,**kwargs):
    """在列里面显示checkbox"""
    if is_header:
        return mark_safe("<span>选择</span>")
    else:
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % obj.pk )

def checkbox_display_func(hidden_xs = ""):
    """在列里面显示checkbox, 需要传参数的checkbox display"""
    def inner(hander_obj,obj=None,is_header=None,*args,**kwargs):
        if is_header:
            return mark_safe("<span class='%s'>选择</span>" % hidden_xs)
        else:
            return mark_safe('<input class="%s" type="checkbox" name="pk" value="%s">' % (hidden_xs, obj.pk) )
    return inner


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

def info_display(field, title=None, time_format="%Y-%m-%d",max_length=None,hidden_xs=""):
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
            verbose_name = handler_obj.model_class._meta.get_field(field).verbose_name
            return mark_safe("<span class='%s'>%s<span>" %(hidden_xs, verbose_name))
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            field_val = getattr(obj, field)
            if field_val is None:
                return "-"
            if max_length and len(field_val)>max_length :
                field_val = field_val[:max_length] + " ..."

            if isinstance(field_val, models.DateTimeField):
                print('the instance is date')

            return mark_safe("<span class='text-display %s' onclick='showInputBox(this)' "
                             "id='%s-id-%s'> %s </span>" % (hidden_xs,field, obj.pk, field_val))


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
                create_date = "-"
            else:
                try:
                    create_date = datetime_obj.strftime(time_format)
                    year = datetime_obj.year
                except:
                    create_date = '日期格式错误'
            defer_btn = "<span style='color:grey;font-size: x-small;cursor:pointer;margin-left:15px' " \
                        " pk='%s' onclick='deferToNextDay(this)'>延</span>" % obj.pk
            change_date_btn = "<span class='date-display %s' year='%s' onclick='showInputBox(this)' id='%s-id-%s' > %s </span>" \
                              % (hidden_xs, year, field, obj.pk, create_date)
            return mark_safe(change_date_btn+defer_btn)
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
        :return:pe
        """
        if is_header:
            return mark_safe("<span class='hidden-xs'>操作</span>")
        else:
            del_url = self.reverse_del_url(pk=obj.pk)
            return mark_safe("<a href='%s' class='hidden-xs'><i class='fa fa-trash'></i></a>" % del_url)

    # 编辑按钮的权限控制
    def edit_display(self, obj=None, is_header=False, *args, **kwargs):
        """
        在列表页显示编辑按钮
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return mark_safe("<span class='hidden-xs'>操作</span>")
        else:
            edit_url = self.reverse_edit_url(pk=obj.id)

        return mark_safe("<a href='%s' class='hidden-xs'><i class='fa fa-edit'></i></a>" % edit_url)

    # 如果删除编辑按钮在权限里面，加入字段列表
    def get_fields_display(self, request, *args, **kwargs):
        val = []
        if self.fields_display == "__all__":
            self.fields_display = [item.name for item in self.model_class._meta.fields]
        val.extend(self.fields_display)

        extra_fields = self.get_extra_fields_display(request, *args, **kwargs)
        if extra_fields:
            val.extend(extra_fields)

        permission_dict = request.session.get(settings.PERMISSION_KEY)
        get_edit_url_name = '%s:%s' % (self.namespace, self.get_edit_url_name)
        get_del_url_name = '%s:%s' % (self.namespace, self.get_del_url_name)

        edit_btn_exists = get_edit_url_name in permission_dict
        del_btn_exists = get_del_url_name in permission_dict
        if edit_btn_exists and del_btn_exists:
            val.extend([self.edit_del_display, ])
        elif edit_btn_exists:
            val.extend([self.edit_display, ])
        elif del_btn_exists:
            val.extend([self.del_display, ])

        return val

    # 添加按钮的权限控制
    def add_btn_display(self,request,*args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)

        get_add_url_name = '%s:%s' % (self.namespace, self.get_add_url_name)
        if get_add_url_name in permission_dict and self.has_add_btn:

            return self.get_add_btn(request,*args, **kwargs)



# 显示text文本字段的通用方法，（带隐藏按钮）
def text_area_display(field, max_length = 130, title=None):
    def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return title or handler_obj.model_class._meta.get_field(field).verbose_name
        else:
            remark = getattr(obj, field)
            remark_incontrol, is_long = str_width_control(remark,max_length)
            if is_long:
                remark_text = "<span id='remark_%s' text='%s'>%s</span>" % (obj.pk, remark, remark_incontrol) + \
                              "<i class='fa fa-chevron-down more' pk='%s' onclick='expandRemark(this)'></i>" % obj.pk
            else:
                remark_text = remark_incontrol

            return mark_safe(remark_text)
    return inner
