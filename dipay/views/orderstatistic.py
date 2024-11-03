from stark.service.starksite import StarkHandler
from stark.utils.display import  PermissionHanlder
from django.shortcuts import HttpResponse, render
from django.db.models import Sum
from dipay.models import ExchangeRate


class OrderStatisticHandler(PermissionHanlder,StarkHandler):
    # 添加按钮
    has_add_btn = False
    page_title = "订单统计"

    # 列表页面
    def show_list(self, request, *args, **kwargs):


        page_title = self.page_title
        model_class = self.model_class  # FollowOrder

        # 列表抬头和表体
        header_list = ["序号", "统计项目", "数值"]
        data_list = []

        # 统计已经出货的，单据和收款两个状态的应收账款合计
        total_collect_queryset = model_class.objects.filter(status__in=[2,3],order__order_type__in=[0,1,]).values("order__currency__title").annotate(total_to_collect= Sum("order__collect_amount"))

        count = 0
        total_amount = 0
        for item in total_collect_queryset:
            count += 1
            currency_title = item["order__currency__title"]
            currency_label = "金凯{}应收账款".format(currency_title)
            total_to_collect_amount =format( item.get("total_to_collect"),",f")
            row = {"active":"", "data":[count,currency_label,total_to_collect_amount]}
            data_list.append(row)
            # sum the total amount in RMB, 1st to get exchange rate.
            currency_obj = ExchangeRate.objects.filter(currency__title=currency_title).order_by("-id").first()
            # RMB has no exchange record.
            exchang_rate = currency_obj.rate if currency_obj else 1
            total_amount += item.get("total_to_collect") * exchang_rate

        # 最后一行加入折合人民币统计
        row =  {"active":"", "data":["合计"," 折合人民币 ", format(total_amount,",.2f")]}
        data_list.append(row)

        return render(request, "stark/show_list.html", locals())


