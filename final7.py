import cv2
import numpy as np
import datetime
import time
import serial
from flask import Flask, request, render_template
import RPi.GPIO as GPIO
import threading

# GPIO setup
window23 = 23
window24 = 24
fire = 14
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(window23, GPIO.OUT)
GPIO.setup(window24, GPIO.OUT)
GPIO.setup(fire, GPIO.OUT)

# Serial setup
ser2 = serial.Serial(port='/dev/ttyAMA4', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)

degree = 0
total_state = ""
sensor_data = {
    "rain": "N/A",
    "gas": "N/A",
    "hum": "N/A",
    "tem": "N/A",
    "dust": "N/A"
}
sensor_status = {
    "rain": "N/A",
    "gas": "N/A",
    "hum": "N/A",
    "tem": "N/A",
    "dust": "N/A"
}

class FireDetector:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()

    def detect_fire(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([15, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        fire_pixels = cv2.countNonZero(mask)
        return fire_pixels > 3000

fire_detector = FireDetector()
cap = cv2.VideoCapture(0)

app = Flask(__name__)

start_time = None
end_time = None
hh1 = 0
mm1 = 0
hh2 = 0
mm2 = 0
window_book = None

hand_control = 1

@app.route('/')
def home():
    global degree

    degree_s = "Fire!!!!!!!" if degree == 1 else "No Fire"

    return render_template("index.html", 
                           rain=sensor_data["rain"], 
                           gas=sensor_data["gas"], 
                           hum=sensor_data["hum"], 
                           tem=sensor_data["tem"], 
                           dust=sensor_data["dust"], 
                           degree_s=degree_s, 
                           rain_s=sensor_status["rain"], 
                           gas_s=sensor_status["gas"], 
                           hum_s=sensor_status["hum"], 
                           tem_s=sensor_status["tem"], 
                           dust_s=sensor_status["dust"])

@app.route('/data', methods=['POST'])
def data():
    global hand_control
    hand_control = 1
    data = request.form['window']
    try:
        if hand_control == 1:
            if data == 'open':
                GPIO.output(window23, 1)
                GPIO.output(window24, 1)
            elif data == 'close':
                GPIO.output(window23, 1)
                GPIO.output(window24, 0)
            elif data == 'auto':
                GPIO.output(window23, 0)
                GPIO.output(window24, 0)
        return home()
    except Exception as e:
        print(f"Error in data route: {e}")
        return str(e)

@app.route('/submit', methods=['POST'])
def submit_hour():
    global start_time, end_time, hh1, mm1, hh2, mm2, window_book, hand_control
    hand_control = 0
    try:
        time_input = request.form['hhmm']
        start_time, end_time, window_book = time_input.split("-")
        hh1, mm1 = map(int, start_time.split(":"))
        hh2, mm2 = map(int, end_time.split(":"))
        time.sleep(0.1)
        return home()
    except Exception as e:
        print(f"Error in submit_hour route: {e}")
        return str(e)

def capture_and_detect():
    global degree
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        is_fire = fire_detector.detect_fire(frame)

        if is_fire:
            text = "Fire detected!"
            color = (0, 0, 255)
            degree = 1
        else:
            text = "No fire detected"
            color = (0, 255, 0)
            degree = 0

        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.imshow('Fire Detection', frame)
        GPIO.output(fire, degree)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def check_time_and_update_gpio():
    global hh1, mm1, hh2, mm2, window_book, hand_control

    while True:
        time.sleep(0.1)
        now = datetime.datetime.now()
        real_hour = (now.hour + 8) % 24
        real_minute = now.minute
        if hand_control == 0:
            if (hh1 * 100 + mm1) <= (hh2 * 100 + mm2):
                if (hh1 <= real_hour <= hh2 and mm1 <= real_minute <= mm2 and window_book == '1'):
                    GPIO.output(window23, 1)
                    GPIO.output(window24, 1)
                elif (hh1 <= real_hour <= hh2 and mm1 <= real_minute <= mm2 and window_book == '0'):
                    GPIO.output(window23, 1)
                    GPIO.output(window24, 0)
            else:
                if (hh1 <= real_hour <= hh2 + 24 and mm1 <= real_minute <= mm2 and window_book == '1'):
                    GPIO.output(window23, 1)
                    GPIO.output(window24, 1)
                elif (hh1 <= real_hour <= hh2 + 24 and mm1 <= real_minute <= mm2 and window_book == '0'):
                    GPIO.output(window23, 1)
                    GPIO.output(window24, 0)

def update_sensor_data():
    global sensor_data, sensor_status
    while True:
        try:
            if ser2.in_waiting > 0:
                total_state = ser2.readline().decode('utf-8').strip()
                result_state = total_state.split(":")
                if len(result_state) > 0:
                    sensor_data["rain"] = result_state[0]
                    sensor_status["rain"] = "Raining" if int(result_state[0]) <= 600 else "No raining"
                if len(result_state) > 1:
                    sensor_data["gas"] = result_state[1]
                    sensor_status["gas"] = "High Gas" if int(result_state[1]) >= 500 else "Low gas"
                if len(result_state) > 2:
                    sensor_data["hum"] = result_state[2]
                    sensor_status["hum"] = "High humidity" if float(result_state[2]) >= 80 else "Low humidity"
                if len(result_state) > 3:
                    sensor_data["tem"] = result_state[3]
                    sensor_status["tem"] = "High temperature" if float(result_state[3]) >= 30 else "Low temperature"
                if len(result_state) > 4:
                    sensor_data["dust"] = result_state[4]
                    sensor_status["dust"] = "High dust density" if float(result_state[4]) >= 800 else "Low dust density"
        except Exception as e:
            print(f"Error in update_sensor_data thread: {e}")
        time.sleep(1)  # Adjust the sleep duration as needed

if __name__ == "__main__":
    threading.Thread(target=capture_and_detect).start()
    threading.Thread(target=check_time_and_update_gpio).start()
    threading.Thread(target=update_sensor_data).start()
    app.run(host='192.168.32.45', port=8080)
