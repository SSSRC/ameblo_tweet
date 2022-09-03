import requests
import re
import pandas as pd
from twitter import Twitter, OAuth

# Slack投稿用
import json
def post2slack(msg):
  WEB_HOOK_URL = "WEB_HOOK_URL"
  requests.post(WEB_HOOK_URL, data = json.dumps({
      'text': msg,  #通知内容
      'username': u'ameblo-notify',  #ユーザー名
      'icon_emoji': u':ameblo:',  #アイコン
      'link_names': 1,  #名前をリンク化
  }))

def getTitleFromURL(url):
  html = requests.get(url)
  title = re.findall(r'<meta data-react-helmet="true" property="og:title" content="『.*』"/>', html.text)[0]
  title = title.split('"/>')[0]
  title = title.split('<meta data-react-helmet="true" property="og:title" content="')[1]
  return title


def post2twitter(msg):
  access_token = "ACCESS_TOKEN"
  access_token_secret = "ACCESS_TOKEN_SECRET"
  api_key = "API_KEY"
  api_secret = "API_SECRET"

  t = Twitter(auth = OAuth(access_token, access_token_secret, api_key, api_secret))
  statusUpdate = t.statuses.update(status=msg)


# スクレイピング(雑)
base_url = "https://ameblo.jp"
entrylist_url = base_url + "/sssrc/entrylist.html"
html = requests.get(entrylist_url)
urls = re.findall(r'/sssrc/entry-\d{11}.html', html.text)
print(len(set(urls)))

# IdとURLの辞書作成
entry_id = {}
for path in set(urls):
  entry_id[int(path[13:24])] = base_url + path

# 既存データベースの取得
try:
  df = pd.read_csv("data/data.csv")
  print("データをロードしました")
  print(df)
  ids = set(df["id"]) #setにすることで計算量が(以下略)
except FileNotFoundError:
  print("データがありません")
  df = pd.DataFrame(index=[], columns=["id","url"])
  ids = set()

# 既存のデータベースとの参照、Slackで通知
for id in entry_id:
  if id in ids:
    pass
  else:
    url = entry_id[id]
    tweet_url = "https://twitter.com/intent/tweet?url=" + url
    print("新規投稿:",url,", TweetURL:",tweet_url)
    # Twitter自動投稿
    tweet_msg = 'アメブロを投稿しました！\n\n' + title + '\n⇨ ' + url
    post2twitter(tweet_msg)
    # Slack投稿テンプレート
    msg = "アメブロに新規投稿がありました\nURL:"+ url + "\nTwitterへ自動投稿されました．"
    post2slack(msg)
    df = pd.concat([df, pd.DataFrame({'id': [id], 'url': [url]})], ignore_index=True)
    # break # デバッグ用

# 出力
df.to_csv("data/data.csv",index=False)
