import json
import firebase_admin
from firebase_admin import credentials, messaging
import flask
import requests
from flask import Flask, request

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

activebooth = {}


def sendPush(title, msg, booth_):
    topic = str(booth_)

    # See documentation on defining a message payload.
    message = messaging.Message(
        data={
            'topic': topic
        },
        notification=messaging.Notification(
            title=title,
            body=msg,
        ),
        topic=topic
    )
    messaging.send(message)
    print("Notification Sent")


port = 80

app = Flask("PiLED")


@app.route("/sendNotification", methods=['GET', 'POST'])
def sendNotification():
    res = {'notification': "Failed"}
    booth = request.args.get("booth")
    if request.args.get("booth") is not None and request.args.get("booth") != "":
        res = {'notification': "Success", 'booth': request.args.get("booth")}
        activebooth.setdefault(booth, request.args.get("server"))
        sendPush('New Order-Booth' + str(booth), 'Click to confirm Order', booth)
    return json.dumps(res)


@app.route("/update_status", methods=['GET', 'POST'])
def changeLED():
    res = {'changeLED': "Failed"}
    color = request.args.get("status")
    print(color)
    print(request.args.get("booth"))
    print(activebooth.get(request.args.get("booth")))
    if request.args.get("booth") is not None and request.args.get("status") is not None and request.args.get(
            "booth") != "":
        response = requests.post('http://'+activebooth.get(request.args.get("booth"))+'/update_status',
                                 params={'status': color, 'booth': request.args.get("booth")})
        if response.status_code == 200:
            res = {'changeLED': 'Success'}
            

    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
