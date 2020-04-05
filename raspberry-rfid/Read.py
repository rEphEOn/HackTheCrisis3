#!/usr/bin/env python
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import post

reader = SimpleMFRC522()
while True:
    id, text = reader.read()
    text = text.replace('\n', '').lstrip().rstrip()
    if text:
        post.post(text, text)
