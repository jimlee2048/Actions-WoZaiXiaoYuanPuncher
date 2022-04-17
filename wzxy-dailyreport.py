# -*- encoding:utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import urllib
import urllib.parse
from urllib.parse import urlencode

import requests

import utils


class WoZaiXiaoYuanPuncher:
    def __init__(self):
        # JWSESSION
        self.jwsession = None
        # 打卡时段
        self.seq = None
        # 打卡结果
        self.status_code = 0
        # 登陆接口
        self.loginUrl = "https://gw.wozaixiaoyuan.com/basicinfo/mobile/login/username"
        # 请求头
        self.header = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.13(0x18000d32) NetType/WIFI Language/zh_CN miniProgram",
            "Content-Type": "application/json;charset=UTF-8",
            "Content-Length": "2",
            "Host": "gw.wozaixiaoyuan.com",
            "Accept-Language": "en-us,en",
            "Accept": "application/json, text/plain, */*",
        }
        # 请求体（必须有）
        self.body = "{}"

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
            jwsession = response.headers["JWSESSION"]
            self.setJwsession(jwsession)
            return True
        else:
            print(res)
            print("登录失败，请检查账号信息")
            self.status_code = 5
            return False

    # 设置JWSESSION
    def setJwsession(self, jwsession):
        # 如果找不到cache,新建cache储存目录与文件
        if not os.path.exists(".cache"):
            print("正在创建cache储存目录与文件...")
            os.mkdir(".cache")
            data = {"jwsession": jwsession}
        elif not os.path.exists(".cache/cache.json"):
            print("正在创建cache文件...")
            data = {"jwsession": jwsession}
        # 如果找到cache,读取cache并更新jwsession
        else:
            print("找到cache文件，正在更新cache中的jwsession...")
            data = utils.processJson(".cache/cache.json").read()
            data["jwsession"] = jwsession
        utils.processJson(".cache/cache.json").write(data)
        self.jwsession = data["jwsession"]

    # 获取JWSESSION
    def getJwsession(self):
        if not self.jwsession:  # 读取cache中的配置文件
            data = utils.processJson(".cache/cache.json").read()
            self.jwsession = data["jwsession"]
        return self.jwsession

    # 获取打卡列表，判断当前打卡时间段与打卡情况，符合条件则自动进行打卡
    def PunchIn(self):
        print("获取打卡列表中...")
        url = "https://student.wozaixiaoyuan.com/heat/getTodayHeatList.json"
        self.header["Host"] = "student.wozaixiaoyuan.com"
        self.header["JWSESSION"] = self.getJwsession()
        self.session = requests.session()
        response = self.session.post(url=url, data=self.body, headers=self.header)
        res = json.loads(response.text)
        # 如果 jwsession 无效，则重新 登录 + 打卡
        if res["code"] == -10:
            print("jwsession 无效，将尝试使用账号信息重新登录")
            self.status_code = 4
            loginStatus = self.login()
            if loginStatus:
                self.PunchIn()
            else:
                print("重新登录失败，请检查账号信息")
        elif res["code"] == 0:
            # 标志时段是否有效
            inSeq = False
            # 遍历每个打卡时段（不同学校的打卡时段数量可能不一样）
            for i in res["data"]:
                # 判断时段是否有效
                if int(i["state"]) == 1:
                    inSeq = True
                    # 保存当前学校的打卡时段
                    self.seq = int(i["seq"])
                    # 判断是否已经打卡
                    if int(i["type"]) == 0:
                        self.doPunchIn(str(i["seq"]))
                    elif int(i["type"]) == 1:
                        self.status_code = 2
                        print("已经打过卡了")
            # 如果当前时间不在任何一个打卡时段内
            if inSeq == False:
                self.status_code = 3
                print("打卡失败：不在打卡时间段内")

    # 执行打卡
    # 参数seq ： 当前打卡的序号
    def doPunchIn(self, seq):
        print("正在进行：" + self.getSeq() + "...")
        url = "https://student.wozaixiaoyuan.com/heat/save.json"
        self.header["Host"] = "student.wozaixiaoyuan.com"
        self.header["Content-Type"] = "application/x-www-form-urlencoded"
        self.header["JWSESSION"] = self.getJwsession()
        cur_time = int(round(time.time() * 1000))
        sign_data = {
            "answers": '["0"]',
            "seq": str(seq),
            "temperature": utils.getRandomTemperature(os.environ["WZXY_TEMPERATURE"]),
            "latitude": os.environ["WZXY_LATITUDE"],
            "longitude": os.environ["WZXY_LONGITUDE"],
            "country": os.environ["WZXY_COUNTRY"],
            "city": os.environ["WZXY_CITY"],
            "district": os.environ["WZXY_DISTRICT"],
            "province": os.environ["WZXY_PROVINCE"],
            "township": os.environ["WZXY_TOWNSHIP"],
            "street": os.environ["WZXY_STREET"],
            "myArea": "",
            "areacode": "",
            "userId": "",
            "city_code": os.environ["WZXY_CITY_CODE"],
            "timestampHeader": cur_time,
            "signature": hashlib.sha256(
                f"{os.environ['WZXY_PROVINCE']}_{cur_time}_{os.environ['WZXY_CITY']}".encode(
                    "utf-8"
                )
            ).hexdigest(),
        }
        data = urlencode(sign_data)
        self.session = requests.session()
        response = self.session.post(url=url, data=data, headers=self.header)
        response = json.loads(response.text)
        # 打卡情况
        if response["code"] == 0:
            self.status_code = 1
            print("打卡成功")
        else:
            print(response)
            print("打卡失败")

    # 获取打卡时段
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
        notifySeq = self.getSeq()

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
            print("消息经Serverchan-Turbo推送成功")
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
            requests.post(url, data=msg)
            print("消息经pushplus推送成功")
        if os.environ.get("DD_BOT_ACCESS_TOKEN"):
            body=json.dumps(msg).encode(encoding='utf-8')
            headers = {'Content-Type':'application/json'}
            r = requests.post(url, data=body, headers=headers).json()
            if r["code"] == 200:
                print("消息经 pushplus 推送成功")
            else:
                print("pushplus: " + r['code'] + ": " + r['msg'])
                print("消息经 pushplus 推送失败，请检查错误信息")
        if os.environ.get('GOBOT_URL'):
            # go_cqhttp 推送
            GOBOT_URL = os.environ["GOBOT_URL"]
            GOBOT_TOKEN = os.environ["GOBOT_TOKEN"]
            GOBOT_QQ = os.environ["GOBOT_QQ"]
            url = f'{GOBOT_URL}?access_token={GOBOT_TOKEN}&{GOBOT_QQ}&message=⏰ 我在校园打卡结果通知\n---------\n\n打卡项目：健康打卡\n\n打卡情况：{notifyResult}\n\n打卡时间: {notifyTime}'
            r = requests.get(url).json()
            if r["status"] == "ok":
                print("消息经 go-cqhttp 推送成功！")
            else:
                print("go-cqhttp:" + r['retcode'] + ": " + r['msg'] + " " + r['wording'])
                print("消息经 go-cqhttp 推送失败，请检查错误信息")
        if os.environ.get('DD_BOT_ACCESS_TOKEN'):
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
            response = requests.post(
                url=url, data=json.dumps(data), headers=headers, timeout=15
            ).json()
            if not response["errcode"]:
                print("消息经钉钉机器人推送成功！")
            r = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=15).json()
            if not r['errcode']:
                print('消息经 钉钉机器人 推送成功！')
            else:
                print("消息经钉钉机器人推送失败！")
        if os.environ.get("BARK_TOKEN"):
                print("dingding:" + r['errcode'] + ": " + r['errmsg'])
                print('消息经 钉钉机器人 推送失败，请检查错误信息')
        if os.environ.get('BARK_TOKEN'):
            # bark 推送
            notifyToken = os.environ["BARK_TOKEN"]
            req = "{}/{}/{}".format(notifyToken, "⏰ 我在校园打卡（日检日报）结果通知", notifyResult)
            requests.get(req)
            print("消息经bark推送成功")
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
