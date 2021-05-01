# This file stores all the shared data needed for updating data
# across the network.

# Messages will come in from other nodes, and all they will
# be stored in a queue.

# If any a proposed changed that comes in has an earlier timestamp than 
# we already have saved locally for a given file, then we just disregard
# the message.

# If a delete update has been sent, then we simply delete the file named
# in the message if we have it locally.

# For any update or new file, we want to 


NUM_OF_PEERS = 0

# The queue of changes is where we'll store the changes that we have detected to the 
# p2pnetwork/data folder. All of these change's contents will be packaged and sent to all the other
# peers
queue_of_changes = []

# Whenever we update the p2pnetwork/data folder via a recieved update, we will detect
# the change in the thread that monitors the folder. To prevent these changes being resent
# over the network, we will store every received update in a set the moment it has been executed.
# Then, any time we detect an update, we will only put it in the queue of changes if it is not
# in the set of known changes.
known_changes = set()


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
