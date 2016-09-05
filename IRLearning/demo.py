
import os
import signal
from microphone import Microphone
from bing_voice import *
from player import Player
import pyaudio
import sys
import time
import re
from spi import SPI
import json
import urllib

try:
    from creds import BING_KEY
except ImportError:
    print('Get a key from https://www.microsoft.com/cognitive-services/en-us/speech-api and create creds.py with the key')
    sys.exit(-1)

script_dir = os.path.dirname(os.path.realpath(__file__))

hi = os.path.join(script_dir, 'audio/hi.wav')
thunder = os.path.join(script_dir, 'audio/thunder-01.wav')
startlearning = os.path.join(script_dir,'audio/startlearning.wav')
stoplearning  = os.path.join(script_dir,'audio/stoplearning.wav')
sendir        = os.path.join(script_dir,'audio/sendir.wav')

spi = SPI()
spi.write('offline\n')

bing = BingVoice(BING_KEY)

mission_completed = False
awake = False

pa = pyaudio.PyAudio()
mic = Microphone(pa)
player = Player(pa)

spi.write('online\n');

def handle_int(sig, frame):
    global mission_completed
    mission_completed = True
    mic.close()


signal.signal(signal.SIGINT, handle_int)

while not mission_completed:
    if not awake:
        if mic.detect():
            spi.write('wakeup\n')
            awake = True
            player.play(hi)
        continue

    data = mic.listen()
    spi.write('wait\n')

    # recognize speech using Microsoft Bing Voice Recognition
    try:
        text = bing.recognize(data, language='en-US')
        spi.write('answer\n')
        print('Bing:' + text.encode('utf-8'))
        
        if re.search(r'start', text):
            spi.write('irlearning\n')
            player.play(startlearning)
            
        elif re.search(r'stop',text):
            spi.write('stoplearning\n')
            player.play(stoplearning)
        elif re.search(r'control',text):
            spi.write('control\n')
            player.play(sendir)
        else:
            print 'unknown command, ignore.' 
        
    except UnknownValueError:
        print("Microsoft Bing Voice Recognition could not understand audio")
    except RequestError as e:
        print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))

    spi.write('sleep\n')
    awake = False
