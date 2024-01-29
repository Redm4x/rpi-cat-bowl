from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from flask import Flask, render_template, Response
import cv2
import time
from threading import Thread

camera = cv2.VideoCapture(0)

app = Flask(__name__)
isOpen = False
targetAngle = [-1]

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/open_close")
def open_or_close():
    global isOpen,targetAngle
    if isOpen:
        print("closing")
        targetAngle[0] = -1
    else:
        print("opening")
        targetAngle[0] = 1
    isOpen=not isOpen
    return "Done"

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def motor_control_loop(targetAngle):
    pinFactory = PiGPIOFactory()
    servo = Servo(17,initial_value=-1,min_pulse_width=0.5/1000,max_pulse_width =2.5/1000, pin_factory=pinFactory)

    currentAngle = -1
    while(True):
        angleDiff = targetAngle[0] - currentAngle
        fullAngleDuration = 2
        steps = 100
        step = fullAngleDuration / steps
        
        if(abs(angleDiff) > 0):
            cappedAngleDiff = min(abs(angleDiff),step)
            cappedAngleDiff = cappedAngleDiff if angleDiff > 0 else -cappedAngleDiff
            servo.value = currentAngle + cappedAngleDiff
            currentAngle  = currentAngle + cappedAngleDiff
        
        time.sleep(fullAngleDuration / steps)

if __name__ == "__main__":
    thread = Thread(target=motor_control_loop, args=(targetAngle,))
    thread.start()
    app.run(debug=False,host="0.0.0.0")
