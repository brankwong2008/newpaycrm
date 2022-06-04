#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
STARK组件的使用文档

1. 把stark文件夹拷贝到项目目录

2. 在settings中注册stark组件
           INSTALLED_APPS = [
            'stark.apps.StarkConfig',
        ]

3. 在每个app文件夹中(除了rbac和主文件夹）新建一个stark.py文件, 并导入：from stark.service.starksite import site

4. 在stark.py中注册model表和对应的handler
    from stark.service.starksite import site
    from work import models
    from work.views.userinfo import MyUserInfoHandler

    # 注册model和handler
    site.register(models.MyUserInfo,MyUserInfoHandler)

5. 如果多个handle对应同一个model，需要加上别名前缀，加以区分
    site.register(models.Customer,PublicCustomerHandler,prev="public")
    site.register(models.Customer,PrivateCustomerHandler,prev="private")


6. 编写对应个handler
    定制参数
    - has_add_btn =  False    # 添加按钮是否显示
    - fields_display =['name','age', check_score_display]  #定制list_view列表显示的列名
        - 定制功能按钮
                def check_score_display(self, obj=None, is_header=False, *args, **kwargs):
                    # self是handler对象，obj是queryset里面每条记录对象
                    if is_header:
                        return "查成绩"
                    else:
                        list_score_url = reverse('stark:work_studenthomework_list_stu', kwargs={'pk': obj.id})
                        return mark_safe("<a href='%s'> %s </a> " % (list_score_url, '查成绩',))

    - 定制路由 url patterns
         def get_urls(self):
            patterns = [
                url("^list/$", self.wrapper(self.show_list), name= self.get_list_url_name),
                url("^add/(?P<classes_id>\d+)/$", self.wrapper(self.add_list), name=self.get_add_url_name),
                url("^edit/(?P<classes_id>\d+)/(?P<pk>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
                url("^del/(?P<pk>\d+)/$", self.wrapper(self.del_list), name=self.get_del_url_name),
            ]
            # extend方法没有返回值，直接改变自身
            patterns.extend(self.get_extra_urls())
            return patterns

    - 定制modelform
        def get_model_form()      # 定制添加和编辑所用的modelform

    - 定制form的保存方法
            def save_form(self,form,request,is_update=False,*args, **kwargs):
                if not is_update:
                    classes_id = kwargs.get('classes_id')
                    form.instance.classes_id = classes_id
                form.save()

    - 定制批量处理方法
        def batch_to_public(self, request):
            pk_list = request.POST.getlist("pk")
            user = request.session.get(settings.LOGIN_KEY)
            if not user:
                return HttpResponse("请先登录")
            self.model_class.objects.filter(id__in=pk_list, consultant=user["id"]).update(consultant=None)
            return redirect(self.reverse_list_url())
        batch_to_public.text = "批量剔除到公户"
        batch_process_list = [batch_to_public, ]

    - 定制模糊搜索
        search_list = ['name__contains','age__lt']    # 几个条件之间是'OR'的关系

    - 定制组合筛选
        from stark.service.starksite import Option
        option_group = [Option('classes'),Option('country')]
        后面代码略去，主要思路就是：从数据库获取每个字段关联的原表数据或者choices数据，然后展现在前端，同时给每个条目动态生成url和active属性


    - 定制列表显示的数据源queryset
        def get_queryset_data(self, request, *args, **kwargs):
            customer_id = kwargs.get("customer_id")
            return self.model_class.objects.filter(customer_id=customer_id)

    - 定制要编辑view要编辑的对象
        def get_edit_obj(self, request, pk, *args, **kwargs):
            user_id = request.user.id
            customer_id = kwargs.get("customer_id")
            if self.model_class.objects.filter(pk=pk, customer_id=customer_id, consultant=user_id).exists():
                return self.model_class.objects.filter(pk=pk).first()

    - 定制删除view要删除的对象
        def get_del_obj(self, request, pk, *args, **kwargs):
                return self.model_class.objects.filter(pk=pk).first()

    - 基于limit_choice_to 关联FK或M2M进行筛选，在models中设置外键的筛选

    - 控制粒度细化到按钮
        在按钮控制的方法里面判断权限字典中是否有此权限，然后确定返回按钮或者None
        把以上公共方法放到一个类里面PermissionHandler, 文件位置：/stark/utils/display/
            注意权限名是否带namespace的问题，可能会导致匹配失败
        然后由业务的handler左继承它
        class StudentHandler(PermissionHandler, StarkHandler)


"""