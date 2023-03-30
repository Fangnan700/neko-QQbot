import os
import redis
import mode
import chat_gpt
import threading
import send_courses
from flask import *
from dotenv import load_dotenv

load_dotenv(".env")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

app = Flask(__name__)
chat_user_list = []

redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


@app.route("/", methods=["POST"])
def get_report():
    report = request.get_json()

    # 消息
    if report["post_type"] == "message":

        raw_message = report["raw_message"]

        # 使用帮助
        if raw_message[:4] == "/帮助":
            mode.get_help(report=report)
            return "OK"

        # 查询余额
        if raw_message[:3] == "/余额":
            mode.get_grants(report=report)
            return "OK"

        # 歌名点歌
        if raw_message[:3] == "/点歌":
            song = str(raw_message).split()[1]
            mode.get_song(report=report, song=song)

        # 绘图
        if raw_message[:3] == "/画画":
            prompt = str(raw_message).split()[1]
            mode.get_picture(report=report, prompt=prompt)

        # 聊天模式
        if raw_message[:4] == "/bye":
            if redis_cli.exists(report["user_id"]):
                redis_cli.delete(report["user_id"])
            mode.finish_chat(report=report)
            return "OK"

        if redis_cli.exists(report["user_id"]):
            chat_thread = threading.Thread(target=chat_gpt.chat, args=(report,))
            chat_thread.start()
            return "OK"

        if raw_message[:5] == "/neko":
            if not redis_cli.exists(report["user_id"]):
                mode.init_chat(report=report)
            mode.start_chat(report=report)
            return "OK"

    return "OK"


# 定时任务
# _thread = threading.Thread(target=send_courses.schedule_send)
# _thread.start()


if __name__ == '__main__':
    app.run()
