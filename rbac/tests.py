from django.test import TestCase

# Create your tests here.


f = open("info",'rt',encoding='utf8')
text = []
# with open("goodinfo.txt",'wt',encoding='utf8') as file_obj:
#     for line in f:
#         line = "\'{}\'".format(line.strip())
#         text.append(line)
#     file_obj.write(','.join(text))


with open("goodinfo.txt",'wt',encoding='utf8') as file_obj:
    for line in f:
        line = f"'{line.strip()}'"
        text.append(line)
    file_obj.write(','.join(text))








