
from stark.service.starksite import StarkHandler
from stark.utils.display import PermissionHanlder

class PayerHandler(PermissionHanlder,StarkHandler):

    search_list = ['title__icontains','customer__title__icontains']
    search_placeholder = '搜索 付款人 客户'

    fields_display = ['id','title','customer']

    def get_queryset_data(self,request,*args,**kwargs):
        if request.user.username == "brank":
            return self.model_class.objects.all()
        if request.user.department == 8:
            return self.model_class.objects.all()
        elif request.user.department == 1:
            return self.model_class.objects.filter(customer__owner = request.user)



