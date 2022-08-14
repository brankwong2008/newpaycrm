def is_chinese(c):
    return  u'\u4e00' <= c <= u'\u9fff'


def str_width_control(s,width):
    count0=0  # 字符数
    count1=0  # 宽度值
    for c in s:
        count0 += 1
        count1 += 2 if is_chinese(c) else 1
        if count1 >= width:
            return s[:count0]+'..' if count0<len(s) else s