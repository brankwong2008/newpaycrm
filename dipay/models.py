# Create your models here.
from django.db import models
from rbac.models import MyUser
from datetime import datetime


class UserInfo(MyUser):
    nickname = models.CharField(max_length=30,verbose_name="姓名")
    department_choices = [(1, '业务部'),
                         (2, '跟单部'),
                         (4, '财务部'),
                         (8, '管理部'),
                    ]
    department = models.SmallIntegerField(choices=department_choices, verbose_name='部门', default=1)

    def __str__(self):
            return self.nickname


class Customer(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name='客户名')
    shortname = models.CharField(max_length=20, verbose_name='客户简称',default='-')
    owner = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name='所属外销员',
                                    limit_choices_to={"department":1} , null=True)
    def __str__(self):
        return self.shortname


class Currency(models.Model):
    title = models.CharField(max_length=10, verbose_name='币种名')
    icon = models.CharField(max_length=3, verbose_name='币种符号')

    def __str__(self):
        return self.title

class CurrentNumber(models.Model):
    num = models.IntegerField(verbose_name='序号')

    def __str__(self):
        return str(self.num)


class ApplyOrder(models.Model):
    create_date = models.DateField(auto_now_add=True, verbose_name='申请日期')
    confirm_date = models.DateField( verbose_name='下单日期',null=True, blank=True )
    salesperson = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,
                                    verbose_name='外销员',
                                    limit_choices_to={"roles__title":"外销员"} ,
                                    null=True,
                                    )
    type_choices = [  (0, 'J'),
                      (1, 'M'),
                      (2, 'X'),
                    ]
    order_type = models.SmallIntegerField(choices=type_choices, verbose_name='订单类型')
    order_number = models.CharField(max_length=32, verbose_name='订单号',unique=True, null=True,blank=True)
    sequence = models.IntegerField(verbose_name='订单序号',null=True,blank=True)
    sub_sequence = models.IntegerField(verbose_name='分批号',default=0)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE,verbose_name='客户',null=True,blank=True)
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
                    ]
    term = models.SmallIntegerField(choices=term_choices, verbose_name='贸易条款',default=0)

    status_choices = [(0, '申请中'),
                    (1, '已配单号'),
                    (2, '已下单'),
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
    book_info = models.CharField(max_length=128, verbose_name='订舱信息',default='订舱:')
    load_info = models.CharField(max_length=128, verbose_name='装箱信息',default='装箱:')
    produce_info = models.CharField(max_length=128, verbose_name='生产情况',default='生产:')
    sales_remark = models.CharField(max_length=128,verbose_name='业务备注', default='-')
    payterm_choices = [(0, '到港付'),
                    (1, '出厂付'),
                    (2, '预付'),
                    ]
    pay_term = models.SmallIntegerField(choices=payterm_choices, verbose_name='付款方式',default=1)
    follow_choices =  [(0, '备货'),
                    (1, '发货'),
                    (2, '单据'),
                    (3, '等款'),
                    (4, '完成'),
                    ]
    status =  models.SmallIntegerField(choices=follow_choices, verbose_name='状态',default=0)
    produce_sequence = models.SmallIntegerField(verbose_name='排产顺序', default=999)

    def __str__(self):
        # 注意这个地方要返回的必须是字符串，否则报错
        return '%s %s' % (self.order.order_number,self.order.customer.shortname)


class Bank(models.Model):
    title = models.CharField(max_length=10, verbose_name='银行名')

    def __str__(self):
        return self.title

class Payer(models.Model):
    title = models.CharField(max_length=128, verbose_name='付款人')
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE,verbose_name='客户')

    def __str__(self):
        return self.title


class Inwardpay(models.Model):
    create_date = models.DateField(verbose_name='汇入日期',default=datetime.now())
    payer = models.ForeignKey(to=Payer, on_delete=models.CASCADE,verbose_name='付款人',null=True)
    keyin_user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE,verbose_name='录入人',default=3)
    bank =models.ForeignKey(to=Bank, on_delete=models.CASCADE,verbose_name='收款行')
    customer =models.ForeignKey(to=Customer, on_delete=models.CASCADE,verbose_name='客户',null=True,blank=True)
    currency = models.ForeignKey(to=Currency, on_delete=models.CASCADE,verbose_name='币种')
    amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='水单金额',default=0)
    got_amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='实收金额',default=0)
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

    def __str__(self):
        return "%s %s%s" % (self.payer.title,self.currency.icon, str(self.amount))


class Pay2Orders(models.Model):
    relate_date =  models.DateField(auto_now_add=True, verbose_name='关联日期')
    payment = models.ForeignKey(to=Inwardpay, on_delete=models.CASCADE,verbose_name='收款')
    order = models.ForeignKey(to=ApplyOrder, on_delete=models.CASCADE,verbose_name='订单')
    amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='关联金额')

class Book(models.Model):
    title = models.CharField(max_length=30,verbose_name="AuthorName")
    def __str__(self):
        return self.title



"""

日期	付款人	客户	收款行	货币	金额	状态 
4月10日	Studworks 	Studworks 	Hero广发	美元	15000	待关联


"""





