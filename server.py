#!/usr/bin/env python3

"""
A simple echo server that handles some exceptions
"""

import socket
import signal
import sys
import json
from os.path import join, dirname
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
from ibm_watson import ApiException
import os
import time
import datetime
import mmap
import wolframalpha
import pickle
import hashlib
from cryptography.fernet import Fernet
from pygame import mixer
import netifaces

from ServerKeys import watsonURL
from ServerKeys import watsonDevKey
from ServerKeys import wolframKey

if(len(sys.argv) != 5):
    print('incorrect number of arguments')
    exit()
else:
    port = int(sys.argv[2])
    size = int(sys.argv[4])

host = ''
backlog = 5

IPAddr = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr']

print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 01] Created Socket at " + IPAddr + " on port " + str(port))
print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 02] Listening for client connections")

s = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind((host,port))
    s.listen(backlog)
except socket.error as message:
    if s:
        s.close()
    print ("Could not open socket: " + str(message))
    sys.exit(1)
while 1:
    try:
        client, address = s.accept()

        print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 03] Accepted client connection from " + address[0] + " on port " + str(port))
        data = client.recv(size)
        if data:
            # Unpickeling 
            ques_tuple = pickle.loads(data)

            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 04] Received data: " + str(ques_tuple))
            # Parameterizing payload
            key = ques_tuple[0]
            ques_cyp_text = ques_tuple[1]
            ques_hash = ques_tuple[2]

            # Error checking hash of question cyphertext
            if hashlib.sha256(ques_cyp_text).hexdigest() != ques_hash:
                print("ERROR: The question hash does not match the given question, closing connection.")
                client.close()
                continue
            
            # Setting the cypher key
            f_obj = Fernet(key)

            # Decrypting the answer
            Qbytes = f_obj.decrypt(ques_cyp_text)

            text = Qbytes.decode("utf-8")

            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 05] Decrypt: Key: " + str(key) + " | Plain text: " + str(text))
        
            if (text == 'close server'):
                exit()

            # If service instance provides API key authentication
            service = TextToSpeechV1(url = watsonURL, iam_apikey= watsonDevKey)


            with open('QAudio.mp3', 'wb') as audio_file:
                audio_file.write(
                    service.synthesize(
                        text,
                        voice='en-US_AllisonVoice',
                        accept='audio/mp3'        
                    ).get_result().content)
                audio_file.close()		
        
            with open('QAudio.mp3') as f:
                m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                mixer.init()
                mixer.music.load(m)
                print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 06] Speaking Question: " + text)
                mixer.music.play()
        
                while mixer.music.get_busy():
                    time.sleep(1)
                mixer.music.stop()
                mixer.quit()

                m.close()

            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 07] Sending question to Wolframalpha: " + text)
            Wclient = wolframalpha.Client(wolframKey)

        
            query = text
            res = Wclient.query(query)
            output = next(res.results).text
            
            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 08] Recieved anwser from Wolframalpha: " + output)

            # Encrypting the answer
            cyphertext = f_obj.encrypt(bytes(output, 'utf-8'))

            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 09] Encrypt: Key: " + str(key) + " | Ciphertext: " + str(cyphertext))

            # Computing the sha Checksum
            checkSum = hashlib.sha256(cyphertext).hexdigest()

            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 10] Generated MD5 Checksum: " + str(checkSum))
            # Creating tuple to send
            send_tup = (cyphertext, checkSum)

            # Pickeling tuple
            outputb = pickle.dumps(send_tup)
            
            print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 11] Sending answer: " + str(outputb))
            # Sending byte stream
            client.send(outputb)
        client.close()
   
    # Implementing interrupt handling 
    except KeyboardInterrupt:
        s.close()
        break
