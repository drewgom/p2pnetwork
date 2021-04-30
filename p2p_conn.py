import socket
import threading

# Although this connection is peer to peer, I found it would be easiest to have
# two streams of data connected between any two nodes: one data stream that sends data out
# from node A to node B, which behaves as if node A is a "client" and node B is a "server",
# and one data stream that sends data out from node B to node A, which behaves as if node B
# is a "client" and node A is a "server". This way, a "client" socket will always attach to
# all servers, and we assume that every client will do so in a timely manner, which gives us
# a gauranteed connection within a certain amount of time. I was having trouble thinking of 
# a single connection that could be estbalished only by one end, when both nodes could potentially
# try to establish a connection on the same port at the same time.

# to try and minimize confusion, I called the "client" socket that sends information out of a
# node the "sender", and the "server" socket that recieves information the "receiver".

# All "sender" sockets for a node are bound to port 2194, and all "receiver" sockets for a node
# are bound to port 2195. These were simply random selections that were not registered with the IANA.

SEND_PORT = 2194
REC_PORT = 2195

# The line of code below allows us to get our local IP address
CURRENT_NODE_IP = ""


def start_receiver(operating_system):
	# Here we create a socket that will use IPv4 for network communcation, and TCP for transport
	# layer communication
	if operating_system == "0":
		# If this option is set, then we are using macOS
		CURRENT_NODE_IP = socket.gethostbyname(socket.getfqdn())
	elif operating_system == "1":
		# If this option is set, then we are using a Raspbian machine
		CURRENT_NODE_IP = socket.gethostbyname(socket.gethostname() + ".local")
	else:
		print("Could not resolve OS")
		exit()
	reciever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	reciever_socket.bind((CURRENT_NODE_IP, REC_PORT))
	reciever_socket.listen()
	print("Started - IP = " + str(CURRENT_NODE_IP) + ", PORT = " + str(REC_PORT))
	while True:
		connection, address = reciever_socket.accept()
		# Here, we start a thread that will receive all the messages for the communication
		# between the two threads


def start_sender(sender_ip):
	sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sender_socket.connect((sender_ip, REC_PORT))
	# Here, we start a thread that will send all the messages for the communication
	# between the two threads
	print("Connected")


'''
def package_change():
	# Here, we simply package up the changed file in to the correct format to
	# be sent over the network


def unpackage_change():


def recieve_change():


def send_change():
'''
