from celery import shared_task
import requests
from bs4 import BeautifulSoup
import datetime


@shared_task
def get_exchange_rate(dollar):
    data = {}
    url2 = 'https://www.boc.cn/sourcedb/whpj/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'
    }
    dated_response = requests.get(url=url2, data=data, headers=headers)
    dated_response.encoding = dated_response.apparent_encoding

    # 实例化soup对象
    soup = BeautifulSoup(dated_response.text, 'lxml')

    # 1.  获取实时表格里面的数据，.BOC_main有两个表，只有第二个是我们需要的
    table = soup.select('.BOC_main .publish table')[1]
    rows = table.find_all("tr")
    # print(rows,len(rows))
    rate = 0
    update_time = datetime.datetime.now()
    for row in rows[1:]:
        tds = row.find_all("td")
        if len(tds) < 7:
            break
        if tds[0].text == dollar:
            rate = float(tds[1].text) / 100
            break

    print(dollar, update_time, rate)

    return dollar, rate
