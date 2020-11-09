# OBS011_LINEBot

## 1. プロジェクト作成後のterminalでの作業

### 1.1 クローン
プロジェクトのホームディレクトリで
```
git clone https://github.com/Nonokyu/OBS011_LINEBot.git
```
を実行する。

### 1.2 必要ライブラリのインストール
clone 成功を確認後、
```
pip install -r"requirements.txt"
```
を実行して、必要なライブラリをインストールする。

これで実行環境は整った。後はコードを確認していく。

requirements.txt　には、このプロジェクトで必要になるライブラリがリストアップされている。

### 1.3 .gitignoreで指定した(githubにアップロードしたくない)ファイルの作成

プロジェクト内のファイルを何でもかんでもgitで共有していては、重要なパスワードが必要になるプログラムの管理ができない。

そのようなときに使用するのが、".gitignore" ファイルである。ここで指定したファイル（または、ディレクトリ）はcommitに含まれなくなる。

当プロジェクトにも.gitignoreは作成してあり、その中を確認すると、

```.gitignore:.gitignore
localsetting.py
.env
```



の2つのファイル名が記載されている。

この2ファイルは当プロジェクトにおいて必要なファイルなので、次のコマンドで作成しておく。

```shell script
type nul > localsetting.py
type nul > .env
```

## 2. app.pyの確認

app.py が当プロジェクトのメインとなるPythonファイルである。

1~8行目

```python:app.py
try:
    import localsetting
    DEBUG = True
except:
    DEBUG = False
```

で実行環境の判定を行っている。

localsetting.py（後で確認）の読み込みが成功すればローカル環境（開発環境）、失敗すればリモート環境（本番環境）と判断している。

※localsetting.pyはローカル環境にしか存在しないファイルであるという前提で

### 2.1 Flask

9行目以降でFlaskというライブラリを使用してプログラムを記述している。

FlaskはWebアプリを作成するためのライブラリである。

記述方法が簡単なため、LINEbotを作るだけなら次回扱うDjangoよりもFlaskの方が手軽である。

基本的な使用方法は、

```python:app.py
from flask import Flask     #インポート
app = Flask(__name__)　　　   #オブジェクト作成

@app.route("/")             #関数の装飾
def hello():
    name = "Hello World"
    return name

if __name__ == "__main__":
    app.run(debug=DEBUG)    #アプリの起動
```

である。 中段の関数の部分を色々変更するだけで、Webアプリを簡単に開発することができる。

@app.route(xxx)の部分でその関数の動作をWebアプリのURLに対応付けている。

WebアプリのURLがhttps://example.comだった場合、上の例だと、https://example.comにアクセスすると関数が実行される。

@app.route("/good")の場合だと、https://example.com/good にアクセスすれば実行される。

今回はLINEBotを作成するだけなので、ブラウザに表示させる必要はなく、ただ、LINEがアクセスしてきたときに適切な処理を行ってLINEに返信を送れればよい。

試しに、
```shell script
python app.py
```
を実行してWebアプリを起動してみよう。

```shell script
* Running on http://127.0.0.1:5000/
```
等が表示され、そのURLにブラウザからアクセスできるようになる。これが、ローカル環境でのアプリのURLである。（ローカルホストと言う）

基本的にここには外部のPCからアクセスすることはできない。それだと、LINEから情報を得られないので、後で紹介するngrokを使用すると外部からのアクセスが可能になる。

### 2.2 LINE Messaging API の仕様

LINEbotを開発するのに使用するLINE　Messaging APIの解説をする。

LINE　Messaging APIは基本的にPOSTメソッドを使用してLINEサーバーとのやり取りを行う。

#### 2.2.1 Webhookの受信

LINEbotで何らかのイベントが発生すると、LINEのサーバーから以下の形式のPOSTが送られてくる。

```text
Header
    X-Line-Signature : 署名の検証に使う署名　（ややこしいので今回は省略するが、BOTを公開する上ではかなり重要）

Body
    events : Webhookイベントのリスト。LINEプラットフォームから疎通確認のために、空のリストが送信される場合がある。
```
Webhookイベントは以下の形式

```json
{
      "replyToken": "0f3779fba3b349968c5d07db31eab56f",
      "type": "message",
      "mode": "active",
      "timestamp": 1462629479859,
      "source": {
        "type": "user",
        "userId": "U4af4980629..."
      },
      "message": {
        "id": "325708",
        "type": "text",
        "text": "Hello, world"
      }
}
```
replyTokenが一番重要で、これが無いとチャットへの返信ができない。

typeはWebhookイベントのタイプを表している。LINEのやり取りで発生するイベントごとにtypeが用意されているが、とりあえずは、
* follow : 友だち登録、ブロック解除
* message : チャット受信

の２つだけ使用している。

Webhookの送信先はLINE Developersから設定できる。これは後で設定を行う。

#### 2.2.2 POST受信のためのFlaskでの設定

LINEからのPOSTを受けると実行される部分は以下である。

