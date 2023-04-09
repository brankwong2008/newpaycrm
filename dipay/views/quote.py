from django.shortcuts import reverse
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder
from django.utils.safestring import mark_safe
from dipay.utils.tools import str_width_control
from dipay.models import Product, ProductPhoto, Quote, ModelNumbers


class QuoteHandler(StarkHandler):
    page_title = "报价管理"

    search_list = ['modelnumbers__product__title__icontains']
    search_placeholder = "搜索 品名"

    order_by_list = ["-create_date"]