
from django.http import JsonResponse
from django.shortcuts import reverse,render,redirect
from django.conf.urls import url
from django.conf import settings
from django.utils.safestring import mark_safe
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import get_date_display, checkbox_display, PermissionHanlder,info_display,follow_date_display
from dipay.utils.displays import save_display
from dipay.utils.tools import get_choice_value
from dipay.models import DailyPlan
from dipay.forms.forms import TaskAddModelForm,TaskEditModelForm

class DailyPlanHandler(PermissionHanlder,StarkHandler):

    show_list_template = 'dipay/show_dailyplan_list.html'
    order_by_list = ['sequence',]

    # 添加按钮
    has_add_btn = True

    # 添加按钮的显示方法
    def add_btn_display(self,request,*args,**kwargs):
        if self.has_add_btn:
            add_url = self.reverse_add_url(*args,**kwargs)
            return "<a href='%s' class='btn btn-primary add-record'> <i class='fa fa-plus'></i> </a>" % (add_url)
        else:
            return None

    # 添加完成按钮的显示方法
    def accomplish_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return 'Done'
        else:
            list_url = self.reverse_list_url()
            switch = 'off' if obj.status else 'on'
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



    # 任务列表

    fields_display = [checkbox_display, content_display, accomplish_display,urgence_display, info_display('remark'),info_display('sequence'), link_display,get_date_display("start_date"),follow_date_display("end_date")   ]


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

    tab_list = [('进行', '进行', 'active'), ('完成', '完成', ""), ]
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
        if is_search:
            return  queryset
        # status 0 进行  1 完成
        if request.GET.get('status'):
            return queryset

        for item in self.tab_list:
            if item[2] == 'active':
                return queryset.filter(status=self.status_dict.get(item[0]))

    search_list = ['content__icontains', 'start_date']
    search_placeholder = '搜索 日期 任务'

    # 自定义按钮的权限控制
    def get_extra_fields_display(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        save_url_name = '%s:%s' % (self.namespace, self.get_url_name('save'))
        return [save_display, ] if save_url_name in permission_dict else []

    def get_extra_urls(self):
        patterns = [
            url("^save/$", self.wrapper(self.save_plan), name=self.get_url_name('save')), ]
        return patterns

    def save_plan(self, request, *args, **kwargs):
        print('save plan request POST:', request.POST)
        # ajax 方式直接修改produce_sequence的值
        if request.is_ajax():
            data_dict = request.POST.dict()
            pk = data_dict.get('pk')
            data_dict.pop('csrfmiddlewaretoken')

            save_obj = DailyPlan.objects.filter(pk=pk).first()
            if not save_obj:
                res = {'status': False, 'msg': 'obj not found'}
            else:
                for item, val in data_dict.items():
                    if item=='urgence':
                        val = False if val.strip() == 'False' else True
                    setattr(save_obj, item, val)
                save_obj.save()
                data_dict['status'] = True
                res = data_dict
            return JsonResponse(res)

    def get_model_form(self,type=None):
        if type=="add":
            return TaskAddModelForm
        else:
            return TaskEditModelForm

    # 新建任务的方法
    def save_form(self,form,request,is_update=False,*args, **kwargs):
        if not request.user:
            return

        if not is_update:
            form.instance.user = request.user
        form.save()