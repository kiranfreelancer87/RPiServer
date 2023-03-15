import json
import requests
from flask import Flask, request
import RPi.GPIO as GPIO
from gpiozero import LED
from gpiozero import Button
from time import sleep
import socket
import socket

port = 8088

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP
ipaddr = extract_ip()
booths = {}


def get_key(val):
    for key, value in booths.items():
        if val == value:
            return key
    return None


# BOOTH 1
red1 = LED(27)
green1 = LED(17)
btn1 = Button(22)

# BOOTH 2
red2 = LED(24)
green2 = LED(23)
btn2 = Button(25)

# BOOTH 3
red3 = LED(5)
green3 = LED(6)
btn3 = Button(12)

# BOOTH 4
red4 = LED(13)
green4 = LED(19)
btn4 = Button(26)

# BOOTH 5
red5 = LED(16)
green5 = LED(20)
btn5 = Button(21)

green1.off()
green2.off()
green3.off()
green4.off()
green5.off()

red1.on()
red2.on()
red3.on()
red4.on()
red5.on()




def redOn(booth_int):
    if booth_int == 1:
        allOff(booth_int)
        print("Red")
        green1.off()
        red1.on()
    if booth_int == 2:
        allOff(booth_int)
        print("Red")
        green2.off()
        red2.on()
    if booth_int == 3:
        allOff(booth_int)
        print("Red")
        green3.off()
        red3.on()
    if booth_int == 4:
        allOff(booth_int)
        print("Red")
        green4.off()
        red4.on()
    if booth_int == 5:
        allOff(booth_int)
        print("Red")
        green5.off()
        red5.on()


def greenOn(booth_int):
    if booth_int == 1:
        allOff(booth_int)
        print("Green")
        red1.off()
        green1.on()
    if booth_int == 2:
        allOff(booth_int)
        print("Green")
        red2.off()
        green2.on()
    if booth_int == 3:
        allOff(booth_int)
        print("Green")
        red3.off()
        green3.on()
    if booth_int == 4:
        allOff(booth_int)
        print("Green")
        red4.off()
        green4.on()
    if booth_int == 5:
        allOff(booth_int)
        print("Green")
        red5.off()
        green5.on()


def blink(booth_int):
    if booth_int == 1:
        red1.blink()
        sleep(1)
        green1.blink()
    if booth_int == 2:
        red2.blink()
        sleep(1)
        green2.blink()
    if booth_int == 3:
        red3.blink()
        sleep(1)
        green3.blink()
    if booth_int == 4:
        red4.blink()
        sleep(1)
        green4.blink()
    if booth_int == 5:
        red5.blink()
        sleep(1)
        green5.blink()


def allOff(booth_int):
    if booth_int == 1:
        red1.off()
        green1.off()
    if booth_int == 2:
        red2.off()
        green2.off()
    if booth_int == 3:
        red3.off()
        green3.off()
    if booth_int == 4:
        red4.off()
        green4.off()
    if booth_int == 5:
        red5.off()
        green5.off()


booth = 0
server_ip = ""

def buttonPushed(booth, server):
    response = requests.post('http://' + server_ip + ':80/sendNotification',
                             params={'booth': booth, 'server': server})
    return response.text


def setReleased(booth_int):
    booth_in = get_key(booth_int)
    res = buttonPushed(booth_in, str(ipaddr + ":" + str(port)))
    print(res)
    allOff(booth_int)
    blink(booth_int)


def btnReleased1():
    setReleased(1)


def btnReleased2():
    setReleased(2)


def btnReleased3():
    setReleased(3)


def btnReleased4():
    setReleased(4)


def btnReleased5():
    setReleased(5)


btn1.when_released = btnReleased1
btn2.when_released = btnReleased2
btn3.when_released = btnReleased3
btn4.when_released = btnReleased4
btn5.when_released = btnReleased5


def getInput(index):
    try:
        val = int(input("Enter Booth Number"))
        booths.setdefault(val, index)
    except Exception as e:
        print("Error:", e)
        getInput(index)





def setServerIP():
    global server_ip
    server_ip = input("Enter IP")
    print("IP is: ", server_ip)


def init():
    for i in range(1, 6):
        getInput(i)


init()
setServerIP()

print(booths)

app = Flask("PiLED")


@app.route("/", methods=['GET', 'POST'])
def index():
    res = buttonPushed(1, str(ipaddr + ":" + str(port)))
    return res


@app.route("/booth", methods=['GET', 'POST'])
def booth():
    res = {"body": "Invalid Request"}
    try:
        if len(request.args.get("booth")) is not None:
            booth = request.args.get("booth")
            key = "B" + booth
            if booths.get(key) is not None:
                res = {str(str(ipaddr + ":" + str(port))): booths.get(key)}
                print(res)
    except:
        pass
    return json.dumps(res)


@app.route("/update_status", methods=['GET', 'POST'])
def get_report():
    status = str(request.args.get("status"))
    booth_int = int(request.args.get("booth"))
    booth_ = int(booths.get(booth_int))
    if status == 'red':
        allOff(booth_)
        redOn(booth_)
    if status == 'green':
        allOff(booth_)
        greenOn(booth_)
    if status == 'blink':
        allOff(booth_)
        blink(booth_)

    return json.dumps({'status': status, 'booth': booth_})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=port)

