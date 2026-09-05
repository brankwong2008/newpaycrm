from celery import shared_task
from celery.utils.log import get_task_logger
import requests
from bs4 import BeautifulSoup
import datetime

from dipay.utils.ali_sms import send_sms

logger = get_task_logger(__name__)

# ===== 任务提醒短信模板配置 =====
# 当前模板 SMS_475870960 的 order 变量是"其他号码"类型（只接受字母数字下划线），
# 发不了中文任务内容。已在阿里云申请新模板（content 为文本变量），
# 新模板审核通过后：把 TEMPLATE_CODE 换成新码，并启用下方"新模板"的
# template_param 构造（把任务内容截断到20字符以内）即可。
REMIND_SMS_SIGN_NAME = '文安县金凯建材有限公司'
REMIND_SMS_TEMPLATE_CODE = 'SMS_512420339'


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


@shared_task
def send_dailyplan_remind_sms():
    """
    每天定时执行：找出提醒日期已到、且尚未发过提醒短信的任务，
    给任务所有人(user)发送短信，然后把状态从'提醒'改为'进行'。
    由 celery beat 每天调度，不依赖任何用户打开页面。
    """
    from dipay.models import DailyPlan

    # 导入放在函数内，避免 celery worker 启动时的循环导入问题
    from paycrm import secret

    today = datetime.date.today()

    # 提醒日期已到 + 未发过短信 + 任务未完成
    # 注意：这里不按 status=2(提醒) 过滤，因为用户在 beat 执行前打开页面
    # 也可能已把状态改成'进行'，按 is_sms_sent 过滤才能保证短信不漏发
    todo_list = DailyPlan.objects.filter(
        remind_date__lte=today,
        is_sms_sent=False,
    ).exclude(status=1)

    sent_count, skipped_count = 0, 0
    for item in todo_list:
        phone = item.user.phone if item.user else None
        if not phone:
            logger.warning("任务[%s]的所有人[%s]没有手机号，跳过短信提醒", item.pk, item.user)
            skipped_count += 1
            item.is_sms_sent = True
            if item.status == 2:
                item.status = 0
            item.save()
            continue

        try:
            # content 为文本变量，支持中文任务内容；阿里云文本变量单值上限 20 字符
            body = send_sms(
                sign_name=REMIND_SMS_SIGN_NAME,
                template_code=REMIND_SMS_TEMPLATE_CODE,
                phone_numbers=phone,
                template_param='{"time":"%s", "content":"%s"}' % (
                    item.remind_date.strftime('%Y-%m-%d'), item.content[:20])
            )
            # 阿里云即使发送失败也返回 HTTP 200，必须检查响应体的 Code 字段
            if body and getattr(body, 'code', None) == 'OK':
                logger.info("任务[%s]提醒短信已发送给 %s (BizId: %s)", item.pk, phone, body.biz_id)
            else:
                # 业务失败（签名/模板/参数/频率等），记录详细错误码便于排查
                logger.error("任务[%s]短信被阿里云拒绝: %s %s", item.pk,
                             getattr(body, 'code', None), getattr(body, 'message', None))
        except Exception as e:
            # 网络/鉴权级别异常
            logger.error("任务[%s]短信发送失败: %s", item.pk, e)

        # 无论成功还是失败都标记为已发，避免失败任务每次运行都重试轰炸用户；
        # 如果希望失败后次日重试，把 item.is_sms_sent = True 移到 code=='OK' 分支内即可
        sent_count += 1
        item.is_sms_sent = True
        # 提醒日期到了，状态同步从'提醒'改为'进行'，与页面里的逻辑保持一致
        if item.status == 2:
            item.status = 0
        item.save()

    logger.info("提醒短信任务完成: 发送%s条, 跳过%s条", sent_count, skipped_count)
    return {'sent': sent_count, 'skipped': skipped_count}
