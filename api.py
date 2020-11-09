import os
import base64
import hashlib
import hmac
import requests
import json

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]


class Validation:
    def __init__(self, channelsecret):
        self.channelsecret = channelsecret

    def __call__(self, x_line_signature, body):
        hashed = hmac.new(self.channelsecret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
        return x_line_signature.encode("utf-8") == base64.b64encode(hashed)


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


Validate = Validation(CHANNEL_SECRET)
Api = API(CHANNEL_ACCESS_TOKEN)