import requests
import os

GO_CQHTTP_HOST = os.getenv("GO_CQHTTP_HOST")
GO_CQHTTP_PORT = int(os.getenv("GO_CQHTTP_PORT"))

BASE_URL = "http://" + GO_CQHTTP_HOST + ":" + str(GO_CQHTTP_PORT)


# 发送私发消息
def send_message_to_user(user_id, message):
    url = BASE_URL + "/send_msg"
    params = {
        "user_id": user_id,
        "message": message
    }
    requests.get(url=url, params=params)


# 发送群聊消息
def send_message_to_group(group_id, message):
    url = BASE_URL + "/send_msg"
    params = {
        "group_id": group_id,
        "message": message
    }
    requests.get(url=url, params=params)
