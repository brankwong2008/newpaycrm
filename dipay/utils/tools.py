import os
import time
import random

def is_chinese(c):
    return  u'\u4e00' <= c <= u'\u9fff'


def str_width_control(s,width):
    count0=0  # 字符数
    count1=0  # 宽度值
    for c in s:
        count0 += 1
        count1 += 2 if is_chinese(c) else 1
        if count1 > width:
            return s[:count0], True
    # 如果for执行完毕都没有触发到width长度，则直接返回s
    return s, False

def get_choice_value(orm_choices,text):
    for item in orm_choices:
        if item[1]==text:
            return item[0]
    return None



def gen_file_name(pre, file_name):
    # 生成带时间戳的文件名
    print("file_name", file_name)
    ext = os.path.splitext(file_name)[1]
    # 合成文件名
    fn =time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100)
    return pre + fn + ext