import requests
from bs4 import BeautifulSoup
import pymysql
import datetime


dollar_names = ["美元","加拿大元","港币","澳大利亚元"]

def get_exchange_rates():
    # 中国银行外汇牌价的URL（请替换为实际网址）
    header = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'
    }
    url = "https://www.boc.cn/sourcedb/whpj/"  # 这个是假设的地址，需要确认实际网址

    try:
        # 发送GET请求
        response = requests.get(url=url,headers=header)
        response.encoding = response.apparent_encoding
        response.raise_for_status()

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(response.text)

        # 假设美元和加拿大元的汇率在特定类名下的元素中
        tr_list = soup.find_all('tr')  # 需要找到美元对应的实际标签

        rates = dict()

        for dollar in dollar_names:
            usd_tds = soup.find_all('td',text=dollar)
            if usd_tds:
                exchange_rate = float(usd_tds[0].next_sibling.next_sibling.string.replace(',', '').replace(' ', '')) / 100
                print(f"{dollar} exchange rate:", exchange_rate)
                rates[dollar]=round(exchange_rate,4)

        # return {'USD': usd_rate, 'CAD': cad_rate}
        return rates

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误：{e}")
        return None
    except AttributeError:
        print("无法从页面中提取汇率信息")
        return None

def connect_mysql(rates):
    # 连接mysql数据库
    conn = pymysql.connect(host='0.0.0.0', port=3306, user="root", password="123",charset="utf8", db='paycrm')

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 开启事务
    conn.begin()

    # exchange_rate  = 7.188
    # dollar = "美元"
    update_date = datetime.datetime.now().strftime("%Y-%m-%d")

    sql = "insert into dipay_exchangerate (currency_id,update_date,rate) values"

    count = 0
    for dollar, exchange_rate in rates.items():
        vals = f"((select id from dipay_currency where title='{dollar}' limit 1) ,'{update_date}',{exchange_rate})"
        count +=1
        if count == 1:
            sql += vals
        else:
            sql = sql + "," + vals

    # sql = "insert into dipay_exchangerate (currency_id,update_date,rate) values(2,'2024-01-30',{val} )".format(val=5.32)

    cursor.execute(sql)
    # fetchall      ( {"id":1,"age":10},{"id":2,"age":10}, )   ((1,10),(2,10))

    result = cursor.fetchall()

    print(result,'....',  type(result))

    conn.commit()

    cursor.close()
    conn.close()




# 获取并打印当日汇率
# rates = get_exchange_rates()
# if rates is not None:
#     for k,v in rates.items():
#         print(f"{k}汇率：{v}")

connect_mysql( get_exchange_rates())

