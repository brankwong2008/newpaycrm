
from stark.service.starksite import StarkHandler, Option
from stark.utils.display import PermissionHanlder
from django_redis import get_redis_connection


class ExchangeRateHandler(PermissionHanlder, StarkHandler):
    page_title = "汇率"

    search_list = ["update_date","currency__title__icontains"]

    search_placeholder = '搜日期(如2022-01-01）'

    # 加入一个组合筛选框, default是默认筛选的值，必须是字符串
    option_group = [
        Option(field='currency', verbose_name="币种" ),
    ]

    # def get_per_page(self):
    #     return 20

    # 单页面显示记录条数的选择下拉框内容，需要同时启动redis，也需要有js配合
    per_page_options = [
        {"val": 10, "selected": ""},
        {"val": 20, "selected": ""},
        {"val": 50, "selected": ""},
    ]

    def get_per_page(self):
        key = "%s:%s" % (self.request.path, self.request.user)
        conn = get_redis_connection()
        print("key", key)

        per_page_count = self.request.POST.get("per_page_count")
        if per_page_count:
            conn.set(key, per_page_count, ex=300)
            return int(per_page_count)

        per_page_redis = conn.get(key)
        print("get key working:",per_page_redis)
        if per_page_redis:
            return int(per_page_redis.decode("utf8"))
        return 20



