# 测试 通过python发微信

import json
import time
import requests

'''
本文件主要实现通过企业微信应用给企业成员发消息
'''

CORP_ID = "ww61dc7ac7d8f586a8"
SECRET = 'hMkfIfRaw8fun3iEFd71TEpAqWZF-WZdm-ciNcZf5tg'

class WeChatPub:
    s = requests.session()

    def __init__(self):
        self.token = self.get_token()
        print('token is:', self.token)

    def get_token(self):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={SECRET}"
        rep = self.s.get(url)
        if rep.status_code != 200:
            print("request failed.")
            return
        return json.loads(rep.content)['access_token']

    def send_msg(self, content):
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        form_data = {
            "touser": "WangYong",#接收人
            "toparty": "华悦远洋贸易北京有限公司",#接收部门
            "totag": "",#通讯录标签id
            "msgtype": "textcard",
            "agentid": 1000002,#应用ID
            "textcard": {
                "title": "到款提醒",
                "description": content,
                "url": "URL",
                "btntxt": "更多"
            },
            "safe": 0
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        if rep.status_code != 200:
            print("request failed.")
            return
        return json.loads(rep.content)

if __name__ == "__main__":
    wechat = WeChatPub()
    timenow = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    wechat.send_msg(f"<div class=\"gray\">{timenow}</div> <div class=\"normal\">注意！</div><div class=\"highlight\">今日有新债，坚持打新！</div>")
    print('消息已发送！')



