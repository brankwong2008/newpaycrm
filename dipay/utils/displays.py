from django.utils.safestring import mark_safe
from django.db import models
import json

def status_display(handler, obj=None, is_header=False, *args, **kwargs):
    """
           显示 followorder, weeklyplan的状态
           :param obj: 该行记录对象
           :param is_header: Handler
           :return: 前端代码
           """
    if is_header:
        return '状态'
    else:
        status_choices = handler.model_class.follow_choices
        status_choices = json.dumps(status_choices)
        # class中加入obj.status, 便于css来操作颜色
        return mark_safe("<span class='status-display status-%s' id='%s-id-%s' choice='%s' onclick='showInputBox(this)' > %s </span>"
                         % (obj.status, 'status',obj.pk, status_choices, obj.get_status_display()) )


def order_number_display(handler, obj=None, is_header=False, *args, **kwargs):
        """
               显示 发票金额
               :param obj:
               :param is_header:
               :return:
               """
        if is_header:
            return '发票号'
        else:
            return mark_safe('<span class="invoice-number-display">%s</span>' % (obj.order.order_number))

def sales_display(handler, obj=None, is_header=False, *args, **kwargs):
    """
           显示销售人员名称首字母
           :param obj:
           :param is_header:
           :return:
           """
    if is_header:
        return '业务'
    else:
        nickname = obj.order.salesperson.nickname if obj.order.salesperson else None

        return nickname[0] if nickname else "-"

def goods_display(handler, obj=None, is_header=False, *args, **kwargs):
    """
           显示销售人员名称首字母
           :param obj:
           :param is_header:
           :return:
           """
    if is_header:
        return '货物'
    else:
        return obj.order.goods[:15]

def customer_display(handler, obj=None, is_header=False, *args, **kwargs):
    """
           显示客户简名
           :param obj:
           :param is_header:
           :return:
           """
    if is_header:
        return '客户'
    else:
        if obj.order.customer:
            customer_name = obj.order.customer.shortname[:10]
        else:
            customer_name = '-'
        return customer_name

 # 下单日期
def confirm_date_display(handler, obj=None, is_header=False, *args, **kwargs):
    """
           显示销售人员名称首字母
           :param obj:
           :param is_header:
           :return:
           """
    if is_header:
        return '下单日'
    else:
        if obj.order.confirm_date:
            return obj.order.confirm_date.strftime('%m/%d')
        else:
            return '-'

# 成交条款
def term_display(handler, obj=None, is_header=False, *args, **kwargs):
    """
           显示 运输条款
           :param obj:
           :param is_header:
           :return:
           """
    if is_header:
        return 'Term'
    else:
        return obj.order.get_term_display()

# 应收金额
def collect_amount_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '应收款'
    else:
        return '%s%s' % (obj.order.currency.icon, obj.order.collect_amount)

# 发票金额
def amount_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '发票金额'
    else:
        amount_tag = "<span class='invoice-amount-display' id='%s-id-%s' amount='%s' onclick='showInputBox(this)'>%s%s</span>" % (
            'amount',obj.pk,obj.order.amount, obj.order.currency.icon, obj.order.amount
        )
        return mark_safe(amount_tag)

# 起运港和目的港
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

# 订舱，装箱，生产信息
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
                pass

            return mark_safe("<span class='text-display' onclick='showInputBox(this)' "
                             "id='%s-id-%s' > %s </span>" % (field, obj.pk, field_val))
            # return info_field

    return inner

# ETA ETD等显示
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

# 保存跟单列表每行数据
def save_display(handler, obj=None, is_header=False, *args, **kwargs):
    """  显示 保存当条跟单记录 """
    if is_header:
        return '保存'
    else:
        save_url = handler.reverse_url('save')
        return mark_safe("<span class='save-sequence' pk='%s' url='%s' onclick='savePlan(this)'>"
                         " <i class='fa fa-check-square-o'></i> </span>" % (obj.pk, save_url))
