import cv2
from flask import Flask
from flask import request
import robot
import time


app = Flask(__name__)
robot = robot.Robots()


@app.route('/qr_code')
def search_qr():
    code_key = request.args.get('code')
    user = request.args.get('user')
    if code_key is None:
        return 'Не передан код!', 400
    else:
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        while True:
                _, img = cap.read()
                data, vertices_array, _ = detector.detectAndDecode(img)
                if vertices_array is not None:
                    if data:
                        if  data == code_key:
                            print('Код верный')
                            robot.container_opening('ON')
                            break
                        else:
                            print('Код неверный')
        """добавить считку положения ( закрылся если угол равен такомо ту числу, запрашиваем угол и сранвиваем"""
        time.sleep(5)
        robot.container_opening('OFF')
        key = {'user': user}
        return key


@app.route("/forward", methods=['GET', 'POST'])
def forward():
	robot.robot_movement('forward')
	return ('', 204)


@app.route("/backward", methods=['GET', 'POST'])
def backward():
	robot.robot_movement('back')
	return ('', 204)

@app.route("/turnRight", methods=['GET', 'POST'])
def turn_right():
	robot.robot_movement('right')
	return ('', 204)


@app.route("/turnLeft", methods=['GET', 'POST'])
def turn_left():
	robot.robot_movement('left')
	return ('', 204)


@app.route("/stop", methods=['GET', 'POST'])
def stop():
	robot.robot_movement('stop')
	return ('', 204)


@app.route("/offlight", methods=['GET', 'POST'])
def off():
	robot.container_opening('OFF')
	return ('', 204)


@app.route("/onlight", methods=['GET', 'POST'])
def on():
	robot.container_opening('ON')
	return ('', 204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7092)