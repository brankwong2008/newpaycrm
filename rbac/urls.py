# from django.contrib import admin
from django.conf.urls import url
from django.urls import path, re_path, include
from rbac.views import role, user, permission, menu

app_name = "rbac"

urlpatterns = [

    path('role/', role.role_list, name="role_list"),
    re_path(r'role/edit/(?P<pk>\d+)/', role.role_edit, name="role_edit"),
    re_path(r'role/del/(?P<pk>\d+)/', role.role_del, name="role_del"),
    path('role/add/', role.role_add, name="role_add"),
    path('role/list/', role.role_list, name="role_list"),

    # path('user/list/', user.user_list, name="user_list"),
    # re_path(r'user/edit/(?P<pk>\d+)/', user.user_edit, name="user_edit"),
    # re_path(r'user/del/(?P<pk>\d+)/', user.user_del, name="user_del"),
    # path(r'user/add/', user.user_add, name="user_add"),
    # re_path(r'^user/reset_pwd/(?P<pk>\d+)/$', user.user_reset_pwd, name="reset_pwd"),

    path('permission/list/', permission.permission_list, name="permission_list"),
    re_path(r'permission/add/(?P<sid>\d+)/', permission.permission_add, name="permission_add"),
    re_path(r'permission/mult_add/(?P<sid>\d+)/', permission.permission_mult_add, name="permission_mult_add"),
    re_path(r'permission/mult_edit/(?P<sid>\d+)/', permission.permission_mult_edit, name="permission_mult_edit"),
    re_path(r'permission/edit/(?P<pk>\d+)/', permission.permission_edit, name="permission_edit"),
    re_path(r'^permission/del/(?P<pk>\d+)/$', permission.permission_del, name="permission_del"),
    url(r'^multipermission/del/(?P<pk>\d+)/$', permission.multi_permission_del, name="multi_permission_del"),
    url('permission/auto_crawle/', permission.auto_crawle_permission, name="auto_crawle_permission"),
    url('permission/distribute/', permission.permission_distribute, name="permission_distribute"),

    url(r'menu/add/', menu.menu_add, name="menu_add"),
    url(r'menu/list/', menu.menu_list, name="menu_list"),
    url(r'^menu/edit/(?P<pk>\d+)/$', menu.menu_edit, name="menu_edit"),
    url(r'^menu/del/(?P<pk>\d+)/$', menu.menu_del, name="menu_del"),

    url(r'^second_menu/add/$', menu.second_menu_add, name="second_menu_add"),
    url(r'second_menu/edit/(?P<pk>\d+)/', menu.second_menu_edit, name="second_menu_edit"),
    url(r'second_menu/del/(?P<pk>\d+)/', menu.second_menu_del, name="second_menu_del"),

]
