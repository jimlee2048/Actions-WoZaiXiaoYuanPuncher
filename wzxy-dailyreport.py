# -*- encoding:utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import urllib
from urllib.parse import urlencode
import requests
import utils


# 需要新增参数'WZXY_location'和'WZXY_SCHOOL'(git新增参数需要在yml中也新增）


class WoZaiXiaoYuanPuncher(utils.Data):
    def __init__(self):
        super().__init__(city=os.environ["WZXY_CITY"], address_recommend=os.environ["ADDRESS_RECOMMEND"])
        # 打卡时段
        self.seq = None
        self.time = None
        # 打卡结果
        self.status_code = 0
        # 登陆接口
        self.loginUrl = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/username"
        # 请求头
        self.header = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d32) NetType/WIFI Language/zh_CN miniProgram",
            "Content-Type": "application/json;charset=UTF-8",
            "Content-Length": "212",
            "Host": "gw.wozaixiaoyuan.com",
            "Accept": "application/json, text/plain, */*",
            # 不加下面的参数会提示非法请求
            "Origin": "https://gw.wozaixiaoyuan.com",
            "X - Requested - With": "com.tencent.mm",
            "Sec - Fetch - Site": "same-origin",
            "Sec - Fetch - Mode": "cors",
            "Sec - Fetch - Dest": "empty",
            "Referer": f"https://gw.wozaixiaoyuan.com/h5/mobile/health/index/health/detail?id={os.environ['WZXY_SCHOOL']}",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",

        }
        # 请求体（必须有）
        self.body = "{}"
        self.session = None

    # 登录
    def login(self):
        username, password = str(os.environ["WZXY_USERNAME"]), str(
            os.environ["WZXY_PASSWORD"]
        )
        url = f"{self.loginUrl}?username={username}&password={password}"
        self.session = requests.session()
        # 登录
        response = self.session.post(url=url, data=self.body, headers=self.header)
        res = json.loads(response.text)
        if res["code"] == 0:
            print("使用账号信息登录成功")
            self.jwsession = response.headers["JWSESSION"]
            self.set_cache()
            return True
        else:
            print(res)
            print("登录失败，请检查账号信息")
            self.status_code = 5
            return False

    def PunchIn(self):
        print("获取打卡列表中...")
        url = "https://gw.wozaixiaoyuan.com/health/mobile/health/getBatch"
        self.header["Host"] = "gw.wozaixiaoyuan.com"
        self.header["JWSESSION"] = self.jwsession
        self.header["Cookie"] = f"JWSESSION={self.jwsession}"
        self.session = requests.session()
        response = self.session.post(url=url, data=self.body, headers=self.header)
        res = json.loads(response.text)
        # 如果 jwsession 无效，则重新 登录 + 打卡
        if res["code"] == 103:  # 101貌似是密码错误要重置
            print(res)
            print("jwsession 无效，将尝试使用账号信息重新登录")
            self.status_code = 4
            loginStatus = self.login()
            if loginStatus:
                self.PunchIn()
            else:
                print(res)
                print("重新登录失败，请检查账号信息")
        elif res["code"] == 0:
            # 标志时段是否有效
            inSeq = False
            # 遍历每个打卡时段（不同学校的打卡时段数量可能不一样）
            res_data = res["data"]
            daily_list = res_data["list"]
            for i in daily_list:
                # 判断时段是否有效
                if int(i["state"]) == 1:
                    inSeq = True
                    # 保存当前学校的打卡时段
                    self.time = f"{i['start']}-{i['end']}"
                    # 判断是否已经打卡
                    if int(i["type"]) == 0:
                        self.doPunchIn()
                    elif int(i["type"]) == 1:
                        self.status_code = 2
                        print("已经打过卡了")
            # 如果当前时间不在任何一个打卡时段内
            if not inSeq:
                self.status_code = 3
                print("打卡失败：不在打卡时间段内")

    # 执行打卡
    # 参数seq ： 当前打卡的序号
    def doPunchIn(self,):
        print("正在进行：" + self.getTime() + "...")
        url = f"https://gw.wozaixiaoyuan.com/health/mobile/health/save?batch={os.environ['WZXY_SCHOOL']}"
        self.header["Host"] = "gw.wozaixiaoyuan.com"
        self.header["Content-Type"] = "application/json;charset=UTF-8"
        self.header["JWSESSION"] = self.jwsession
        self.header["Cookie"] = f"JWSESSION={self.jwsession}; JWSESSION={self.jwsession}"
        cur_time = int(round(time.time() * 1000))
        sign_data = {
            "location": os.environ['WZXY_location'],
            "t1": "[\"无下列情况，健康状况正常\"]",
            "t2": "是",
            "type": 0,
            "locationMode": 0,
            "locationType": 0,
        }
        print(self.country,)
        self.session = requests.session()
        response = self.session.post(url=url, json=sign_data, headers=self.header)
        response = json.loads(response.text)

        # 打卡情况
        if response["code"] == 0:
            self.status_code = 1
            print("打卡成功")
        else:
            print(response)
            print("打卡失败")

    # 获取打卡时段 弃用
    def getSeq(self):
        seq = self.seq
        if seq == 1:
            return "早打卡"
        elif seq == 2:
            return "午打卡"
        elif seq == 3:
            return "晚打卡"
        else:
            return "非打卡时段"

    # 获取打卡时段
    def getTime(self):
        time = self.time

        return time

    # 获取打卡结果
    def getResult(self):
        res = self.status_code
        if res == 1:
            return "✅ 打卡成功"
        elif res == 2:
            return "✅ 你已经打过卡了，无需重复打卡"
        elif res == 3:
            return "❌ 打卡失败，当前不在打卡时间段内"
        elif res == 4:
            return "❌ 打卡失败，jwsession 无效"
        elif res == 5:
            return "❌ 打卡失败，登录错误，请检查账号信息"
        else:
            return "❌ 打卡失败，发生未知错误，请检查日志"

    # 推送打卡结果
    def sendNotification(self):
        notifyTime = utils.getCurrentTime()
        notifyResult = self.getResult()
        notifySeq = self.getTime()

        if os.environ.get("SCT_KEY"):
            # serverchan 推送
            notifyToken = os.environ["SCT_KEY"]
            url = "https://sctapi.ftqq.com/{}.send"
            body = {
                "title": "⏰ 我在校园打卡结果通知",
                "desp": "打卡项目：日检日报\n\n打卡情况：{}\n\n打卡时段：{}\n\n打卡时间：{}".format(
                    notifyResult, notifySeq, notifyTime
                ),
            }
            requests.post(url.format(notifyToken), data=body)
            print("消息已通过 Serverchan-Turbo 推送，请检查推送结果")
        if os.environ.get("PUSHPLUS_TOKEN"):
            # pushplus 推送
            url = "http://www.pushplus.plus/send"
            notifyToken = os.environ["PUSHPLUS_TOKEN"]
            content = json.dumps(
                {
                    "打卡项目": "日检日报",
                    "打卡情况": notifyResult,
                    "打卡时段": notifySeq,
                    "打卡时间": notifyTime,
                },
                ensure_ascii=False,
            )
            msg = {
                "token": notifyToken,
                "title": "⏰ 我在校园打卡结果通知",
                "content": content,
                "template": "json",
            }
            body = json.dumps(msg).encode(encoding="utf-8")
            headers = {"Content-Type": "application/json"}
            r = requests.post(url, data=body, headers=headers).json()
            if r["code"] == 200:
                print("消息经 pushplus 推送成功")
            else:
                print("pushplus: " + str(r["code"]) + ": " + str(r["msg"]))
                print("消息经 pushplus 推送失败，请检查错误信息")
        if os.environ.get("GOBOT_URL"):
            # go_cqhttp 推送
            GOBOT_URL = os.environ["GOBOT_URL"]
            GOBOT_TOKEN = os.environ["GOBOT_TOKEN"]
            GOBOT_QQ = os.environ["GOBOT_QQ"]
            url = f"{GOBOT_URL}?access_token={GOBOT_TOKEN}&{GOBOT_QQ}&message=⏰ 我在校园打卡结果通知\n---------\n\n打卡项目：健康打卡\n\n打卡情况：{notifyResult}\n\n打卡时间: {notifyTime}"
            r = requests.get(url).json()
            if r["status"] == "ok":
                print("消息经 go-cqhttp 推送成功！")
            else:
                print(
                    "go-cqhttp:"
                    + str(r["retcode"])
                    + ": "
                    + str(r["msg"])
                    + " "
                    + str(r["wording"])
                )
                print("消息经 go-cqhttp 推送失败，请检查错误信息")
        if os.environ.get("DD_BOT_ACCESS_TOKEN"):
            # 钉钉推送
            DD_BOT_ACCESS_TOKEN = os.environ["DD_BOT_ACCESS_TOKEN"]
            DD_BOT_SECRET = os.environ["DD_BOT_SECRET"]
            timestamp = str(round(time.time() * 1000))  # 时间戳
            secret_enc = DD_BOT_SECRET.encode("utf-8")
            string_to_sign = "{}\n{}".format(timestamp, DD_BOT_SECRET)
            string_to_sign_enc = string_to_sign.encode("utf-8")
            hmac_code = hmac.new(
                secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
            ).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
            print("开始使用 钉钉机器人 推送消息...", end="")
            url = f"https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_ACCESS_TOKEN}&timestamp={timestamp}&sign={sign}"
            headers = {"Content-Type": "application/json;charset=utf-8"}
            data = {
                "msgtype": "text",
                "text": {
                    "content": f"⏰ 我在校园打卡结果通知\n---------\n打卡项目：日检日报\n\n打卡情况：{notifyResult}\n\n打卡时间: {notifyTime}"
                },
            }
            r = requests.post(
                url=url, data=json.dumps(data), headers=headers, timeout=15
            ).json()
            if not r["errcode"]:
                print("消息经 钉钉机器人 推送成功！")
            else:
                print("dingding:" + str(r["errcode"]) + ": " + str(r["errmsg"]))
                print("消息经 钉钉机器人 推送失败，请检查错误信息")
        if os.environ.get("BARK_TOKEN"):
            # bark 推送
            notifyToken = os.environ["BARK_TOKEN"]
            req = "{}/{}/{}".format(notifyToken, "  ⏰ 我在校园打卡（日检日报）结果通知", notifyResult)
            requests.get(req)
            print("消息经bark推送成功")
        # 喵提醒
        if os.environ.get("MIAO_CODE"):
            baseurl = "https://miaotixing.com/trigger"
            body = {
                "id": os.environ["MIAO_CODE"],
                "text": "打卡项目：日检日报\n\n打卡情况：{}\n\n打卡时段：{}\n\n打卡时间：{}".format(
                    notifyResult, notifySeq, notifyTime
                ),
            }
            requests.post(baseurl, data=body)
            print("消息已通过 喵推送 进行通知，请检查推送结果")
        # telegram机器人
        if os.environ.get("TG-TOKEN"):
            token = os.environ["TG-TOKEN"]
            chat_id = os.environ["TG-CHATID"]
            text = "打卡项目：日检日报\n\n打卡情况：{}\n\n打卡时间：{}".format(notifyResult, notifyTime)
            tg_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
            results = requests.get(tg_url)
            print("消息已通过 Telegram-bot 进行通知，请检查推送结果")


if __name__ == "__main__":
    # 找不到cache，登录+打卡
    wzxy = WoZaiXiaoYuanPuncher()
    if not os.path.exists(".cache"):
        print("找不到cache文件，正在使用账号信息登录...")
        loginStatus = wzxy.login()
        if loginStatus:
            wzxy.PunchIn()
        else:
            print("登陆失败，请检查账号信息")
    else:
        print("找到cache文件，尝试使用jwsession打卡...")
        wzxy.PunchIn()
    wzxy.sendNotification()