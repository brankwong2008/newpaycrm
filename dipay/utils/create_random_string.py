import random
import string

def get_string(length=10):
    # 定义所有可能的字符，包括大小写字母和数字
    all_characters = string.ascii_letters + string.digits
    # 生成 10 位随机字符串
    random_string = ''.join(random.choice(all_characters) for i in range(length))
    return random_string