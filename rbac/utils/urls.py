
from django.shortcuts import reverse
from django.http import QueryDict

def memory_reverse(request,name):
    """
    功能：将filter中保存的原url中的过滤参数解析还原到原url中，便于跳转回原来的状态
    :param request:
    :param name: 原url的name
    :return: 加上原过滤条件的url
    """
    url = reverse(name)
    filter_term = request.GET.get('_filter')
    if filter_term:
        url = "%s?%s" % (reverse(name), filter_term)

    return url

def memory_url(request,name,*args,**kwargs):
    """
    把原url中的参数打包保存在filter参数中，放在跳转后的新url后面
    便于完成功能后跳转回原状态
    :param request:
    :param name: 跳转后的新url的name
    :param args: url正则路由中需要的无名参数
    :param kwargs: url正则路由中需要的有名参数
    :return: 打包了filter参数的新url
    """
    url = reverse(name, args=args, kwargs=kwargs)

    if request.GET:
        query_dict = QueryDict(mutable=True)  # mutable 可变的，否则query dict不支持修改
        query_dict['_filter'] = request.GET.urlencode()
        url = "{}?{}".format(url, query_dict.urlencode())

    return url