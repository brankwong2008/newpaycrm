from django.utils.safestring import mark_safe
from django.db import models
from django.urls import reverse
import json
from dipay.utils.tools import str_width_control
from dipay.models import Pay2Orders



def status_display(handler_obj, obj=None, is_header=False, *args, **kwargs):
    """
           显示 followorder, weeklyplan的状态
           :param obj: 该行记录对象
           :param is_header: Handler
           :return: 前端代码
           """
    if is_header:
        return '状态'
    else:
        status_choices = handler_obj.model_class.follow_choices
        status_choices = json.dumps(status_choices)
        # class中加入obj.status, 便于css来操作颜色

        # 判断用户是否有此字段的编辑权限
        is_editable = handler_obj.get_editable('status')
        if is_editable:
            return mark_safe(
                "<span class='status-display status-%s' id='%s-id-%s' choice='%s' onclick='showInputBox(this)' > %s </span>"
                % (obj.status, 'status', obj.pk, status_choices, obj.get_status_display()))
        else:
            return mark_safe(
                "<span class='status-display status-%s' id='%s-id-%s' choice='%s'  > %s </span>"
                % (obj.status, 'status', obj.pk, status_choices, obj.get_status_display()))

#  订单号的显示
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

# 关联订单显示
def related_orders_display(self, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '已关联订单'
    else:
        related_list = Pay2Orders.objects.filter(payment=obj)
        if related_list:
            order_list = ','.join([ pay2order_obj.order.order_number for pay2order_obj in related_list])
            related2order_url = reverse("stark:dipay_inwardpay_relate2order", kwargs={'inwardpay_id':obj.pk})
            return mark_safe(f"<a href='{related2order_url}' target='_blank'>{order_list}</a>")
        else:
            return '--'

# 业务员的显示
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

# 货物的显示
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

# 客户的显示
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
            return obj.order.confirm_date.strftime('%Y/%m/%d')
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


# 已收和应收金额
def rcvd_amount_blance_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '已收和应收'
    else:
        return_url = handler.reverse_url('show_pay_details', order_id=obj.order.pk)
        return mark_safe(
            "<a onclick='return showPayDetails(this)' href='%s' customer_name='%s'><span>收: <span class='amount-value'>%s</span> </span><br><span>欠:<span class='amount-value'>%s</span></span></a>" % (
                return_url, obj.order.customer, obj.order.rcvd_amount, obj.order.collect_amount))


# 发票金额
def amount_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '发票金额'
    else:
        amount_tag = "<span class='invoice-amount-display' id='%s-id-%s' amount='%s' onclick='showInputBox(this)'>%s%s</span>" % (
            'amount', obj.pk, obj.order.amount, obj.order.currency.icon, obj.order.amount
        )
        return mark_safe(amount_tag)


# 起运港和目的港
def port_display(field, title=None, hidden_xs=''):
    def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
        """功能：ETD ETA日期字段的显示 """
        if is_header:
            if title:
                name = title
            else:
                name = handler_obj.model_class._meta.get_field(field).verbose_name
            return mark_safe("<span class='%s'>%s</span>" % (hidden_xs, name))
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            port_name = getattr(obj, field) or '--'
            port_name = port_name[:15]

            return mark_safe("<span class='text-display %s'  onclick='showInputBox(this)' "
                             "id='%s-id-%s' > %s </span>" % (hidden_xs, field, obj.pk, port_name))

    return inner


# 订舱，装箱，生产信息 (如果内容太长自动进行隐藏的办法）  hidden-xs的单元格将在手机屏幕不显示
def info_display(field, title=None, hidden_xs='', max_width=100):
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
                name = title
            else:
                name = handler_obj.model_class._meta.get_field(field).verbose_name

            return mark_safe("<span class='%s'> %s </span>" % (hidden_xs, name))

        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            field_val = getattr(obj, field)
            if field_val is None:
                return "-"
            if isinstance(field_val, models.DateTimeField):
                pass

            more_tag = "<span class='more_tag' onclick=showFullContent(this)><i class='fa fa-ellipsis-h'></i></span>"

            # 判断用户是否有此字段的编辑权限
            is_editable = handler_obj.get_editable(field)
            if is_editable:
                return mark_safe("<span cont='%s' class='text-display %s' onclick='showInputBox(this)' "
                                     "id='%s-id-%s' > %s </span>" % (field_val, hidden_xs, field, obj.pk, field_val))
            else:
                return mark_safe("<span cont='%s' class='text-display %s' "
                                     "id='%s-id-%s' > %s </span>" % (field_val, hidden_xs, field, obj.pk, field_val))

    return inner


# ETA ETD等显示
def follow_date_display(field, title=None, time_format="%Y-%m-%d", hidden_xs=""):
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
            is_editable = handler_obj.get_editable(field)
            if is_editable:
                return mark_safe("<span class='date-display %s' year='%s' onclick='showInputBox(this)' "
                                 "id='%s-id-%s' > %s </span>" % (hidden_xs, year, field, obj.pk, create_date))
            else:
                return mark_safe("<span class='date-display %s' year='%s' "
                                 "id='%s-id-%s' > %s </span>" % (hidden_xs, year, field, obj.pk, create_date))

    return inner



# 保存跟单列表每行数据
def save_display(handler, obj=None, is_header=False, *args, **kwargs):
    """  显示 保存当条跟单记录 """
    if is_header:
        return mark_safe("<span class='hidden-xs save-sequence'> 保存 </span>")
    else:
        save_url = handler.reverse_url('save')
        return mark_safe("<span class='save-sequence hidden-xs' pk='%s' url='%s' onclick='savePlan(this)'>"
                         " <i class='fa fa-check-square-o'></i> </span>" % (obj.pk, save_url))


# 基本信息展示（订单号，下单日期，sales）
def basic_info_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '基本信息'
    else:
        order_number = obj.order.order_number
        salesperson = obj.order.salesperson.nickname if obj.order.salesperson else '-'
        confirm_date = confirm_date_display(handler, obj, False)
        order_link = reverse("stark:dipay_applyorder_list")+"?q=%s"% order_number
        basic_info = f'<span class="invoice-number-display"><a class="order-link" href="{order_link}" target="_blank">{order_number}</a></span> <br>' \
                     f' <span>{confirm_date}</span><br>' \
                     f'<span>{salesperson}</span>'
        return mark_safe(basic_info)


# 订舱信息展示，加入船公司和集装箱信息
def book_info_display(field, title=None, time_format="%Y-%m-%d", hidden_xs='', max_width=52):
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
                header = title
            else:
                header = handler_obj.model_class._meta.get_field(field).verbose_name
            return mark_safe("<span class='%s'>%s</span>" % (hidden_xs, header))
        else:
            # getattr方法可用字符串方式从对象中调取方法或者属性
            field_val = getattr(obj, field)
            if field_val is None:
                return mark_safe("<span class='%s'>--</span>" % (hidden_xs))

            # 船公司信息和编辑
            shipline = obj.shipline.shortname if obj.shipline else '--'
            shipline_link = obj.shipline.link if obj.shipline else '#'
            shipline_field_obj = handler_obj.model_class._meta.get_field('shipline')
            shipline_model = shipline_field_obj.related_model
            shipline_choices = [(item.pk, item.shortname) for item in shipline_model.objects.all().order_by('shortname')]
            shipline_choices = json.dumps(shipline_choices)

            container = obj.container or '--'

            container_tag_btn = f""" <span><i class='fa fa-building'></i></span> <span class='text-display container_tag' onclick='showInputBox(this)' 
                                id="container-id-{obj.pk}" >{container} </span>
                                <button id='clipboard-btn-{obj.pk}' class="clipboard_btn" type="button" 
                                data-clipboard-demo="" data-clipboard-target="#container-id-{obj.pk}"></button>
                                """
            shipping_tag = f"<a href={shipline_link} pk='{obj.pk}' onclick='return trackShipment(this)'>" \
                           f"<i class='fa fa-ship'></i></a><span class='status-display shipline-tag'" \
                           f" id='shipline-id-{obj.pk}' choice='{shipline_choices}' " \
                           f"onclick='showInputBox(this)' > {shipline} </span> {container_tag_btn}"

            return mark_safe("<span cont='%s' class='text-display %s' onclick='showInputBox(this)' "
                             f"id='%s-id-%s' > %s </span>  <br>"
                             "%s" % (field_val, hidden_xs, field, obj.pk, field_val, shipping_tag))
    return inner


#  客户，货物，目的港和贸易条款的展示
def customer_goods_port_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return '客户/货物/目的港'
    else:
        customer = str_width_control(obj.order.customer.shortname,16)[0] if obj.order.customer else '-'
        goods = obj.order.goods[:15]
        discharge_port = port_display('discharge_port')(handler, obj, False)
        term = obj.order.get_term_display()
        if obj.order.customer:
            customer_details_url = reverse("stark:dipay_customer_show_detail", kwargs={"pk":obj.order.customer.pk})
        else:
            customer_details_url = "#"

        basic_info = f'<span style="font-weight:bolder"><a class="customer-link" href="{customer_details_url}" target="_blank">{customer}</a></span> <br>' \
                     f' <span>{goods}</span><br>' \
                     f'{discharge_port} &nbsp&nbsp <span>{term}</span>'
        return mark_safe(basic_info)


def amount_rvcd_collect_display(handler, obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return mark_safe("<span class='hidden-xs'>账务</span>")
    else:
        amount_tag = "<span class='invoice-amount-display' id='%s-id-%s' amount='%s' onclick='showInputBox(this)'>%s%s</span>" % (
            'amount', obj.pk, obj.order.amount, obj.order.currency.icon, obj.order.amount
        )

        rcvd_collect_amount = rcvd_amount_blance_display(handler, obj, False)

        content = f'发票：{amount_tag} <br>' \
                  f'{rcvd_collect_amount}'

        return mark_safe("<div class='hidden-xs'>%s</div>" % content)



# 每行的more_tag显示
def more_tag_display(handler, obj=None, is_header=False, *args, **kwargs):
    """  显示 保存当条跟单记录 """
    if is_header:
        return mark_safe("<span class='hidden-xs'>Handle</span>")
    else:
        add_dailyplan_url = reverse('stark:dipay_dailyplan_add')
        return mark_safe(""" <ul class='hidden-xs'> <li class='dropdown'>
                        <a href='#' class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup='true'
                           aria-expanded='false'> <span class='fa fa-navicon'></span></a>
                        <ul class='dropdown-menu'>
                            <li><a pk='%s' href='%s?get_type=simple' onclick='return addDailyPlan(this)'>添加任务</a></li>
                        </ul>
                    </li></ul>""" % (obj.pk, add_dailyplan_url) )


# 显示水单小图片
def ttcopy_display(handler,obj=None, is_header=False, *args, **kwargs):
    if is_header:
        return mark_safe("<span class='hidden-xs'>水单</span>")
    else:
        if obj.ttcopy:
            img_tag = f"<img class='ttcopy-small-img hidden-xs' src={obj.ttcopy.url} " \
                      f"onclick='return popupImg(this)' width='30px' height='30px'>"
        else:
            img_tag = '<i class="fa fa-minus-square hidden-xs"></i>'


    return mark_safe(img_tag)