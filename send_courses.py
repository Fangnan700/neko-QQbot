import json
import time
import datetime
import utils
import requests
import os

courses_file = open("files/courses.json", "r")
courses_data = json.load(courses_file)
love_qqnum = "3200649365"
test_qqnum = "2621737589"


def schedule_send():
    while True:
        time_tamp = time.time()
        struct_time = time.localtime(time_tamp)

        time_str = time.strftime("%H:%M:%S", struct_time)

        if time_str == "07:00:00":
            # 获取今天日期
            today = datetime.date.today()
            weekday_num = today.weekday()
            if weekday_num == 0:
                weekday = "星期一"
            elif weekday_num == 1:
                weekday = "星期二"
            elif weekday_num == 2:
                weekday = "星期三"
            elif weekday_num == 3:
                weekday = "星期四"
            elif weekday_num == 4:
                weekday = "星期五"
            elif weekday_num == 5:
                weekday = "星期六"
            else:
                weekday = "星期天"

            # 获取今天天气
            weather_data = get_weather()
            city = weather_data["city"]
            weather = weather_data["future"][0]["weather"]
            temperature = weather_data["future"][0]["temperature"]
            wind_direct = weather_data["future"][0]["direct"]

            # 读取今天课程
            courses_text = ""
            courses = courses_data["name"][weekday]
            if len(courses) > 0:
                courses_text = "主人今天记得上课哦，neko为您准备的课表在这喵～"
                for index, course in courses.items():
                    courses_text = courses_text + "\n\n序号：" + str(index) + "\n课程：" + course["课程"] + "\n时间：" + course["时间"] + "\n地点：" + course["地点"]
            else:
                courses_text = "主人今天没有课哦～"

            messages = '''
                嗨～，主人早上好～
                今天是：{}，{}
                neko带来的天气预报如下～
                城市：{}
                天气：{}
                气温：{}
                风向：{}
                祝您有美好的一天喵～
            '''.format(str(today), str(weekday), city, weather, temperature, wind_direct)

            messages = '\n'.join([line.strip() for line in messages.strip().split('\n')])

            utils.send_message_to_user(user_id=love_qqnum, message=messages)
            utils.send_message_to_user(user_id=test_qqnum, message=messages)
            time.sleep(1)
            utils.send_message_to_user(user_id=love_qqnum, message=courses_text)
            utils.send_message_to_user(user_id=test_qqnum, message=courses_text)

        time.sleep(1)


def get_weather():
    key = os.getenv("JUHEAPI_KEY")
    base_url = "http://apis.juhe.cn/simpleWeather/query"
    city = "合肥"

    response = requests.get(url=base_url + "?city=" + city + "&key=" + key)

    return response.json()["result"]
