#!/usr/bin/env python

import RPi.GPIO as GPIO
import rdm6300
import requests
import time
import json

reader = rdm6300.Reader('/dev/ttyS0')
locked_url = '/locked'
user_url = '/check_rfid'
RELAY = 18 #GPIO 24
GREEN = 40
RED = 38
CZUJ = 26 

def Alarm():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RELAY, GPIO.HIGH)
    GPIO.output(RED, GPIO.HIGH)
    time.sleep(10)
    GPIO.output(RELAY, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)
    GPIO.cleanup()

while True:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CZUJ, GPIO.IN)
    time.sleep(5)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    try:
        if GPIO.input(CZUJ):
            responseA = requests.get(locked_url)
            if responseA.json().get('locked'):
                start_time = time.time()
                while time.time() - start_time < 30:
                    card = reader.read()
                    time.sleep(0.1)
                    id = card.value
                    if id is not None:
                        login_time = time.time()
                        break
                    time.sleep(1)
                else:
                    Alarm()
                payload = {"rfid": f'{id}'}
                response = requests.post(user_url,data = json.dumps(payload), headers = {'content-type':'application/ld+json'})
                if response.status_code == 422:
                    print('User not found. Alarm!')
                    Alarm()
                elif response.status_code == 204:
                    GPIO.output(GREEN, GPIO.HIGH)
                    print('Disarmed')
                    while time.time() - login_time < 150:
                        if (time.time() - login_time > 120):
                            GPIO.output(GREEN, GPIO.LOW)
                        card = reader.read()
                        time.sleep(0.1)
                        id = card.value
                        if(id!=None):
                            login_time = time.time()
                        time.sleep(1)
                else:
                    print('Error!')
            else:
                GPIO.output(RELAY, GPIO.LOW) #wyłączenie syreny
    finally:
        GPIO.cleanup()
