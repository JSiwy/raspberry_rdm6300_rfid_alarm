#!/usr/bin/env python

import RPi.GPIO as GPIO
import rdm6300
#from dotenv import load_dotenv
import requests
import time
import json

#load_dotenv()

reader = rdm6300.Reader('/dev/ttyS0')

locked_url = '/locked'
user_url = '/check_rfid'
RELAY = 18 #GPIO 24
GREEN = 40
CZUJ = 26 

while True:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CZUJ, GPIO.IN)
    time.sleep(5)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    try:
        if GPIO.input(CZUJ):
            print("t2")
            responseA = requests.get(locked_url)
            if responseA.json().get('locked'):
                print('t1')
                card = reader.read()
                time.sleep(0.1)
                id = card.value
                print(id)
                payload = {"rfid": f'{id}'}
                response = requests.post(user_url,data = json.dumps(payload), headers = {'content-type':'application/ld+json'})
                print(json)
                print(response)
                if response.status_code == 422:
                    print('User not found. Alarm!')
                    GPIO.output(RELAY, GPIO.HIGH)
                    time.sleep(2)
                    GPIO.output(RELAY, GPIO.LOW)
                elif response.status_code == 204:
                    print('Disarmed')
                    GPIO.output(GREEN, GPIO.HIGH)
                    time.sleep(120)
                    GPIO.output(GREEN, GPIO.LOW)
                    time.sleep(30)
                elif response.status_code == None:
                    print('t3')
                else:
                    print('Error!')
            else:
                print('t4')
                GPIO.output(RELAY, GPIO.LOW) #wyłączenie syreny
                
    finally:
        GPIO.cleanup()
