import utils
import chat_gpt
import os
import redis
import pickle
import music

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))


redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


# 聊天模式参数
chat_user_list = {}
# 开启/关闭与ChatGPT对话
chat_mode = False


# 初始化聊天模式
def init_chat(report):

    system_tips = str(open("files/system_tips.txt", "r", encoding="utf-8").read().strip())
    messages = [
        {
            "role": "system",
            "content": system_tips
        }
    ]
    redis_cli.set(report["user_id"], pickle.dumps(messages))


# 开始聊天
def start_chat(report):
    message_type = report["message_type"]
    user = report["user_id"]
    chat_user_list[user] = True
    # 私发消息
    if message_type == "private":
        user_id = report["user_id"]
        utils.send_message_to_user(user_id=user_id, message="嗨～主人，我在呢!")
    # 群聊消息
    if message_type == "group":
        user_id = report["user_id"]
        group_id = report["group_id"]
        utils.send_message_to_group(group_id=group_id, message="嗨～主人，我在呢!" + " [CQ:at,qq=" + str(user_id) + "]")
    return "OK"


# 结束聊天
def finish_chat(report):
    message_type = report["message_type"]
    # 私发消息
    if message_type == "private":
        user_id = report["user_id"]
        utils.send_message_to_user(user_id=user_id, message="主人再见～喵～")
        # 群聊消息
    if message_type == "group":
        user_id = report["user_id"]
        group_id = report["group_id"]
        utils.send_message_to_group(group_id=group_id, message="主人再见～喵～" + " [CQ:at,qq=" + str(user_id) + "]")
    return "OK"


# 查询余额
def get_grants(report):
    message_type = report["message_type"]
    grants_obj = chat_gpt.get_credit_grants()
    # 私发消息
    if message_type == "private":
        user_id = report["user_id"]
        utils.send_message_to_user(user_id=user_id, message="当前密钥额度还剩" + grants_obj["total_available"] + "$哦～")
        # 群聊消息
    if message_type == "group":
        group_id = report["group_id"]
        utils.send_message_to_group(group_id=group_id, message="当前密钥额度还剩" + grants_obj["total_available"] + "$哦～")
    return "OK"


# 使用帮助
def get_help(report):
    message_type = report["message_type"]
    help_text = "唤醒neko的关键字：\n1、/neko -- 开始与neko对话\n2、/bye -- 结束与neko对话\n3、/余额 -- 查看当前密钥余额\n4、/点歌 [歌曲名] -- 搜索歌曲\n5、/画画 [描述] -- 画一幅画\n6、/帮助 -- 查看使用说明"
    # 私发消息
    if message_type == "private":
        user_id = report["user_id"]
        utils.send_message_to_user(user_id=user_id, message=help_text)
        # 群聊消息
    if message_type == "group":
        group_id = report["group_id"]
        utils.send_message_to_group(group_id=group_id, message=help_text)
    return "OK"


# 歌名点歌
def get_song(report, song):
    message_type = report["message_type"]
    play_url = music.search_song(song=song)
    if play_url is not None:
        # 私发消息
        if message_type == "private":
            user_id = report["user_id"]
            utils.send_message_to_user(user_id=user_id, message="[CQ:record,file=" + play_url + "]")
            # 群聊消息
        if message_type == "group":
            group_id = report["group_id"]
            utils.send_message_to_group(group_id=group_id, message="[CQ:record,file=" + play_url + "]")
        return "OK"
    else:
        # 私发消息
        if message_type == "private":
            user_id = report["user_id"]
            utils.send_message_to_user(user_id=user_id, message="抱歉主人～neko找不到这首歌哦～")
            # 群聊消息
        if message_type == "group":
            group_id = report["group_id"]
            user_id = report["user_id"]
            utils.send_message_to_group(group_id=group_id, message="抱歉主人～neko找不到这首歌哦～" + " [CQ:at,qq=" + str(user_id) + "]")
        return "OK"


# 绘图
def get_picture(report, prompt):
    message_type = report["message_type"]
    image_url = chat_gpt.draw(prompt=prompt)

    if image_url is not None:
        # 私发消息
        if message_type == "private":
            user_id = report["user_id"]
            utils.send_message_to_user(user_id=user_id, message="[CQ:image,file=" + image_url + "]")
            # 群聊消息
        if message_type == "group":
            group_id = report["group_id"]
            utils.send_message_to_group(group_id=group_id, message="[CQ:image,file=" + image_url + "]")
        return "OK"
    else:
        # 私发消息
        if message_type == "private":
            user_id = report["user_id"]
            utils.send_message_to_user(user_id=user_id, message="抱歉主人～neko画不出来喵～")
            # 群聊消息
        if message_type == "group":
            group_id = report["group_id"]
            user_id = report["user_id"]
            utils.send_message_to_group(group_id=group_id, message="抱歉主人～neko画不出来喵～" + " [CQ:at,qq=" + str(user_id) + "]")
        return "OK"

