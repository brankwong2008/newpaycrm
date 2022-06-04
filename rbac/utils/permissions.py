from rbac import models
from django.conf import settings
from collections import OrderedDict
def init_permissions(request,user):
    """
    从数据库获取该用户权限，构建权限字典和二级菜单字典
    :param request:
    :param user: 当前登录用户
    :return: None
    """

    # 一次性跨表查询从数据库获取所有需要的字段，并去重
    permissions_queryset = user.roles.filter(permissions__isnull=False).values("permissions__urls",
                                                                               "permissions__menu_id",
                                                                               "permissions__menu__sequence",
                                                                               "permissions__name",
                                                                               "permissions__id",
                                                                               "permissions__icon",
                                                                               "permissions__title",
                                                                               "permissions__parent_id",
                                                                               "permissions__parent__title",
                                                                               "permissions__parent__urls",).distinct()

    # 一次循环同时创建：动态二级菜单的字典，权限字典
    # 通过权限去找一级菜单，可以避免显示下面没有任何权限的一级菜单
    permission_dict = dict()
    menu_dict = {}
    for item in permissions_queryset:
        permission_dict[item['permissions__name']] = {
            "url": item['permissions__urls'],
            "id": item['permissions__id'],
            "title": item['permissions__title'],
            "mid": item['permissions__menu_id'],
            "msq": item['permissions__menu__sequence'],
            "pid": item['permissions__parent_id'],
            "p_title": item["permissions__parent__title"],
            "p_url": item["permissions__parent__urls"],
        }
        #  menu_id不为null的是二级菜单
        if item["permissions__menu_id"]:
            node = {"title": item["permissions__title"],
                    "id": item['permissions__id'],
                    "url": item["permissions__urls"],
                    "icon": item["permissions__icon"]}

            # 此处menu_dict的键是元组（menu_sequence, menu_id）, 方便进行定制排序
            primary_menu = menu_dict.get((item['permissions__menu__sequence'],item["permissions__menu_id"]))
            if primary_menu:
                primary_menu["children"].append(node)
            else:
                menu_obj = models.Menu.objects.get(pk=item["permissions__menu_id"])
                menu_dict[(item['permissions__menu__sequence'],item["permissions__menu_id"])] = {"title": menu_obj.title,
                                                           "icon": menu_obj.icon,
                                                           "mid": menu_obj.id,
                                                           "class": "hide",
                                                           "children": [node, ], }

    # menu_dict 的结构 { (menu_id,menu__sequence): { 'title':xx, 'icon':xx, 'mid':xx, 'children':[ {},{}  ]   }    }
    # 把动态二级菜单的字典存入session

    # 对menu字典进行排序
    new_menu_dict = OrderedDict()
    for k in sorted(menu_dict.keys()):
        new_menu_dict[k[0]] = menu_dict[k]
    request.session[settings.MENU_LIST_KEY] = new_menu_dict

    # 把权限字典存入session
    request.session[settings.PERMISSION_KEY] = permission_dict

    print(menu_dict,permission_dict)

    return