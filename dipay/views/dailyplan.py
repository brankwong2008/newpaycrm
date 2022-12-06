
from django.http import JsonResponse
from django.shortcuts import reverse,render,redirect
from django.conf.urls import url
from django.conf import settings
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, checkbox_display, PermissionHanlder,info_display,change_date_display
from dipay.utils.displays import save_display
from dipay.utils.tools import get_choice_value
from dipay.models import DailyPlan, FollowOrder, UserInfo
from dipay.forms.forms import TaskAddModelForm,TaskEditModelForm
import datetime

class DailyPlanHandler(PermissionHanlder,StarkHandler):

    show_list_template = 'dipay/show_dailyplan_list.html'
    page_title = "日计划"

    def get_per_page(self):
        return 15

    # 添加按钮
    has_add_btn = True

    # 搜索时必须把date类型放在第一位，因为后台逻辑是出错，则按第一个正确的来搜索
    search_list = ['start_date', 'content__icontains', 'remark__icontains', ]
    search_placeholder = '搜索 任务 备注 日期'

    def get_order_by_list(self, request):
        if request.GET.get('status')=='1':
            return ['-id',]
        return ['sequence','-id']

    # 添加按钮的显示方法
    def add_btn_display(self,request,*args,**kwargs):
        if self.has_add_btn:
            add_url = self.reverse_add_url(*args,**kwargs)
            return "<a href='%s?get_type=simple' class='btn btn-primary add-record' onclick='return simpleAddDailyPlan(this)'> + </a>" % (add_url)
        else:
            return None

    # 添加完成按钮的显示方法
    def accomplish_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return 'Done'
        else:
            list_url = self.reverse_list_url()
            switch = 'off' if obj.status==1 else 'on'
            return mark_safe("<a href='%s' pk='%s' onclick='return accomplishTask(this)'><i class='fa fa-toggle-%s' ></i></a>" %
                             (list_url, obj.pk,switch ))

    # 重要性的显示方法
    def urgence_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '急'
        else:
            list_url = self.reverse_list_url()
            color = 'red' if obj.urgence else 'grey'
            return mark_safe("<a href='%s' class pk='%s' urgence='%s' onclick='return switchUrgence(this)' style='color:%s'>"
                             "<i class='fa fa-exclamation'></i></a>" %
                             (list_url,obj.pk, obj.urgence, color))

    # 显示关联跟单记录的display
    def link_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return "关联"
        else:
            if obj.link:
                followorder_url = reverse("stark:dipay_followorder_list")+"?q=%s" % obj.link.order.order_number
                return mark_safe("<a href='%s' target='_blank'>%s</a>" % (followorder_url, obj.link))
            else:
                return '--'

    # 显示任务名称的display
    def content_display(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "任务"
        else:
            color = "red" if obj.urgence else ""
            return mark_safe("<span class='text-display %s' onclick='showInputBox(this)' "
                             "id='%s-id-%s'> %s </span>" % (color, "content", obj.pk, obj.content))



    # 任务字段列表
    fields_display = [content_display,info_display('remark'), accomplish_display,
                      urgence_display, info_display('sequence',hidden_xs='hidden-xs'),
                      link_display,get_date_display("start_date",time_format='%m-%d',hidden_xs='hidden-xs'),
                      change_date_display('remind_date',time_format='%m-%d'), ]


    # 按状态筛选
    option_group = [Option(field='status'),]

    # 批量处理： 切换状态
    def batch_switch_status(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        for pk in pk_list:
            obj = self.model_class.objects.filter(pk=pk).first()
            status = '进行' if obj.status==1 else '完成'
            obj.status = get_choice_value(self.model_class.status_choices,status)
            obj.save()
        return JsonResponse({'status':200, 'data':'切换成功'})

    batch_switch_status.text = '切换状态'

    batch_process_list = [batch_switch_status,]

    # 控制筛选框的显示
    filter_hidden = "hidden"
    batch_process_hidden = 'hidden'

    tab_list = [('进行', '进行', 'active'),  ('提醒', '提醒', ""),('完成', '完成', ""), ]
    status_dict = {item[1]: item[0] for item in DailyPlan.status_choices}

    # 定义筛选标签页头
    def get_tabs(self, request, *args, **kwargs):
        tabs = []
        status_dict = {item[1]: item[0] for item in DailyPlan.status_choices}

        for status in self.tab_list:
            status_val = str(status_dict.get(status[0]))
            row = {
                'url': '?status=%s' % status_val,
                'label': status[1],
                'active': status[2],
            }
            if request.GET:
                query_dict = request.GET.copy()
                query_dict._mutable = True
                if query_dict.get('status'):
                    if query_dict.get('status') == status_val:
                        row['active'] = 'active'
                    else:
                        row['active'] = ''
                query_dict["status"] = status_val
                row['url'] = '?%s' % query_dict.urlencode()

            tabs.append(row)
        return tabs

    def get_queryset_data(self, request, is_search=None, *args, **kwargs):
        # 搜索所用的数据另行指定范围
        queryset =  self.model_class.objects.filter(user=request.user)
        # 检查reminder的状态, 如果提醒日期到了，status变更为进行
        for item in queryset.filter(status=self.status_dict.get('提醒')):
            if item.remind_date <= datetime.date.today():
                item.status = self.status_dict.get('进行')
                item.save()

        if is_search:
            return  queryset
        # status 0 进行  1 完成
        if request.GET.get('status'):
            return queryset

        for item in self.tab_list:
            if item[2] == 'active':

                return queryset.filter(status=self.status_dict.get(item[0]))


    # 自定义按钮的权限控制
    def get_extra_fields_display(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        save_url_name = '%s:%s' % (self.namespace, self.get_url_name('save'))
        return [save_display, ] if save_url_name in permission_dict else []

    def get_extra_urls(self):
        patterns = [
            url("^save/$", self.wrapper(self.save_plan), name=self.get_url_name('save')), ]
        return patterns

    # 新增一条记录
    def add_list(self, request, *args, **kwargs):
        if request.method == "GET":
            form = self.get_model_form("add")()
            # 手动更新cc抄送字段的choice，只能自定一个更新的方法，choices源必须是列表等可迭代对象
            form.update_choices('cc',UserInfo.objects.all().exclude(pk=request.user.pk).values_list("id","nickname"))
            model_name = self.model_name
            # 当返回数据给模态框时，get_type = simple，只返回核心内容
            get_type = request.GET.get('get_type')

            # 从跟单页面直接添加关联任务时触发这个功能，以get_type来区分
            if get_type == 'simple':
                self.add_list_template = "dipay/dailyplan_simple_change_list.html"
            return render(request, self.add_list_template or "stark/change_list.html", locals())

        if request.method == "POST":
            form = self.get_model_form(htype="add")(request.POST, request.FILES)
            if form.is_valid():
                result = self.save_form(form, request, False, *args, **kwargs)
                return result or redirect(self.reverse_list_url(*args, **kwargs))
            else:
                return render(request, self.add_list_template or "stark/change_list.html", locals())

    def save_plan(self, request, *args, **kwargs):
        print('save plan request POST:', request.POST)
        # ajax 方式直接修改produce_sequence的值
        if request.is_ajax():
            data_dict = request.POST.dict()
            pk = data_dict.get('pk')
            res = {}
            data_dict.pop('csrfmiddlewaretoken')

            save_obj = DailyPlan.objects.filter(pk=pk).first()
            if not save_obj:
                res = {'status': False, 'msg': 'obj not found'}
            else:
                for item, val in data_dict.items():
                    if item=='urgence':
                        val = False if val.strip() == 'False' else True
                    if item=='remind_date':
                        remind_date = datetime.datetime.strptime(val,'%Y-%m-%d')
                        if remind_date <= datetime.datetime.today():
                            data_dict['status'] = False
                            data_dict['field'] = 'remind_date'
                            data_dict['error'] = '提醒日期要大于当前日期'
                            return JsonResponse(data_dict)

                        save_obj.status = 2
                        save_obj.urgence = True
                        res['msg'] = '提醒设置成功'
                    setattr(save_obj, item, val)
                save_obj.save()
                data_dict['status'] = True
                res.update(data_dict)
            return JsonResponse(res)

    def get_model_form(self,htype=None):
        if htype=="add":
            return TaskAddModelForm
        else:
            return TaskEditModelForm

    # 新建任务的方法
    def save_form(self,form,request,is_update=False,*args, **kwargs):
        if not request.user:
            return

        remind_date = request.POST.get('remind_date')
        # 判断是否有输入提醒日期
        if remind_date:
            remind_date = datetime.datetime.strptime(remind_date, '%Y-%m-%d')
            if remind_date > datetime.datetime.today():
                form.instance.status = 2
            else:
                return JsonResponse({"status": False, "msg": '提醒日期要大于当前日期'})

        # 新增一条任务
        if not is_update:
            print("request.POST",request.POST)
            link_id = request.POST.get('link_id')
            cc = request.POST.getlist('cc[]')

            if link_id:
                form.instance.link_id = link_id
                followorder_obj = FollowOrder.objects.get(pk=link_id)
                form.instance.remark = '%s %s ' % (
                followorder_obj.order.customer.shortname, followorder_obj.order.order_number)
                # 如果设置了提醒日期，判断日期是否大于当前日期

            form.instance.user = request.user
            form.save()

            # 带抄送功能
            if cc:
                content = "%s fm:%s" % (request.POST.get('content'), request.user.nickname)
                for each in cc:
                    form.instance.content = content
                    cc_user = UserInfo.objects.filter(pk=each).first()
                    if cc_user:
                        # 此处是否可以使用pk置为null的方式，然后form.save()来新建一条记录
                        form.instance.pk=None
                        form.instance.user = cc_user
                        form.instance.content = content
                        form.save()

            return JsonResponse({"status":True, "msg":'任务快速添加成功'})

        # 更新一条任务
        form.save()
