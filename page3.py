from collections import OrderedDict
from tkinter.messagebox import showinfo

import function as func

# ディレクトリのパスを指定して関数を呼び出し
directory_path = 'data'
result_list = func.read_and_concat_csv(directory_path)

jpn_lists = [new_list[2] for new_list in result_list if new_list[3] == "J"]

# LINE Notifyのトークンをここに設定
line_token = "tVpuB4sNAMQlYTE9giCfCQSmzrkb8cO54sIcGrGQyfL"

page = func.scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=3&legend=all")

if page :
    total_list = page
    now_lists = [list(item) for item in zip(*total_list)]

    now_jpn_list = []
    for now_list in now_lists:
        for jpn_list in jpn_lists:
            if now_list[2] == jpn_list:
                now_jpn_list.append(now_list)

    # 各リストの要素をタプルに変換
    result = list(OrderedDict.fromkeys(map(tuple, now_jpn_list)))
    result = [list(item) for item in result]

    for array in result:
        array[0] += "位"
        del array[1]

    result_str = '\n'.join([' '.join(map(str, tpl)) for tpl in result])
    # メッセージの内容を設定
    message = "201-300位:\n {}".format(result_str)

    # LINEにメッセージを送信
    status_code = func.send_line_message(line_token, message)

    if status_code == 200:
        print("メッセージが送信されました。")
    else:
        print("メッセージの送信に失敗しました。ステータスコード: {}".format(status_code))
else:
    print("スクレイピングでエラーが発生したため、結果を取得できませんでした。")
    message = "スクレイピングでエラーが発生したため、結果を取得できませんでした。"

    # LINEにメッセージを送信
    status_code = func.send_line_message(line_token, message)

    if status_code == 200:
        print("メッセージが送信されました。")
    else:
        print("メッセージの送信に失敗しました。ステータスコード: {}".format(status_code))

showinfo('処理は完了しました。')
