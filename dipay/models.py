# Create your models here.
from django.db import models
from rbac.models import MyUser
from datetime import datetime

# 货代表
class Forwarder(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name='货代名')
    shortname = models.CharField(max_length=20, verbose_name='货代简称')
    contact = models.CharField(max_length=20, verbose_name='货代联系人',default='-')
    phone = models.CharField(max_length=11, verbose_name='电话', default='-')
    email = models.CharField(max_length=128, verbose_name='邮件地址', default='-')
    bank_account = models.TextField(verbose_name='银行信息', default='--')
    remark = models.TextField(verbose_name='货代详情', default='--')
    # user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,verbose_name='绑定用户',null=True)

    def __str__(self):
        return self.shortname if self is not None else '-'


class UserInfo(MyUser):
    nickname = models.CharField(max_length=30,verbose_name="姓名")
    department_choices = [(1, '业务部'),
                         (2, '跟单部'),
                         (4, '财务部'),
                         (8, '管理部'),
                         (7, '外部'),
                    ]
    department = models.SmallIntegerField(choices=department_choices, verbose_name='部门', default=1)
    forwarder = models.ForeignKey(to=Forwarder, on_delete=models.CASCADE, verbose_name='绑定货代', null=True)

    def __str__(self):
            return self.nickname


class Customer(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name='客户名')
    shortname = models.CharField(max_length=20, verbose_name='客户简称')
    remark = models.TextField(verbose_name='客户详情', default='--')
    email = models.CharField(max_length=128, verbose_name='邮件地址', default='-')
    owner = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name='所属外销员',
                                    limit_choices_to={"department":1} , null=True)
    def __str__(self):
        if self is None:
            return '-'
        return self.shortname


class Payer(models.Model):
    title = models.CharField(max_length=128, verbose_name='付款人')
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE,verbose_name='客户')

    def __str__(self):
        return self.title

# 货币
class Currency(models.Model):
    title = models.CharField(max_length=10, verbose_name='币种名')
    icon = models.CharField(max_length=3, verbose_name='币种符号')

    def __str__(self):
        return self.title

# 最新编号表
class CurrentNumber(models.Model):
    num = models.IntegerField(verbose_name='序号')
    reference = models.IntegerField(verbose_name='收款编号')
    dist_ref = models.IntegerField(verbose_name='款项分配编号',default=6000)

    def __str__(self):
        return '最新订单号：%s 最新收款编号：%s' %(self.num,self.reference)

# 船公司
class ShipLines(models.Model):
    title = models.CharField(max_length=30, verbose_name="船公司全名")
    shortname = models.CharField(max_length=30, verbose_name="船公司简称")
    link =  models.CharField(max_length=128, verbose_name="网址")

    def __str__(self):
        return "%s %s" % (self.shortname , self.link)


class ApplyOrder(models.Model):
    create_date = models.DateField(auto_now_add=True, verbose_name='申请日期')
    confirm_date = models.DateField( verbose_name='下单日期',null=True, blank=True )
    salesperson = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,
                                    verbose_name='外销员',
                                    limit_choices_to={"roles__title":"外销员"} ,
                                    null=True,
                                 )
    # D 代理订单， L 临时账户（每个客户只能有一个临时账户，预留L1000以下的编号给临时账户使用）
    type_choices = [  (0, 'J'),
                      (1, 'M'),
                      (2, 'X'),
                      (3, 'D'),
                      # (4, 'L'),
                    ]
    order_type = models.SmallIntegerField(choices=type_choices, verbose_name='订单类型')
    order_number = models.CharField(max_length=32, verbose_name='订单号',unique=True, null=True,blank=True)
    sequence = models.IntegerField(verbose_name='订单序号',null=True,blank=True)
    sub_sequence = models.IntegerField(verbose_name='分批号',default=0)
    customer = models.ForeignKey(to=Customer, on_delete=models.RESTRICT,verbose_name='客户',null=True,blank=True)
    goods =  models.CharField(max_length=128, verbose_name='数量-货物')
    remark = models.TextField(verbose_name='详情',default='--')
    currency = models.ForeignKey(to=Currency, on_delete=models.CASCADE,
                                 verbose_name='币种',
                                 default= 1 )
    amount = models.DecimalField(max_digits=15,decimal_places=2,verbose_name='发票金额',default=0)
    rcvd_amount = models.DecimalField(max_digits=15,decimal_places=2,verbose_name='到账金额',default=0)
    collect_amount = models.DecimalField(max_digits=15,decimal_places=2,verbose_name='应收金额',default=0)
    term_choices = [(0, 'FOB'),
                    (1, 'CFR'),
                    (2, 'CIF'),
                    (3, 'EXW'),
                    ]
    term = models.SmallIntegerField(choices=term_choices, verbose_name='贸易条款',default=0)

    status_choices = [(0, '申请中'),
                    (1, '已配单号'),
                    (2, '已下单'),
                    (6, '款齐'),
                    (3, '完结'),
                    (4, '固定账户'),
                    (5, '无效'),
                    ]
    status = models.SmallIntegerField(choices=status_choices, verbose_name='订单状态',default=0)

    def __str__(self):
        return self.order_number


