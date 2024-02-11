import os
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder


class ExchangeRateHandler(PermissionHanlder, StarkHandler):
    page_title = "汇率"