```python:app.py
def callback():
    events = request.get_json()["events"]
    body = request.get_data(as_text=True)
    X_Line_Signature = request.headers.get("X-Line-Signature")
    if Validate(X_Line_Signature, body):
        if events:  #Verificationは空POSTなのでそれ以外を選択
            event = events[0]
            if event["type"] == "message":          #イベントタイプで条件分岐　: メッセージイベント
                replytoken = event["replyToken"]    #リプライトークン取得
                msg = event["message"]["text"]      #受信メッセージ取得
                print("message", msg)
                Api.send_messages(replytoken, msg)
            elif event["type"] == "follow":         #友だち登録イベント
                replytoken = event["replyToken"]
                print("follow")
                Api.send_messages(replytoken, "友だち登録ありがとうございます。")
        return Response(status=200)
    else:
        return Response(status=403)
```

まず、リクエストbodyとheaderを使用して署名の確認を行っている。（Validate はapi.py内の自作クラスValidationのインスタンス）

署名の確認ができれば、LINEからのメッセージであるので、以降イベントオブジェクトの中身を見ていく。

イベントタイプで条件分岐を行い、メッセージならその内容をオウム返し、フォローなら挨拶文をLINEサーバーに返信している。（Api　は　api.py内の自作クラスAPIのインスタンス）

#### 2.2.3 返信のための処理

自作クラスAPIの中を見て、サーバーへの返信方法を確認していく。

サーバーへの返信にもPOSTメソッドが利用されている。その構造は以下。

```text
Header
    "Content-Type": "application/json",
    "Authorization": "Bearer "+CHANNEL_ACCESS_TOKEN <- これはLINE Developersから調べられる。他人に教えないこと。
Body
    "data" : JSONデータ 
```
dataの書式は以下。
```json
{
  "replyToken": "**イベント内記載のリプライトークン**",
  "messages": [
    {
      "type": "text",
      "text": "**送信メッセージの文面**"
    }
  ]
}
```
messagesがリスト形式になっていることがポイントである。ここに5つまで要素を加えることができる。

つまり、同時に5通まで返信メッセージを送ることができる。

これら返信処理を行うのが自作クラスAPIである。

```python:api.py
class API:
    def __init__(self, channelaccesstoken):
        self.channelaccesstoken = channelaccesstoken
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer "+channelaccesstoken
        }

    def send_messages(self, token, msgs):
        if type(msgs)==list or type(msgs)==tuple :
            data = {
                "replyToken": token,
                "messages": [
                    {
                        "type": "text",
                        "text": f"{msg}"
                    } for msg in msgs
                ]
            }
        else:
            data = {
                "replyToken": token,
                "messages": [
                    {
                        "type": "text",
                        "text": f"{msgs}"
                    }
                ]
            }
        requests.post('https://api.line.me/v2/bot/message/reply',
                      data=json.dumps(data),
                      headers=self.headers)
```

CHANNEL_ACCESS_TOKENを与えてインスタンスを生成して、send_messagesメソッドでlineのサーバーにPOSTを送信する。

POSTの送信部分はrequestsライブラリを使用している。

LINE Developersのリファレンスを見ればただの文面を送る以外に、他にも様々なメッセージの送り方が書かれているので是非調べてもらいたい。

基本的にmessagesの要素を変更するだけである。

## 3. LINE Developersでの設定

コードの説明はこれで以上なので、LINE Developersでbotを使うための設定を行う。

### 3.1 CHANNEL_ACCESS_TOKENとCHANNEL_SECRETの取得

自分のBotの設定画面を開き、

Basic　settings下部に記載されている　Channel secretと　

Messaging API下部のChannel access tokenを.envに以下のように書き加える。

初めての場合は、発行ボタンを押すとChannel access tokenが発行される。

.envファイルは以下のようになる。

```text:.env
CHANNEL_ACCESS_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CHANNEL_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXX
```
「=」の前後にスペースは入れないこと。

このように、外部に漏らしたくない変数は環境変数として保存しておく。もちろん、.gitignoreのおかげで、commitには反映されない。

### 3.2 Webhookの有効化

次はLINEのサーバーにPOSTの送り先を教える。

Webhook settingsのWebhookURLにアプリのURLを入力する。

今回はローカルホストでの実行になるので、事前にngrokを実行して外部からローカルホストにアクセスするための一時的なURLを発行しておく。

おそらく、https://ｘｘｘｘｘｘｘｘ.ngrok.io のようなURLが発行されるので、

https://ｘｘｘｘｘｘｘｘ.ngrok.io/callback　と入力すれば設定完了である。

※LINEはSSL対応のURL（https://で始まるURL）しか使用できない。

### 3.3 その他応答設定
デフォルトのままだと、応答メッセージと挨拶メッセージがオンになっているので、BOTからの応答とLINEデフォルトの応答の両方が発生してしまう。

それを解消するために、設定から、これらをOFFにすることができる。