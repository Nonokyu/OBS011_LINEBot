try:
    import localsetting
    DEBUG = True
except:
    DEBUG = False
from api import Validate, Api
from flask import Flask, request, Response
import json
app = Flask(__name__)


@app.route("/")
def hello():
    name = "Hello World"
    return name


@app.route("/good")
def good():
    name = "Good"
    return name


@app.route("/callback", methods=["POST"])
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



if __name__ == "__main__":
    app.run(debug=DEBUG)
