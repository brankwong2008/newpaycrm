from django.template import Library

register = Library()


@register.filter
def div(a,b):
    """
    模板过滤器：基本除法
    :param a: 被除数
    :param b: 除数
    :return:  保留两位小数的结果
    """
    return round(a/b,2)

@register.filter
def multiply(a,b):
    """
    模板过滤器：基本除法
    :param a: 被除数
    :param b: 除数
    :return:  保留两位小数的结果
    """
    return round(a*b,2)

