
# 装饰器
import time

def timer(_fun=None, log=None):
    def decorate(fun=_fun):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = fun(*args, **kwargs)
            end = time.time()
            print(f"LOG_{log} {fun.__name__} is runing, time is {end - start} seconds")
            return result
        return wrapper
    if log is None:
        return decorate
    else:
        return decorate(_fun)


def square(x:int):
    return x*x

@timer(log="CONSOLE")
def newsquare(x):
    return x*x

print(newsquare(10))