class FollowOrder(models.Model):
    order = models.OneToOneField(to=ApplyOrder, on_delete=models.CASCADE,verbose_name='订单号')
    load_port = models.CharField(max_length=32, verbose_name='起运港',default="Tianjin")
    discharge_port = models.CharField(max_length=32, verbose_name='目的港',default='-')
    ETD = models.DateField(verbose_name='ETD', null=True, blank=True)
    ETA = models.DateField(verbose_name='ETA', null=True, blank=True)
    book_info = models.CharField(max_length=512, verbose_name='订舱信息',default='订舱:')
    load_info = models.CharField(max_length=512, verbose_name='装箱信息',default='装箱:')
    produce_info = models.CharField(max_length=128, verbose_name='生产情况',default='生产:')
    sales_remark = models.CharField(max_length=128,verbose_name='业务备注', default='-')
    salesman = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,
                                    verbose_name='外销员',
                                    limit_choices_to={"roles__title": "外销员"},
                                    null=True, )
    payterm_choices = [(0, '到港付'),
                    (1, '出厂付'),
                    (2, '预付'),
                    ]
    pay_term = models.SmallIntegerField(choices=payterm_choices, verbose_name='付款方式',default=1)
    follow_choices =  [(0, '备货'),
                    (1, '发货'),
                    (5, '装箱'),
                    (2, '单据'),
                    (3, '等款'),
                    (4, '完成'),
                    ]
    status =  models.SmallIntegerField(choices=follow_choices, verbose_name='状态',default=0)
    produce_sequence = models.SmallIntegerField(verbose_name='排产顺序', default=999)
    shipline = models.ForeignKey(to=ShipLines, on_delete=models.CASCADE,
                                 verbose_name='船公司', null=True )
    container = models.CharField(max_length=20, verbose_name='生产情况', default='--')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间', null=True)

    def __str__(self):
        # 注意这个地方要返回的必须是字符串，否则报错
        return self.order.order_number


class Bank(models.Model):
    title = models.CharField(max_length=10, verbose_name='银行名')

    def __str__(self):
        return self.title


class Inwardpay(models.Model):
    create_date = models.DateField(verbose_name='汇入日期')
    payer = models.ForeignKey(to=Payer, on_delete=models.CASCADE,verbose_name='付款人',null=True)
    keyin_user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,verbose_name='录入人',default=3)
    bank =models.ForeignKey(to=Bank, on_delete=models.CASCADE,verbose_name='收款行')
    customer =models.ForeignKey(to=Customer, on_delete=models.CASCADE,verbose_name='客户',null=True,blank=True)
    currency = models.ForeignKey(to=Currency, on_delete=models.CASCADE,verbose_name='币种')
    amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='水单金额',default=0)
    got_amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='实收金额',default=0)
    ttcopy = models.ImageField(upload_to="ttcopy", verbose_name='电汇水单', null=True)
    torelate_amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='待关联金额',default=0)

    status_choices = [(0,'待关联'),
                      (1,'已关联')]
    status = models.SmallIntegerField(choices=status_choices, verbose_name='状态',default=0)
    confirm_choices = [(0, '未确认'),  (1, '业务确认'),(2, '跟单确认'),
                      (4, '财务确认'), (3, '业务.跟单确认'), (5, '业务.财务确认'),
                      (6, '跟单.财务确认'), (7, '全部确认'),
                       ]
    confirm_status = models.SmallIntegerField(choices=confirm_choices, verbose_name='确认',default=0)
    orders = models.ManyToManyField(to=ApplyOrder, through="Pay2Orders", verbose_name='关联记录',blank=True)
    remark = models.TextField(verbose_name='备注', default='-')
    reference = models.IntegerField(verbose_name='收款编号',help_text='避免出现重复记录',null=True,default=1000)


    def __str__(self):
        create_date = self.create_date.strftime("%Y-%m-%d")
        return "%s: %s %s%s (实到：%s)" % (create_date, self.customer, self.currency.icon, str(self.amount),str(self.got_amount))


