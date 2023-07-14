# NetApps
VT Network Applications Class - Team 12 - Eamon, Kulneet, Brandon

Server Initialization: to start the server enter "python3 server.py -sp <SERVER_PORT> -z <SOCKET_SIZE>" here SERVER_PORT and SOCKET_SIZE are specified by the user

Client Initilization: to start the client enter "python3 client.py -sip <SERVER_IP> -sp <SERVER_PORT> -z <SOCKET_SIZE>" where the SERVER_IP, SERVER_PORT, and SOCKET_SIZE are the same values frtom the server

Server initialization should be done first as the server checkpoints print out the servers ip adress

Extra Libraries used:
Tweepy: Was used top open a twitter stream which filtered results using our team specific hashtag.

Datetime: Was used to pring out the timestamps required for the checkpoint statements.

Ibm_watson: Generated a .mp3 file containing the translated audio.

Time: Was used to allow the program to pause when waiting for twitter input or audio completion.

Mmap: Was used to properly open and close the .mp3 files for reading and writing.

Hashlib: Was used to generate the checksum to verify proper transmission over the connection.

Fernet: Was used to encrypt the questions and answers.

Pickel: Was used to serialize the messages before sending them to and from the server.

Contextlib: Was used to suppres the self advertising messages of Pygame.

Pygame: Was used to play the generated .mp3 files automatically.

Wolframalpha: Was used to retrieve the answer to our question.

Netifaces: Was used to retrieve the ip address from wlan0 on the server
