import hashlib
from PIL import Image
import os

# 加密算法
SALT = "fafmaofda".encode()


def gen_md5(pwd):
    hashlib_obj = hashlib.md5(SALT)
    hashlib_obj.update(pwd.encode())

    return hashlib_obj.hexdigest()


# 压缩图片
def compress_image(outfile):
    # 获取磁盘文件的大小， 大小一般是bit，除以1024等于kb
    file_size = os.path.getsize(outfile) // 1024
    if file_size <= 200:
        return outfile

    # 按0.9的比例逐步压缩，以达到200k以下的目的
    while file_size > 200:
        im = Image.open(outfile)
        x, y = im.size
        # Image.ANTIALIAS 这个参数可以提高图片质量
        outfile_obj = im.resize((int(x * 0.9), int(y * 0.9)), Image.ANTIALIAS)
        try:
            outfile_obj.save(outfile, quality=85)
        except Exception as e:
            break

        file_size = os.path.getsize(outfile) // 1024

    return outfile

# 处理图片压缩的线程任务
def compress_image_task(file_path):
    # print(1111,form.instance.ttcopy.name)
    # print('inwardpay ttcopy.path', form.instance.ttcopy.path)
    # print(3333,form.instance.ttcopy.url)
    result = compress_image(outfile=file_path)
    print(result)