import requests


def search_song(song):
    url = f"https://v.api.aa1.cn/api/kugou/?msg={song}&type=1"

    resp = requests.get(url=url).json()
    play_url = resp["PlayLink"]
    if play_url != "":
        return play_url
    else:
        return None
