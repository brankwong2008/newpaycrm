from dipay.models import Pay2Orders, ApplyOrder

def order_payment_update(order_obj,order_id=None):
    if order_id:
        order_obj = ApplyOrder.objects.filter(order_id=order_id).first()

    order_obj.rcvd_amount = sum([item.amount for item in Pay2Orders.objects.filter(order=order_obj)])
    order_obj.collect_amount = order_obj.amount - order_obj.rcvd_amount
    order_obj.save()
