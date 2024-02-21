
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import PermissionHanlder



class ExchangeRateHandler(PermissionHanlder, StarkHandler):
    page_title = "汇率"

    search_list = ["update_date","currency__title__icontains"]

    search_placeholder = '搜日期(如2022-01-01）'

    # 加入一个组合筛选框, default是默认筛选的值，必须是字符串
    option_group = [
        Option(field='currency', verbose_name="币种" ),
    ]

