import socket
import threading
import queue_manager
import os
import time

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

DISCOVERY_PORT = 2194
REC_PORT = 2195

CURRENT_NODE_IP = ""

HEADER_FILE_NAME_SIZE = 64
HEADER_UPDATE_TYPE_SIZE = 1
HEADER_UPDATE_TIMESTAMP = 32
HEADER_FILE_SIZE = 16

HEADER_SIZE = HEADER_FILE_NAME_SIZE + HEADER_UPDATE_TYPE_SIZE + HEADER_UPDATE_TIMESTAMP + HEADER_FILE_SIZE

def get_ip(operating_system):
	ip = ""
	if operating_system == "0":
		# If this option is set, then we are using macOS
		# CURRENT_NODE_IP = socket.gethostbyname(socket.getfqdn())
		ip = "192.168.1.7"
	elif operating_system == "1":
		# If this option is set, then we are using a Raspbian machine
		ip = socket.gethostbyname(socket.gethostname() + ".local")
	else:
		print("Could not resolve OS")
		exit()

	return ip

def discovery_receiver(operating_system):
	CURRENT_NODE_IP = get_ip(operating_system)
	discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	discovery_socket.bind((CURRENT_NODE_IP, DISCOVERY_PORT))
	discovery_socket.listen()
	print("Started - IP = " + str(CURRENT_NODE_IP) + ", PORT = " + str(DISCOVERY_PORT))
	while True:
		connection, address = discovery_socket.accept()
	

def start_receiver(operating_system):
	CURRENT_NODE_IP = get_ip(operating_system)
	reciever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	reciever_socket.bind((CURRENT_NODE_IP, REC_PORT))
	reciever_socket.listen()
	print("Started - IP = " + str(CURRENT_NODE_IP) + ", PORT = " + str(REC_PORT))
	request_executer_thread = threading.Thread(target=queue_manager.request_executer, args=())
	request_executer_thread.start()
	while True:
		connection, address = reciever_socket.accept()
		# Here, we start a thread that will receive all the messages for the communication
		# between the two threads
		recieve_change(connection, address)


def start_sender(sender_ip):
	sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	to_be_sent_manager_thread = threading.Thread(target=queue_manager.to_be_sent_manager, args=())
	to_be_sent_manager_thread.start()
	sender_socket.connect((sender_ip, REC_PORT))
	# Here, we start a thread that will send all the messages for the communication
	# between the two threads
	print("CONNECTION MADE ON " + str(sender_ip) + ", PORT " + str(REC_PORT))
	send_change_thread = threading.Thread(target=send_change, args=(sender_socket,))
	send_change_thread.start()


def recieve_change(connection, address):
	print("in recieve_change")
	currently_connected = True
	while currently_connected:
		# At the start of any message we receive is the header. The header will contain:
		#	1. The file name (padded to always be a length of 64 characters)
		#	2. The type of update that occurred (always is a single character)
		#	3. The timestamp of the update (padded to always be a length of 32 characters)
		#	4. The size of the file (padded to always be length 16)
		# After the header, we will simply receive the contents of the file
		header = connection.recv(HEADER_SIZE).decode("utf8")
		if header:
			print("In header")
			# First we store the header information
			file_name = header[:64]
			print("file name is " + file_name)
			update_type = header[64]
			update_timestamp = header[65:97]
			file_size = header[97:]
			# Once we have the header info, we recieve the file data, and queue
			# it to be decoded
			file_contents = connection.recv(int(file_size))
			change_identifier = queue_manager.get_external_change_identifier(file_name, update_type, update_timestamp)
			print(file_name)
			print(update_type)
			print(update_timestamp)
			print(file_size)
			queue_manager.received_queue.append((change_identifier, file_contents))


	connection.close()

def send_change(sending_socket):
	# If a sender runs and the top of the queue is still the previous message that was sent by this sender,
	# then we know that we should essentially busy wait
	previous_message = None
	queue_manager.register_sender()

	currently_connected = True
	while currently_connected:
		# If the queue is empty or if we already sent the message that's at the top of the queue, we simply wait
		print("QUEUE OF CHANGES FROM SENDER")
		print(queue_manager.to_be_sent_queue)

		while len(queue_manager.to_be_sent_queue) == 0 or previous_message == queue_manager.to_be_sent_queue[0]:
			time.sleep(2)

		# Once we have finished sending the message, we'll signal that we are done to the semaphore.
		change_identifier = queue_manager.to_be_sent_queue[0]
		# First we add in the header
		header = change_identifier[0].encode("utf8")
		header += b' ' * (HEADER_FILE_NAME_SIZE - len(header))
		# Next, we add in the single value for the status
		header += queue_manager.get_status_code(change_identifier[1]).encode("utf8")
		# Currently the line below should do nothing, but it is still good to have incase the size of this were to change
		header += b' ' * (HEADER_FILE_NAME_SIZE+HEADER_UPDATE_TYPE_SIZE - len(header))
		# After that, we add the timestamp
		header += str(change_identifier[2]).encode("utf8")
		header += b' ' * (HEADER_FILE_NAME_SIZE+HEADER_UPDATE_TYPE_SIZE+HEADER_UPDATE_TIMESTAMP - len(header))
		# Finally we add the size. This will be a size of 1 if it is a delete command, and the size of the
		# file in bytes otherwise
		if change_identifier[1] == "deleted":
			header += "1".encode("utf8")
		else:
			header += str(os.path.getsize("./data/"+change_identifier[0])).encode("utf8")
		
		header += b' ' * (HEADER_FILE_NAME_SIZE+HEADER_UPDATE_TYPE_SIZE+HEADER_UPDATE_TIMESTAMP+HEADER_FILE_SIZE - len(header))

		# Once we have gotten the header, we need to get the contents of the file into a variable and encode it

		file_data = "0".encode("utf8")
		# If we are sending a new file or an updated file, we want to get the file's data and turn that in to
		# the file_data variable
		
		if change_identifier[1] != "deleted":
			with open("./data/"+change_identifier[0], "rb") as f:
				file_data = f.read()
		


		# At this point, all that's left is that we send the header and then the other message
		print("about to send")
		print(header)

		sending_socket.sendall(header)
		print("sent header")
		sending_socket.sendall(file_data)
		print("sent file data")

		#Once we have sent the messages, we will signal that we have sent the message, and that
		previous_message = change_identifier
		queue_manager.signal_semaphore()

	queue_manager.deregister_sender()