import datetime
import json
import random
import time

import pytz


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
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, "rb") as file:
            data = json.load(file)
        file.close()
        return data

    def write(self, data):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        file.close()
