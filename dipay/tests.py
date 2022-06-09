from django.test import TestCase

# Create your tests here.

s="""0, order_number 
1, salesperson 
3, status 
4, customer 
6, goods
7, term 
8, ports 
9, confirmed_date
10, ETD 
11,ETA 
12, load_info
13, book_info 
14, payterm
15, amount 
16, deposit 
17, balance_USD
18, balance_RMB
19,  payment1
20,  payment2  """

row_list = []
row = ''
for a in s:
    if a != '\n':
        row += a
    else:
        num, field = row.split(',')
        row_list.append((int(num.strip()),field.strip()))
        row = ''



print(row_list)

