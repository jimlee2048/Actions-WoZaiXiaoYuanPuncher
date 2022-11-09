import datetime
import json
import os
import random
import time
from urllib import parse

import jsonpickle
import pytz
import requests


# 获取当前时间(云函数的运行环境是 0 时区时间，需要 +8 转化为北京时间）
def getCurrentTime():
    return datetime.datetime.now(pytz.timezone("Asia/Shanghai")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# 获取当前小时
def getCurrentHour():
    return datetime.datetime.now(pytz.timezone("Asia/Shanghai")).hour


# 获取随机温度
def getRandomTemperature(self, temperature="36.0~36.5"):
    if temperature.find("~") == -1:
        return str(float(temperature))
    else:
        scope = temperature.split("~")
        random.seed(time.ctime())
        return "{:.1f}".format(random.uniform(float(scope[0]), float(scope[1])))


# 读写 json 文件
class processJson:
    def __init__(self, path, address):
        self.path = path
        self.location = None
        self.address_component = None
        self.address_reference = None
        self.ad_info = None
        self.formatted_addresses = None
        self.jwsession = None
        self.address = address
        self.address_recommend = None

    def read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
                file.close()
                return data
        except FileNotFoundError:
            make_cache = getattr(self, 'set_cache')
            make_cache()
        except json.decoder.JSONDecodeError:
            make_cache = getattr(self, 'set_cache')
            make_cache()
        data = self.read()
        return data

    def write(self):
        with open(self.path, "w", encoding="utf-8") as file:
            self.json_request(self.address)
            file.write(jsonpickle.encode(self.__dict__, indent=4))
        file.close()

    def json_request(self, address):
        url = 'https://apis.map.qq.com/ws/geocoder/v1/?address=' + parse.quote(
            address) + '&key=A3YBZ-NC5RU-MFYVV-BOHND-RO3OT-ABFCR'
        jr = json.loads(requests.get(url).text)['result']['location']
        url = 'https://apis.map.qq.com/ws/geocoder/v1/?key=A3YBZ-NC5RU-MFYVV-BOHND-RO3OT-ABFCR&location=' + str(
            jr['lat']) + ',' + str(jr['lng'])
        jr = json.loads(requests.get(url).text)['result']
        self.location = jr['location']
        self.address_component = jr['address_component']
        self.address_reference = jr['address_reference']
        self.ad_info = jr['ad_info']
        self.formatted_addresses = jr['formatted_addresses']
        return jr


class Data(processJson):
    def __init__(self, city, address_recommend):
        super().__init__(".cache/cache.json", city + address_recommend)
        jr = self.read()
        if 'jwsession' in jr:
            self.jwsession = jr['jwsession']
        if not jr['formatted_addresses']['recommend'] or jr['formatted_addresses']['recommend'] != address_recommend:
            jr = self.json_request(city + address_recommend)
            self.address_recommend = jr['formatted_addresses']['recommend']
            self.set_cache()
        self.address_recommend = jr['formatted_addresses']['recommend']
        self.latitude = str(jr['location']['lat'])
        self.longitude = str(jr['location']['lng'])
        self.country = jr['address_component']['nation']
        self.city = jr['address_component']['city']
        self.district = jr['address_component']['district']
        self.province = jr['address_component']['province']
        self.township = jr['address_reference']['town']['title']
        self.towncode = jr['address_reference']['town']['id']
        self.adcode = jr['ad_info']['adcode']
        self.street = jr['address_reference']['street']['title']
        self.areacode = (self.adcode, self.towncode)["北京市" == self.province]
        self.citycode = jr['ad_info']['city_code']

    def set_cache(self):
        # 如果找不到cache,新建cache储存目录与文件
        if not os.path.exists(".cache"):
            print("正在创建cache储存目录与文件...")
            os.mkdir(".cache")
        elif not os.path.exists(".cache/cache.json"):
            print("正在创建cache文件...")
        # 如果找到cache,读取cache并更新
        else:
            print("找到cache文件，正在更新cache...")
        self.write()