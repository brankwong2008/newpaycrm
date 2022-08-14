# 测试压缩图片的方法

from PIL import Image
import os
from django.conf import settings

# def compress_image(outfile):
#     # 获取磁盘文件的大小， 大小一般是bit，除以1024等于kb
#     file_size = os.path.getsize(outfile)//1024
#     if file_size <= 200:
#         return outfile
#
#     while file_size > 200:
#         im = Image.open(outfile)
#         x,y = im.size
#         outfile_obj = im.resize((int(x*0.9),int(y*0.9)), Image.ANTIALIAS)
#         try:
#             outfile_obj.save(outfile, quality=85)
#         except Exception as e:
#             break
#
#         file_size = os.path.getsize(outfile)//1024
#
#     return outfile
#
# ret = compress_image('/Users/wongbrank/PycharmProjects/pythonProjec/newpaycrm/media/WechatIMG11334的副本.jpeg')

# 测试中英文混杂字符串的

def is_chinese(c):
    if u'\u4e00' <= c <= u'\u9fff':
        return True
    else:
        return False


def width_control(s, width):
    count0 = 0  # 字符数
    count1 = 0  # 宽度值
    for c in s:
        count0 += 1
        if is_chinese(c):
            count1 += 2
        else:
            count1 += 1
        print('count0 count1',count0,count1)
        if count1 >= width:
            return s[:count0]

