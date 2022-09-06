from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import HttpResponse, redirect
from django.contrib.auth.models import AnonymousUser
import re
from django.utils.module_loading import import_string
from dipay import models

# 按字符串导入模块
rbac_user_model_class = import_string(settings.RBAC_USER_MODLE_CLASS)


class RbacMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        current_url = request.path
        print('current_url:', current_url)
        login_session = request.session.get(settings.LOGIN_KEY, None)
        if not login_session:
            request.user = AnonymousUser()
        else:
            request.user = rbac_user_model_class.objects.filter(pk=login_session.get("id")).first()

        # 1.  访问的是白名单，直接放行
        for reg in settings.WHITE_URL_LIST:
            match_result = re.match(reg, current_url)
            print('reg, match result:', reg, match_result)
            if match_result:
                return

        if not request.user.username:
            return redirect('/login/')

        # 确保自动权限也支持导航栏，所以这句话要提前
        request.navi_list = [{"title": "首页", "url": '/index/'}, ]

        # 2.  如果访问的是要登录但无需权限的名单内的，登录后放行
        for reg in settings.NO_PERMISSION_LIST:
            if re.match(reg, current_url):
                return

        # 3.  需要权限的，需要判断用户是否有权限
        print('following step need permission,user is: ', request.user)
        user_obj = rbac_user_model_class.objects.filter(pk=login_session.get("id")).first()
        if not user_obj:
            request.user = AnonymousUser()
        else:
            request.user = user_obj

        permission_dict = request.session.get(settings.PERMISSION_KEY)

        # 获取进行中的任务的count
        request.task_count = models.DailyPlan.objects.filter(status=0,user=request.user).count()

        # 判断用户的访问路径是否在权限里面
        if permission_dict:
            for key,item in permission_dict.items():
                reg = "^{}$".format(item["url"])
                if re.match(reg, current_url):
                    request.current_url_name = key
                    request.menu = request.session.get(settings.MENU_LIST_KEY)
                    # 设置导航条的nav_list, 如果pid存在，则是三级菜单，显示一级和二级菜单
                    if item['pid']:
                        request.navi_list.extend([{"title": item['p_title'], "url": item['p_url']},
                                                  {"title": item['title'], "url": ""}
                                                  ])
                    # 设置导航条的nav_list, 如果mid存在，则本身是二级菜单，显示一级和自己
                    if item['mid']:
                        request.navi_list.extend([{"title": item['title'], "url": ""}, ])

                    # 找到需要高亮的菜单id
                    request.hilight_menu_id = item['pid'] or item['id']
                    return



       #  return HttpResponse("无访问权限")
