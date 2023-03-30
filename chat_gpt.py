import utils
import requests
import json
import demjson
import redis
import pickle
import os

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

def chat(report):
    redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    message_type = report["message_type"]
    raw_message = report["raw_message"]
    user_id = report["user_id"]

    messages = pickle.loads(redis_cli.get(user_id))

    messages.append({
        "role": "user",
        "content": raw_message
    })

    try:
        if len(messages) > 10:
            del messages[1: 2]

        gpt_answer = get_openai_response(messages)
        messages.append({
            "role": "assistant",
            "content": gpt_answer
        })
        redis_cli.set(user_id, pickle.dumps(messages))

    except Exception as ex:
        gpt_answer = "null"

    # 私发消息
    if message_type == "private":

        utils.send_message_to_user(user_id=user_id, message=gpt_answer)

    # 群聊消息
    if message_type == "group":
        group_id = report["group_id"]
        utils.send_message_to_group(group_id=group_id, message=gpt_answer + " [CQ:at,qq=" + str(user_id) + "]")


# 获取OpenAI回答
def get_openai_response(messages):
    key = os.getenv("OPENAI_KEY")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "model": "gpt-3.5-turbo",
        "n": 1,
        "stream": True,
        "messages": messages
    })

    response = requests.post(url=url, headers=headers, data=data)
    resp_data = response.content.decode("utf-8").split("\n")

    resp_content = ""

    for resp in resp_data:
        if resp == "data: [DONE]":
            break
        if resp != "":
            try:
                resp_content += demjson.decode("{" + resp + "}")["data"]["choices"][0]["delta"]["content"]
            except Exception:
                pass

    return resp_content


# 查询试用余额
def get_credit_grants():
    key = os.getenv("OPENAI_KEY")
    url = 'https://api.openai.com/dashboard/billing/credit_grants'
    headers = {
        'authorization': 'Bearer ' + key,
        'origin': 'https://platform.openai.com',
        'referer': 'https://platform.openai.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
    }
    response = requests.get(url=url, headers=headers)
    data_obj = json.loads(response.content.decode('utf-8'))

    data = {
        'key': key,
        'total_granted': '{:.2f}'.format(float(data_obj['total_granted'])),
        'total_used': '{:.3f}'.format(float(data_obj['total_used'])),
        'total_available': '{:.3f}'.format(float(data_obj['total_available']))
    }
    return data


# 绘图
def draw(prompt):
    key = os.getenv("OPENAI_KEY")
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        'authorization': 'Bearer ' + key,
        'content-type': 'application/json',
        'origin': 'https://platform.openai.com',
        'referer': 'https://platform.openai.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
    }

    data = {
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }

    resp = requests.post(url=url, headers=headers, data=json.dumps(data))

    return resp.json()["data"][0]["url"]

