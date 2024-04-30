# 1.아두이노, 파이썬 연결
# 1-1. 아두이노 

include <SPI.h>
include <Ethernet.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177); // 아두이노의 IP 주소
EthernetServer server(80);

void setup() {
  Ethernet.begin(mac, ip);
  server.begin();
  pinMode(2, OUTPUT); // 센서 또는 LED 연결 핀
}

void loop() {
  EthernetClient client = server.available();
  if (client) {
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        // HTTP 요청 처리 로직 구현
        if (c == '\n' && currentLineIsBlank) {
          // 여기에 요청에 따라 센서를 제어하는 코드 작성
          digitalWrite(2, HIGH); // 예를 들어, LED 켜기
          delay(1000);
          digitalWrite(2, LOW); // LED 끄기
          client.stop();
        }
        if (c == '\n') {
          currentLineIsBlank = true;
        } else if (c != '\r') {
          currentLineIsBlank = false;
        }
      }
    }
  }
}

# 1-2. 파이썬 코드
import streamlit as st
import requests

def send_command():
    # 아두이노 서버의 IP 주소와 포트
    url = "http://192.168.1.177"
    response = requests.get(url)
    if response.status_code == 200:
        st.success("명령이 성공적으로 전송되었습니다.")
    else:
        st.error("명령 전송에 실패했습니다.")

st.title("아두이노 제어")
st.button("센서 켜기", on_click=send_command)

#---------------------------------------------------------------
# 2. 센서 제어 - 웹사이트에 접속했을때 LED를 키고 끄는 코드
# 파일 이름: flaskTest.py
from flask import Flask, render_template_string
import RPi.GPIO as GPIO

app = Flask(__name__)

# GPIO 설정
GPIO.setmode(GPIO.BCM)
sensor_pin = 18
GPIO.setup(sensor_pin, GPIO.OUT)

# HTML 페이지 템플릿
HTML = '''
<!doctype html>
<html>
<head>
<title>GPIO Control</title>
</head>
<body>
    <h1>GPIO Control Interface</h1>
    <button onclick="fetch('/on').then(response => response.text()).then(html => document.getElementById('status').innerHTML = html)">Turn ON</button>
    <button onclick="fetch('/off').then(response => response.text()).then(html => document.getElementById('status').innerHTML = html)">Turn OFF</button>
    <p id="status">Sensor is OFF</p>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/on')
def gpio_on():
    GPIO.output(sensor_pin, GPIO.HIGH)
    return 'Sensor is ON'

@app.route('/off')
def gpio_off():
    GPIO.output(sensor_pin, GPIO.LOW)
    return 'Sensor is OFF'

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080)
    finally:
        GPIO.cleanup()  # 앱 종료 시 GPIO 핀을 초기화
