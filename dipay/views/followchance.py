
from stark.service.starksite import StarkHandler
from dipay.forms.forms import FollowChanceEditForm, FollowChanceAddForm
from stark.utils.display import save_display, PermissionHanlder
from dipay import models
from django.shortcuts import HttpResponse, render,redirect
from django.http import  JsonResponse
from django.conf.urls import url
from django.conf import settings

class FollowChanceHandler(PermissionHanlder,StarkHandler):

    has_add_btn = True
    order_by_list = ['-id',]
    fields_display = "__all__"
    show_list_template = "dipay/show_followchance_list.html"

    # 重新定义路由
    def get_urls(self):
        patterns = [
            url("^list/(?P<chance_id>\d+)/$", self.wrapper(self.show_list), name=self.get_list_url_name),
            url("^add/(?P<chance_id>\d+)/$", self.wrapper(self.add_list), name=self.get_add_url_name),
            url("^edit/(?P<pk>\d+)/(?P<chance_id>\d+)/$", self.wrapper(self.edit_list), name=self.get_edit_url_name),
            url("^del/(?P<pk>\d+)/(?P<chance_id>\d+)/$", self.wrapper(self.del_list), name=self.get_del_url_name),
            url("^create/$", self.wrapper(self.create_list), name=self.get_url_name('create')),
            url("^save/$", self.wrapper(self.save_plan), name=self.get_url_name('save')),
        ]
        # extend方法没有返回值，直接改变自身
        patterns.extend(self.get_extra_urls())
        return patterns

    # model_form的自定义
    def get_model_form(self,handle_type=None):
        return FollowChanceEditForm if handle_type == "edit" else FollowChanceAddForm

    # show_list数据源筛选
    def get_queryset_data(self,request,is_search=None,*args,**kwargs):
        chance_id = kwargs.get("chance_id")
        return self.model_class.objects.filter(chance_id=chance_id)

    # 自定义save_form的新增记录
    def save_form(self,form,request,is_update=False,*args, **kwargs):
        if not is_update:
            form.instance.chance_id = kwargs.get("chance_id")
            form.save()

    # 编辑一条记录
    def edit_list(self, request, pk, *args, **kwargs):
        """编辑跟进记录，路由需要两个参数 pk,chance_id"""
        chance_id = kwargs.get('chance_id')
        chance_obj = models.Chance.objects.filter(pk=chance_id).first()
        form_class = self.get_model_form("edit")
        edit_obj = self.get_edit_obj(request, pk, *args, **kwargs)

        if not edit_obj:
            return HttpResponse("编辑的记录不存在")

        if request.method == "GET":
            # 初始化model form的部分数据
            form = form_class(instance=edit_obj,initial={"opportunity":str(chance_obj)})

            back_url = self.reverse_list_url(chance_id=chance_id)
            namespace = self.namespace
            app_label = self.app_label
            # 自定义列表，外键字段快速添加数据，在前端显示加号
            popup_list = self.popup_list
            return render(request, self.edit_list_template or "stark/change_list.html", locals())

        if request.method == "POST":
            remark = request.POST.get('remark')
            form = form_class(instance=edit_obj, data={'remark':remark})

            if form.is_valid():
                responds = self.save_form(form, request, True, *args, **kwargs)

                return responds or redirect(self.reverse_list_url(*args, **kwargs))
                # return responds
            else:
                return render(request, self.edit_list_template or "stark/change_list.html", locals())

    # 自定义按钮的权限控制
    def get_extra_fields_display(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        save_url_name = '%s:%s' % (self.namespace, self.get_url_name('save'))
        return [save_display, ] if save_url_name in permission_dict else []

    # 快速编辑保存记录
    def save_plan(self, request, *args, **kwargs):
        print('save plan request POST:', request.POST)
        # ajax 方式直接修改produce_sequence的值
        if request.is_ajax():
            data_dict = request.POST.dict()
            pk = data_dict.get('pk')
            res = {}
            data_dict.pop('csrfmiddlewaretoken')

            save_obj = models.FollowChance.objects.filter(pk=pk).first()
            if not save_obj:
                res = {'status': False, 'msg': 'obj not found'}
            else:
                for item, val in data_dict.items():
                    setattr(save_obj, item, val)
                save_obj.save()
                data_dict['status'] = True
                res.update(data_dict)
            return JsonResponse(res)