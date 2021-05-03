import os
from time import sleep, time

# This file stores all the shared data needed for updating data
# across the network.

# Messages will come in from other nodes, and all they will
# be stored in a queue.

# If any a proposed changed that comes in has an earlier timestamp than 
# we already have saved locally for a given file, then we just disregard
# the message.

# If a delete update has been sent, then we simply delete the file named
# in the message if we have it locally.

def get_status_code(status):
	if status == "new":
		return "0"
	elif status == "update":
		return "1"
	elif status == "deleted":
		return "2"
	else:
		return "3"

def get_external_change_identifier(item, status_code, time):
	status = ""
	if status_code == "0":
		status = "new"
	elif status_code == "1":
		status = "update"
	elif status_code == "2":
		status = "deleted"

	return (item.strip(), status, float(time))


def get_local_change_identifier(item, status):
	if status == "deleted":
		# Since we cannot get the last modified 
		return (item, status, time())
	else:
		return (item, status, os.path.getmtime("./data/"+item))


# The queue of changes is where we'll store the changes that we have detected to the 
# p2pnetwork/data folder. All of these change's contents will be packaged and sent to all the other
# peers
to_be_sent_queue = []

# Whenever we recieve a change, we store it here
received_queue = []

# Whenever we update the p2pnetwork/data folder via a recieved update, we will detect
# the change in the thread that monitors the folder. To prevent these changes being resent
# over the network, we will store every received update in a set the moment it has been executed.
# Then, any time we detect an update, we will only put it in the queue of changes if it is not
# in the set of known changes.
known_changes = set()


NUM_OF_PEERS = 0

# Here we have a semaphore that we use to ensure that each sender has sent a message before we 
# remove that message from the top of the queue
sender_semaphore = 0

def register_sender():
	global NUM_OF_PEERS
	global sender_semaphore
	NUM_OF_PEERS += 1
	sender_semaphore += 1


def deregsiter_sender():
	global NUM_OF_PEERS
	NUM_OF_PEERS -= 1

def signal_semaphore():
	global sender_semaphore
	sender_semaphore -= 1

	if sender_semaphore == 0:
		global to_be_sent_queue
		to_be_sent_queue.pop(0)
		sender_semaphore = NUM_OF_PEERS

# We want to have mutual exclusion between sending and receiving. To explain,
# think of the following example:
#	- A change is recieved, and we go to implement it. While implementing the change,
#	  we detect a change has occured, and send a message based on a partial update. That
# 	  partial update becomes the "newest version" of the file, and then the udpdate ends
#	  up vanishing.
# Ideally, when we receive a change, we want to make sure that the change is implemented
# before we send out any new updates of changed files. The reality is that we will receive
# a change to the data folder, we have to edit the file to change state. However, these
# updates should not be transmitted becuase they are not user updates.


# The mutual exclusion algorithm I decided to implement was Peterson's Algorithm, becuase it
# is fairly simple and works in this case because there are only two logical entities (the senders
# and the receivers) that need mutual exclusion on the shared data (the /p2pnetwork/data folder)

# The first flag will represent the receiver threads, and the second flag will represent the
# sender threads
flags = [False, False]
mutex_turn = 0


def request_executer():
	global flags
	global mutex_turn

	while True:
		# To implement Peterson's Algorithm for mutual exlcusion, we first need to set our flag to
		# true and give the turn to the sending threads
		if len(received_queue) > 0:
			flags[0] = True
			mutex_turn = 1
			while flags[1] == True and mutex_turn == 1:
				sleep(1)

		while len(received_queue) > 0:
			# If there are messages that we have received that we still need to execute, they get handled
			# after this if statement
			next_message = received_queue.pop(0)
			next_message_change_identifier = next_message[0]
			file_contents = next_message[1]
			# If the message is not a delete message, then simply write the contents of the file
			if next_message_change_identifier[1] == "deleted":
				os.remove("./data/"+next_message_change_identifier[0])
			else:
				with open("./data/"+next_message_change_identifier[0], "wb") as f:
					f.write(file_contents)
				# These lines of code give read, write, and execute permission to everyone
				os.chmod("./data/"+next_message_change_identifier[0], 0o777)
			# After the change is executed, we add the change identifier to the set of known changes
			known_changes.add(get_local_change_identifier(next_message_change_identifier[0],next_message_change_identifier[1]))

		# Since we know that a known change can only happen while the request_executer has mutex control,
		# we know that it is okay to simply wait until the end of request_executer's turn to clear out all 
		# known changes from the list of changes to be sent.

		# At this point in the code, for each known change, there are a few states it can be in:
		# 1. The known change has been detected by the change detector
		# 2. A known change has not been detected by the change detector

		# This will solve for all known changes in scenario 2. If scenario 1 occurs, then it
		# it will be handled by the change detector when it attempts to add the change
		to_be_sent_queue_copy = []
		for message in to_be_sent_queue:
			to_be_sent_queue_copy.append(message)

		for message in to_be_sent_queue_copy:
			if message in known_changes:
				to_be_sent_queue.remove(message)

		known_changes.clear()
		flags[0] = False

		sleep(1)


def to_be_sent_manager():
	global flags
	global mutex_turn

	while True:
		# To implement Peterson's Algorithm for mutual exlcusion, we first need to set our flag to
		# true and give the turn to the sending threads
		if len(to_be_sent_queue) > 0:
			flags[1] = True
			mutex_turn = 0
			while flags[0] == True and mutex_turn == 0:
				sleep(1)

		while len(to_be_sent_queue) > 0:
			sleep(1)

		flags[1] = False

		sleep(1)

