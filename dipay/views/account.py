from django.shortcuts import render, HttpResponse,redirect,reverse
from django.conf import settings
from django.utils.module_loading import import_string
from stark.utils.common import gen_md5
from django.utils.safestring import mark_safe
from rbac.utils.permissions import init_permissions
from dipay import models

MyUserInfo = import_string(settings.RBAC_USER_MODLE_CLASS)   # 使用import_string 增加代码的通用性

def login(request):
    if request.method == "GET":
        return render(request,"account/login.html")

    if request.method == "POST":
        username = request.POST.get("username")
        pwd = gen_md5(request.POST.get("pwd"))
        user_obj = MyUserInfo.objects.filter(username=username,password=pwd).first()
        if user_obj:
            request.session[settings.LOGIN_KEY] = {"username":user_obj.username, "id":user_obj.id}
            request.user = user_obj
            init_permissions(request,user_obj)

            return redirect(reverse("index"))
        else:
            return render(request,"account/login.html",{"msg":"用户名密码错误"})

def logout(request):
    del request.session[settings.LOGIN_KEY]
    url = reverse("login")
    return redirect(url)


def index(request):
    # print(888888, request.navi_list)
    payment_header_list=['日期','金额','付款人','收款银行','确认状态','关联状态']
    payment_queryset = models.Inwardpay.objects.filter(status=0)
    payment_data_list = []

    for obj in payment_queryset:
        create_date =obj.create_date.strftime('%Y-%m-%d')
        got_amount = '%s %s' % ( obj.currency.icon , obj.got_amount)
        payer = obj.payer.title[:20]
        bank = obj.bank.title
        if obj.confirm_status == 0:
            confirm_url = reverse('stark:dipay_inwardpay_confirm_pay',kwargs=dict(inwardpay_id=obj.pk))
            confirm_status = mark_safe("<a href='%s'> 请认领 </a>" % confirm_url)
            status = '待关联'
        if obj.confirm_status == 1:
            confirm_url = reverse('stark:dipay_inwardpay_confirm_pay', kwargs=dict(inwardpay_id=obj.pk))
            confirm_status = '已认领待确认'
            relate2order_url =  reverse('stark:dipay_inwardpay_relate2order',
                                        kwargs=dict(inwardpay_id=obj.pk,payer_id=obj.payer_id))
            status = mark_safe("<a href='%s'> 待关联 </a>" % relate2order_url )
        else:
            confirm_status = '跟单确认'
            status = '已关联'

        payment_data_list.append((create_date,got_amount,payer,bank,confirm_status, status))

    order_header_list = ['日期', '业务', '订单号', '客户', '数量货物', '发票金额','订单状态','已收款']

    department_dict = {item[1]:item[0] for item in MyUserInfo.department_choices}
    if request.user.department == department_dict.get('业务部'):     # 跟单部
        order_queryset = models.ApplyOrder.objects.filter(salesperson=request.user,status__lte=2)
    elif request.user.department == department_dict.get('跟单部'):
        order_queryset = models.ApplyOrder.objects.filter(status__lte=2)
    else:
        order_queryset = models.ApplyOrder.objects.all()
    order_data_list = []
    print(111111, order_queryset)
    for obj in order_queryset:
        create_date = obj.create_date.strftime('%Y-%m-%d')
        salesperson = obj.salesperson.nickname[0]
        order_number = obj.order_number
        customer = obj.customer.title[:10] if obj.customer else '-'
        goods = obj.goods[:10]
        amount = '%s %s' % ( obj.currency.icon , obj.amount)
        order_status = obj.get_status_display()
        rcvd_amount_url_name = "%s:%s" % ('stark', 'dipay_pay2orders_list')
        rcvd_amount_url = reverse(rcvd_amount_url_name,kwargs={'order_id':obj.id})
        rcvd_amount = mark_safe("<a href='%s'>%s %s</a>" % (rcvd_amount_url, obj.currency.icon , obj.rcvd_amount))
        order_data_list.append([create_date,salesperson,order_number,customer,goods, amount,order_status, rcvd_amount])

    return render(request,"account/index.html",locals())


from django import forms
class BookAddForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['title',]

def book_create(request):

    form =  BookAddForm(request.POST or None)
    print(request.POST)
    if form.is_valid():
        book_obj = form.save()
        return HttpResponse("<script> opener.closePopup(window,'%s','%s','#id_book') </script>"
                            % (book_obj.pk, book_obj))

    return render(request,'dipay/create_record.html',locals())
