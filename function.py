import os
import pandas as pd
import requests
from requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup
import time


def scrape(url):
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