class Pay2Orders(models.Model):
    relate_date =  models.DateField(auto_now_add=True, verbose_name='关联日期')
    payment = models.ForeignKey(to=Inwardpay, on_delete=models.CASCADE,verbose_name='收款')
    order = models.ForeignKey(to=ApplyOrder, on_delete=models.CASCADE,verbose_name='订单')
    amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='关联金额')
    dist_ref = models.IntegerField(verbose_name='分配编号',default=10000)

    def __str__(self):
        return '%s %s  %s' % (self.payment.create_date.strftime('%Y/%m/%d'),self.order.order_number,self.amount)


class Book(models.Model):
    title = models.CharField(max_length=30,verbose_name="AuthorName")
    def __str__(self):
        return self.title

class ExchangeRate(models.Model):
    update_date = models.DateField(auto_now_add=True, verbose_name='日期')
    currency = models.ForeignKey(to=Currency, on_delete=models.CASCADE,verbose_name='货币')
    rate = models.DecimalField(max_digits=9, decimal_places=3, verbose_name='汇率')

    def __str__(self):
        return '%s %s: %s' % (self.update_date.strftime('%Y/%m/%d'), self.currency.title, self.rate)


# 申请放单
class ApplyRelease(models.Model):
    apply_date =  models.DateField(auto_now_add=True, verbose_name='申请日期')
    applier = models.ForeignKey(to=UserInfo, related_name='applier', on_delete=models.CASCADE, verbose_name='申请人')
    verify_date =  models.DateField(verbose_name='审批日期', null=True, blank=True)
    verifier = models.ForeignKey(to=UserInfo,related_name='verifier', on_delete=models.CASCADE, verbose_name='审批人')
    remark =  models.TextField(verbose_name='备注', default='-')
    decision = models.BooleanField(verbose_name='审批意见', null=True)
    order = models.ForeignKey(to=ApplyOrder, on_delete=models.CASCADE,verbose_name='订单')

    def __str__(self):
        return '%s 放单申请 %s' % (self.apply_date.strftime('%Y/%m/%d'),self.order.order_number)


# 日计划
class DailyPlan(models.Model):
    start_date =  models.DateField(auto_now_add=True, verbose_name='开始')
    remind_date =  models.DateField(verbose_name='提醒',null=True,blank=True)
    end_date =  models.DateField(verbose_name='结束日期',null=True,blank=True)
    content = models.CharField(max_length=512, verbose_name='任务')
    status_choices = [(0, '进行'), (1, '完成'), (2, '提醒'),]
    status = models.SmallIntegerField(choices=status_choices, verbose_name='状态', default=0)
    sequence =  models.IntegerField(verbose_name='排序', default=6)
    link = models.ForeignKey(to=FollowOrder, on_delete=models.CASCADE,verbose_name='关联', null=True, blank=True)
    remark = models.TextField(verbose_name='备注', default='-')
    urgence = models.BooleanField(verbose_name="紧急",default=False)
    user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,verbose_name='创建人',default=3)

    def __str__(self):
        return "%s %s" % (self.start_date.strftime('%Y/%m/%d'), self.content)

"""
创建日期   提醒日期  结束日期  内容  状态  排序  关联   
"""


# 商机表
class Chance(models.Model):
    create_date = models.DateField(auto_now_add=True, verbose_name='创建日')
    channel_choices = [(0, '阿里询盘'), (1, '阿里RFQ'), (2, '1688'),(3, '广交会'), (4, '其他'),]
    channel = models.SmallIntegerField(choices=channel_choices,verbose_name='渠道',default=0)
    category_choices = [(0, '轻钢'), (1, '烤漆'), (2, '配件'), (3, '其他') ]
    category = models.SmallIntegerField(choices=category_choices, verbose_name='产品', default=0)
    company = models.CharField(max_length=128, verbose_name='公司名')
    contact = models.CharField(max_length=128, verbose_name='联系人')
    phone = models.CharField(max_length=28, verbose_name='电话',null=True)
    email = models.EmailField(max_length=128, verbose_name='邮件',null=True)
    remark = models.TextField(verbose_name='详情', default='--')
    owner = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name='跟进外销员',
                              limit_choices_to={"department": 1}, null=True)

    def __str__(self):
        return '商机 %s - %s' % ( self.company[:10],self.create_date.strftime("%Y/%m/%d"))


