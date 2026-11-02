# -*- coding: utf-8 -*-
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder


class PriceConfigHandler(PermissionHanlder, StarkHandler):
    page_title = "价格参数"

    fields_display = "__all__"

    search_list = ['key__icontains', 'title__icontains']
    search_placeholder = '搜索 参数名/说明'
