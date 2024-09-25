from django.template import Library
from django.conf import settings
from django.shortcuts import reverse
from django.http import QueryDict
from rbac.utils import urls

register = Library()

@register.inclusion_tag("left_menu.html")
def left_menu(request):
    menu_dict = request.session[settings.MENU_LIST_KEY]

    if hasattr(request,"hilight_menu_id"):
        for primary_menu in menu_dict.values():
            # 默认所有的一级目录都是闭合的，只有高亮的子目录的一级目录不是闭合的
            primary_menu['class'] = 'hide'
            for item in primary_menu['children']:
                # 默认所有的子级目录不高亮
                item['class'] = ''
                if request.hilight_menu_id == item['id']:
                    item['class']='hilight'
                    primary_menu['class']=''

    return {"menu_list":menu_dict.values()}

@register.filter
def btn_control(request,name):
    permission_dict = request.session[settings.PERMISSION_KEY]
    if name in permission_dict:
        return True

@register.simple_tag
def memory_url(request,name,*args,**kwargs):
    return urls.memory_url(request,name,*args,**kwargs)
