
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
from dipay.views.inwardpay_account import InwardPayAccountHandler
from dipay.views.dailyplan import DailyPlanHandler
from dipay.views.chance import ChanceHandler
from dipay.views.followchance import FollowChanceHandler
from dipay.views.charge import ChargeHandler
from dipay.views.chargepay import ChargePayHandler
from dipay.views.forwarder_charge import ForwarderChargeHandler
from dipay.views.forwarder_chargepay import ForwarderChargePayHandler
from dipay.views.chance_stats import ChanceStatsHandler
from dipay.views.forwarder import ForwarderHandler
from dipay.views.ports import PortsHandler




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

# 收款记录(财务版）
site.register(models.Inwardpay, InwardPayAccountHandler, prev='account')

# 收款订单关联记录
site.register(models.Pay2Orders, Pay2OrdersHandler)

# 付款人
site.register(models.Payer,PayerHandler)

# 船公司
site.register(models.ShipLines)

# 港口
site.register(models.Ports, PortsHandler)

# 最新编码
site.register(models.CurrentNumber)

# 申请放单
site.register(models.ApplyRelease, ApplyReleaseHandler)

# 申请放单审核
site.register(models.ApplyRelease, ApplyReleaseVerifyHandler,prev='verify')

# 每日任务
site.register(models.DailyPlan, DailyPlanHandler)

# 货代表
site.register(models.Forwarder, ForwarderHandler)

# 商机表
site.register(models.Chance, ChanceHandler)

# 商机统计表
site.register(models.Chance, ChanceStatsHandler, prev='stats')

# 跟进表
site.register(models.FollowChance,FollowChanceHandler )

# 货代费用表
site.register(models.Charge, ChargeHandler)

# 货代费用付款单
site.register(models.ChargePay, ChargePayHandler )

# 货代费用表-货代版
site.register(models.Charge, ForwarderChargeHandler,prev='forwarder')

# 货代费用付款单-货代版
site.register(models.ChargePay, ForwarderChargePayHandler,prev='forwarder' )

# 产品管理
site.register(models.Product )

# 供应商管理
site.register(models.Supplier )

# 报价管理
site.register(models.Quote )