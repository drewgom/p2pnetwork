import os
from time import sleep

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
	NUM_OF_PEERS += 1


def deregsiter_sender():
	global NUM_OF_PEERS
	NUM_OF_PEERS -= 1

def signal_semaphore():
	sender_semaphore -= 1

	if sender_semaphore == 0:
		global to_be_sent_queue
		to_be_sent_queue.pop()
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


mutex_locks = [False, False]
mutex_turn = 1





def request_executer():
	while True:
		# If there are messages that we have received that we still need to execute, they get handled
		# after this if statement
		if len(received_queue) > 0:
			next_message = received_queue.pop(0)
			next_message_change_identifier = next_message[0]
			file_contents = next_message[1]
			# If the message is not a delete message, then simply write the contents of the file
			testing_path = "text2.txt"
			print("would operate on " + next_message_change_identifier[0] + ", instead on " + testing_path)
			if next_message_change_identifier[1] == "deleted":
				os.remove("./data/"+next_message_change_identifier[0])
			else:
				with open("./data/"+next_message_change_identifier[0], "wb") as f:
					f.write(file_contents)
			


			# After the change is executed, we add the change identifier to the set of known changes
			known_changes.add(get_local_change_identifier(next_message_change_identifier[0],next_message_change_identifier[1]))
		sleep(1)