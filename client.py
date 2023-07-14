#!/usr/bin/env python3

"""
A simple echo client that handles some exceptions
"""

import tweepy
import socket
import sys
import json
import datetime
from os.path import join, dirname
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
from ibm_watson import ApiException
import os
import time
import mmap
import hashlib
from cryptography.fernet import Fernet
import pickle

#importing keys from external file
from ClientKeys import watsonURL
from ClientKeys import watsonDevKey
from ClientKeys import consumer_key
from ClientKeys import consumer_secret
from ClientKeys import access_token
from ClientKeys import access_token_secret

import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer


#stream listening 
class MyStreamListener(tweepy.StreamListener):
    # Member Variables
    myText = ""
    hasData = False
    # status handler
    def on_status(self, status):
        print(status.text)
        self.myText = status.text
        self.hasData = True
    #function to set the value of hasData
    def set_data_flag(self, val):
        self.hasData = val
    #error handler
    def on_error(self, status):
        print(status)
        if status == 420:
            return False


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

myListen = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener = myListen)
myStream.filter(follow=['2296781816'], track=['ECE4564T12'], is_async=True)
#myStream.filter()



if (len(sys.argv) != 7):
    print("Incorrect number of arguements passeed to program.")
    exit()
else:
    host = str(sys.argv[2])
    port = int(sys.argv[4])
    size = int(sys.argv[6])

run = True
# Adding a while loop to allow user to enter multiple questions
while run:
    
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))

    #except socket.error, (value,message):
    except socket.error as message:
        if s:
            s.close()
        print ("Unable to open the socket: " + str(message))
        sys.exit(1)

    print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 01] Connecting " + str(host) + " on port " + str(port))

    # Listen for the tweet
    while myListen.hasData == False:
        time.sleep(1)
    text = myListen.myText.replace("#ECE4564T12","")
    myListen.set_data_flag(False)
    
    
    print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 03] New Question " + text)
    # Adding code to encrypt question text
    # This is the encrypt/decrypt key
    key = Fernet.generate_key()

    # Creating a Fernet Object from the generated key
    f_obj = Fernet(key)

    # Encrypting the question
    cyphertext = f_obj.encrypt(bytes(text, 'utf-8'))

    # Computing the sha Checksum
    checkSum = hashlib.sha256(cyphertext).hexdigest()
	
    print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 04] Encrypt: Generated Key: " + str(key) + " | Cipher text: " + str(cyphertext))
	# Creating tuple to send
    send_tup = (key, cyphertext, checkSum)
	
	# Pickeling tuple
    sendb = pickle.dumps(send_tup)

    print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 05] Sending data: " + str(sendb))
    # Send pickled tuple
    s.send(sendb)

    if(text == 'close server'):
        s.close()
        exit()
    
    # Waiting for server response
    # Recieving pickeled tuple 
    recieveb = s.recv(size)

    print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 06] Received data: " + str(recieveb))

    # Unpickling 
    recieve_tup = pickle.loads(recieveb)

    # Answer Cypher Text
    ans_cypher = recieve_tup[0]

    # Answer checksum
    ans_hash = recieve_tup[1]

    # Error checking hash of answer cyphertext
    if hashlib.sha256(ans_cypher).hexdigest() != ans_hash:
        print('ERROR: The answer hash does not match the given answer.')
        s.close()
        exit()

    # Decrypting the answer
    Abytes = f_obj.decrypt(ans_cypher)

    # Converting the answer to a string
    Atext = Abytes.decode("utf-8")

    print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 07] Decrypt: Using Key: " + str(key) + " | Plain text: " + Atext)

    # If service instance provides API key authentication
    service = TextToSpeechV1(url = watsonURL, iam_apikey= watsonDevKey)


    with open('AAudio.mp3', 'wb') as audio_file:
        audio_file.write(
            service.synthesize(
                Atext,
                voice='en-US_MichaelV3Voice',
                accept='audio/mp3'        
            ).get_result().content)
        audio_file.close()		
        
    with open('AAudio.mp3') as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        mixer.init()
        mixer.music.load(m)

        print("[" + str(datetime.datetime.now().time()) + "]" + "[Checkpoint 08] Speaking Answer: " + Atext)
        
        mixer.music.play()
        
        while mixer.music.get_busy():
            time.sleep(1)
        mixer.music.stop()
        mixer.quit()

        m.close()
    s.close()