# 商机跟进表 (与商机是一对多的关系）
class FollowChance(models.Model):
    create_date = models.DateField(auto_now_add=True, verbose_name='创建日')
    chance = models.ForeignKey(to=Chance, on_delete=models.CASCADE, verbose_name='商机')
    remark = models.TextField(verbose_name='跟进记录', default='--')

    def __str__(self):
        return self.create_date.strftime('%Y/%m/%d') + '跟进'+ str(self.chance)




# 货代费用单表
class Charge(models.Model):
    BL_date = models.DateField(verbose_name='提单日期', default="2022-10-01")
    followorder =  models.ForeignKey(to=FollowOrder, on_delete=models.CASCADE, verbose_name='跟单号')
    forwarder = models.ForeignKey(to=Forwarder, on_delete=models.CASCADE, verbose_name='货代')
    seafreight = models.IntegerField(verbose_name='海运费U$',default=0)
    insurance = models.DecimalField(verbose_name='保险费U$',default=0,max_digits=10,decimal_places=2)
    port_charge = models.IntegerField(verbose_name='港杂费￥',default=0)
    trailer_charge = models.IntegerField(verbose_name='拖车费￥',default=0)
    other_charge =  models.IntegerField(verbose_name='其他费用￥',default=0)
    remark = models.TextField(verbose_name='费用说明', default='提单号 港口 箱量')
    status_choices = [(0, '未结'), (1, '美元已结'), (2, '人民币已结'), (3, '结清')]
    status = models.SmallIntegerField(choices=status_choices, verbose_name='结清状态', default=0)

    def __str__(self):
        return  self.followorder.order.order_number + self.forwarder.shortname + '费用'


# 货代结算记录
class ChargePay(models.Model):
    create_date = models.DateField(verbose_name='支付日期',default=datetime.now())
    bank = models.ForeignKey(to=Bank,on_delete=models.CASCADE, verbose_name='出账银行',null=True)
    forwarder = models.ForeignKey(to=Forwarder, on_delete=models.CASCADE, verbose_name='货代')
    currency = models.ForeignKey(to=Currency,on_delete=models.CASCADE, verbose_name='货币',default=1)
    amount =  models.DecimalField( verbose_name='金额',max_digits=10,decimal_places=2)
    ttcopy =  models.ImageField(upload_to="ttcopy", verbose_name='付款水单', null=True)
    charge = models.ManyToManyField(to=Charge, through='PayToCharge', verbose_name='关联账单',null=True,blank=True)
    remark = models.TextField(verbose_name='备注', default='--')
    status_choices = [(0, '待付'), (1, '已出账')]
    status = models.SmallIntegerField(choices=status_choices, verbose_name='支付状态', default=0)

    def __str__(self):
        return self.create_date.strftime('%Y/%m/%d') + self.forwarder.shortname, self.currency.icon + str(self.amount)


class PayToCharge(models.Model):
    chargepay = models.ForeignKey(to=ChargePay,on_delete=models.CASCADE, verbose_name='付费单')
    charge = models.ForeignKey(to=Charge,on_delete=models.CASCADE, verbose_name='费用单')
    currency = models.ForeignKey(to=Currency,on_delete=models.CASCADE, verbose_name='货币',default=1)
    amount = models.DecimalField( verbose_name='金额',max_digits=10,decimal_places=2, default=0)
    remark = models.TextField(verbose_name='备注', default='--')

    def __str__(self):
        return str(self.charge) + str(self.amount)


# class Supplier(models.Model):
#     name = models.CharField(max_length=128, verbose_name='供应商名称')
#
# class Product(models.Model):
#     name = models.CharField(max_length=128, verbose_name='品名')
#     supplier = models.ForeignKey(to=Supplier,on_delete=models.CASCADE, verbose_name='供应商')
#     quote = models.ManyToManyField(to=Customer, through='Quote', verbose_name='关联账单',null=True,blank=True)
#
#
