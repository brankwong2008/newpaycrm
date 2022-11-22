
from stark.service.starksite import StarkHandler,Option
from stark.utils.display import get_date_display,get_choice_text
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from stark.utils.display import PermissionHanlder, info_display, save_display
from django.conf.urls import url
from django.conf import settings
from django.http import JsonResponse
from dipay.utils.tools import str_width_control
from dipay.forms.forms import ChanceModelForm

class ChanceHandler(PermissionHanlder,StarkHandler):
    page_title = "商机"

    show_list_template = "dipay/show_chance_list.html"

    search_list = ['company__icontains','contact__icontains']
    search_placeholder = "搜索 客户 联系人"

    # 加入一个组合筛选框, default是默认筛选的值，必须是字符串
    option_group = [
        Option(field='channel'),
        Option(field='category', verbose_name='类别'),
        # Option(field='category', filter_param={'roles__title': '外销员'}, verbose_name='业务'),
    ]

    # 跟进记录display
    def follow_chance_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '跟进记录'
        else:
            follow_chance_url = reverse("stark:dipay_followchance_list", kwargs={"chance_id":obj.pk})
            return mark_safe('<a href="%s" target="_blank">跟进</a>' % follow_chance_url)

    # 邮件display
    def email_display(self, obj=None, is_header=False, *args, **kwargs):
        if is_header:
            return '邮件'
        else:
            mailto = "<a href='mailto:%s'> %s </a>" % (obj.email,obj.email)
            return mark_safe(mailto)

    # 详情display
    def remark_display(max_length = None):
        def inner(handler_obj, obj=None, is_header=None, *args, **kwargs):
            if is_header:
                return '详情'
            else:
                remark, is_long = str_width_control(obj.remark,max_length)
                if is_long:
                    remark_text = "<span id='remark_%s' text='%s'>%s</span>" % (obj.pk, obj.remark, remark) + \
                                  "<i class='fa fa-chevron-down more' pk='%s' onclick='expandRemark(this)'></i>" % obj.pk
                else:
                    remark_text = remark

                return mark_safe(remark_text)
        return inner


    fields_display = [get_date_display('create_date'),
                      get_choice_text('channel'),
                      get_choice_text('category'),
                      'company',
                      'contact',
                      'phone',
                      email_display,
                      remark_display(max_length=130),
                      follow_chance_display,
                      'owner']

    def  get_queryset_data(self,request,is_search=None,*args,**kwargs):
        if request.user.username in ["brank","zhangweiguo"] :
            return self.model_class.objects.all()
        else:
            return self.model_class.objects.filter(owner=request.user)

    def get_extra_urls(self):
        patterns = [
            url("^save/$", self.wrapper(self.save_record), name=self.get_url_name('save')),
        ]

        return patterns

  # 自定义按行存储按钮的权限控制
    def get_extra_fields_display(self, request, *args, **kwargs):
        permission_dict = request.session.get(settings.PERMISSION_KEY)
        save_url_name = '%s:%s' % (self.namespace, self.get_url_name('save'))

        print('自定义存储的权限控制， permmisons:',permission_dict)

        if save_url_name in permission_dict:
            return [save_display, ]
        else:
            return []

    def get_model_form(self,type=None):
        return ChanceModelForm

    def save_form(self,form,request,is_update=False,*args, **kwargs):
        if not is_update:
            form.instance.owner = request.user
        form.save()

