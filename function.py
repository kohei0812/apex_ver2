import os
import pandas as pd
import requests
from requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup
import time
from collections import OrderedDict
from tkinter.messagebox import showinfo


def scrape(url, start, end):
    session = requests.Session()
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
    # rank_list = [rank.text.strip() for rank in soup.find_all(class_='rank')]

    # rankクラス内のspan要素が34〜66までのものを抽出
    rank_elements = soup.select('.rank span')[start:end]
    # rank要素のテキストを取得
    rank_list = [rank.text.strip() for rank in rank_elements]

    # usernameクラスのテキストを取得してリストに追加
    # username_list = [username.text.strip() for username in soup.find_all(class_='username')]

    # 同じ<tr>内のusernameクラスの要素を抽出
    username_elements = soup.select('.username')[start:end]
    # username要素のテキストを取得
    username_list = [username.text.strip() for username in username_elements]

    # userのプロフィールページURLリスト化
    base_url = "https://apex.tracker.gg"
    account_list = []
    for username_element in username_elements:
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
        time.sleep(3)

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


def send_line_message(token, message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    payload = {"message": message}
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code


def verify(page,start,end):
    # LINE Notifyのトークンをここに設定
    line_token = "tVpuB4sNAMQlYTE9giCfCQSmzrkb8cO54sIcGrGQyfL"
    # ディレクトリのパスを指定して関数を呼び出し
    directory_path = 'data'
    result_list = read_and_concat_csv(directory_path)

    jpn_lists = [new_list[2] for new_list in result_list if new_list[3] == "J"]

    if page:
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
        start += 1
        end += 1
        message = f"{start}-{end}位: \n{result_str}"

        # LINEにメッセージを送信
        status_code = send_line_message(line_token, message)

        if status_code == 200:
            print("メッセージが送信されました。")
        else:
            print("メッセージの送信に失敗しました。ステータスコード: {}".format(status_code))
    else:
        print("スクレイピングでエラーが発生したため、結果を取得できませんでした。")
        message = "スクレイピングでエラーが発生したため、結果を取得できませんでした。"

        # LINEにメッセージを送信
        status_code = send_line_message(line_token, message)

        if status_code == 200:
            print("メッセージが送信されました。")
        else:
            print("メッセージの送信に失敗しました。ステータスコード: {}".format(status_code))

    showinfo('処理は完了しました。')
