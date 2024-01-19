import os
import pandas as pd
from collections import OrderedDict
import requests
from requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup
import time

session = requests.Session()


def scrape(url):
    try:
        # ページの取得
        response = session.get(url, timeout=10)
        response.raise_for_status()  # HTTPエラーレスポンスがあれば例外を発生
    except Timeout:
        print("リクエストがタイムアウトしました。")
        return None
    except RequestException as e:
        print(f"リクエスト中にエラーが発生しました: {e}")
        return None

    # 取得したページのHTMLを解析
    soup = BeautifulSoup(response.text, "html.parser")
    # rankクラスのテキストを取得してリストに追加
    rank_list = [rank.text.strip() for rank in soup.find_all(class_='rank')]
    # usernameクラスのテキストを取得してリストに追加
    username_list = [username.text.strip() for username in soup.find_all(class_='username')]

    # userのプロフィールページURLリスト化
    base_url = "https://apex.tracker.gg"
    account_list = []
    for username_element in soup.find_all(class_='username'):
        path = username_element.find('a')['href']
        full_url = base_url + path

        try:
            # ページの取得
            response = session.get(full_url, timeout=10)
            response.raise_for_status()  # HTTPエラーレスポンスがあれば例外を発生
        except Timeout:
            print("リクエストがタイムアウトしました。")
            return None
        except RequestException as e:
            print(f"リクエスト中にエラーが発生しました: {e}")
            return None

        sub_soup = BeautifulSoup(response.text, "html.parser")
        account_elements = sub_soup.find_all(class_='ph-details__identifier')
        # すべての要素のテキストをリストに追加
        for account_element in account_elements:
            account_list.append(account_element.text.strip())
        time.sleep(5)

    return rank_list, username_list, account_list


def read_and_concat_csv(directory_path):
    # 指定されたディレクトリ内のCSVファイル一覧を取得
    csv_files = [file for file in os.listdir(directory_path) if file.endswith('.csv')]

    # CSVファイルを読み込んでデータフレームに格納し、リストに追加
    dataframes = []
    for csv_file in csv_files:
        file_path = os.path.join(directory_path, csv_file)
        # ヘッダーをスキップして読み込む
        df = pd.read_csv(file_path, header=None)
        dataframes.append(df)

    # データフレームを結合
    combined_df = pd.concat(dataframes, ignore_index=True)

    # 結合したデータフレームをリストに変換
    combined_list = combined_df.values.tolist()

    return combined_list


# ディレクトリのパスを指定して関数を呼び出し
directory_path = 'data'
result_list = read_and_concat_csv(directory_path)

jpn_lists = [new_list[2] for new_list in result_list if new_list[3] == "J"]

page1 = scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=1&legend=all")
page2 = scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=2&legend=all")
page3 = scrape("https://apex.tracker.gg/apex/leaderboards/stats/all/RankScore?page=3&legend=all")

if page1 and page2 and page3:
    total_list = [
        list(page1[0]) + list(page2[0] + page3[0]),
        list(page1[1]) + list(page2[1] + page3[1]),
        list(page1[2]) + list(page2[2] + page3[2])
    ]

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

    def send_line_message(token, message):
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": "Bearer " + token}
        payload = {"message": message}
        response = requests.post(url, headers=headers, data=payload)
        return response.status_code

    # LINE Notifyのトークンをここに設定
    line_token = "tVpuB4sNAMQlYTE9giCfCQSmzrkb8cO54sIcGrGQyfL"

    # メッセージの内容を設定
    message = "結果: {}".format(result_str)

    # LINEにメッセージを送信
    status_code = send_line_message(line_token, message)

    if status_code == 200:
        print("メッセージが送信されました。")
    else:
        print("メッセージの送信に失敗しました。ステータスコード: {}".format(status_code))
else:
    print("スクレイピングでエラーが発生したため、結果を取得できませんでした。")
