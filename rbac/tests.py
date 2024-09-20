from django.test import TestCase
import os, django
import sys

# Create your tests here.
#
# from django_redis import get_redis_connection
#
# conn = get_redis_connection()    # 连接redis 自动从settings.CACHE中获取配置

# redis的连接也可以这么写

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paycrm.settings')
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    django.setup()
    from django_redis import get_redis_connection

    conn = get_redis_connection()
    conn.set("name","Kaifeng")
    print("name",conn.get("name").decode("utf8"))
    conn.delete("hobby")
    conn.llen("hobby")
    print('conn.llen("hobby")',conn.llen("hobby"))
    # conn.lpush("hobby","music")
    # conn.lpush("hobby", "read")
    # conn.lpush("hobby", "games")
    # conn.lpush("hobby", "games2")
    # conn.lpush("hobby", "games3")
    conn.rpush("hobby", *[1,2,3,4,5])
    result = conn.lrange("hobby",0, 5)
    result = [ x.decode("utf8") for x in result]
    idx = result.index("1")
    print(result,"before change")
    temp = result[idx]
    result[idx]=result[idx-1]
    result[idx-1]=temp
    print(result,"final result")






# key="age"
# conn.set(key, 12, ex=300)
# per_page_redis = conn.get(key)
#
# print("per_page_redis",per_page_redis)









