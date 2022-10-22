

from stark.service.starksite import StarkHandler,Option
from stark.utils.display import get_date_display,get_choice_text
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from stark.utils.display import PermissionHanlder, info_display, save_display
from django.conf.urls import url
from django.conf import settings
from django.http import JsonResponse
from dipay.utils.tools import str_width_control

class ChargeHandler(StarkHandler):

    fields_display = "__all__"