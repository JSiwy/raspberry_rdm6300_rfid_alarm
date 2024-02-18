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

def Alarm(log_time):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RELAY, GPIO.HIGH)
    GPIO.output(RED, GPIO.HIGH)
    while time.time() - log_time < 30:
        card = reader.read(1)
        time.sleep(0.1)
        if card is not None:
            GPIO.output(RED, GPIO.LOW)
            id = card.value
            Check(id)
        time.sleep(1)
    GPIO.output(RELAY, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)
    GPIO.cleanup()

def Disarm(login_time):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.output(GREEN, GPIO.HIGH)
    while time.time() - login_time < 15:
        if (time.time() - login_time > 10):
            GPIO.output(GREEN, GPIO.LOW)
        card = reader.read(1)
        time.sleep(0.1)
        if card is not None:
            GPIO.output(GREEN, GPIO.HIGH)
            id = card.value
            login_time = time.time()
        time.sleep(1)

def Check(id):
    payload = {"rfid": f'{id}'}
    response = requests.post(user_url,data = json.dumps(payload), headers = {'content-type':'application/ld+json'})
    if response.status_code == 422:
        Alarm(log_time)
    elif response.status_code == 204:
        login_time = time.time()
        Disarm(login_time)
    else:
        print('Error!')

while True:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CZUJ, GPIO.IN)
    time.sleep(5)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(GREEN, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)
    try:
        if GPIO.input(CZUJ):
            responseA = requests.get(locked_url)
            if responseA.json().get('locked'):
                start_time = time.time()
                card = reader.read(10)
                time.sleep(0.1)
                if card is not None:
                    id = card.value
                    login_time = time.time()
                    Disarm(login_time)
                    time.sleep(1)
                else:
                    log_time = time.time()
                    Alarm(log_time)
                Check(id)
                
            else:
                GPIO.output(RELAY, GPIO.LOW) #wyłączenie syreny
    finally:
        GPIO.cleanup()
