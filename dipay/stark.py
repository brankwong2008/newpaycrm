
from stark.service.starksite import site
from . import models
from dipay.views.applyorder import ApplyOrderHandler
from dipay.views.inwardpay import InwardPayHandler
from dipay.views.pay2order import Pay2OrdersHandler
from dipay.views.userinfo import MyUserInfoHandler
from dipay.views.applyorder_verify import ApplyOrderVerifyHandler
from dipay.views.customer import CustomerHandler
from dipay.views.payer import PayerHandler
from dipay.views.followorder import FollowOrderHandler
from dipay.views.weeklyplan import WeekelyPlanHandler
from dipay.views.applyrelease import ApplyReleaseHandler
from dipay.views.applyrelease_verify import ApplyReleaseVerifyHandler


# 用户信息管理
site.register(models.UserInfo,MyUserInfoHandler)

# 订单跟进
site.register(models.FollowOrder, FollowOrderHandler)

# 排产计划
site.register(models.FollowOrder, WeekelyPlanHandler,prev='plan')

# 币种
site.register(models.Currency)

# 银行
site.register(models.Bank)

# 客户
site.register(models.Customer,CustomerHandler)

# 申请订单号
site.register(models.ApplyOrder,ApplyOrderHandler)

# 申请订单号-审核
site.register(models.ApplyOrder,ApplyOrderVerifyHandler,prev='verify')

# 收款记录
site.register(models.Inwardpay, InwardPayHandler)

# 收款记录
site.register(models.Inwardpay, InwardPayHandler)

# 收款订单关联记录
site.register(models.Pay2Orders, Pay2OrdersHandler)

# 付款人
site.register(models.Payer,PayerHandler)

# 最新编码
site.register(models.CurrentNumber)

# 申请放单
site.register(models.ApplyRelease, ApplyReleaseHandler)

# 申请放单审核
site.register(models.ApplyRelease, ApplyReleaseVerifyHandler,prev='verify')

