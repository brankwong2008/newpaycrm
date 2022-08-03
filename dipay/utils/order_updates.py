from dipay.models import Pay2Orders, ApplyOrder
from django.db.models import Sum

def order_payment_update(order_obj,order_id=None):
    if order_id:
        order_obj = ApplyOrder.objects.filter(order_id=order_id).first()

    # order_obj.rcvd_amount = sum([item.amount for item in Pay2Orders.objects.filter(order=order_obj)])


    total_rcvd_dict = Pay2Orders.objects.filter(order=order_obj).aggregate(total_rcvd = Sum('amount'))
    # total_rcvd_dict {'total_rcvd': Decimal('4600.00')} <class 'dict'>
    print('total_rcvd', total_rcvd_dict,type(total_rcvd_dict))
    # 直接用布尔运算，比条件判断效率更高
    order_obj.rcvd_amount = total_rcvd_dict['total_rcvd'] or 0
    order_obj.collect_amount = order_obj.amount - order_obj.rcvd_amount
    order_obj.save()
