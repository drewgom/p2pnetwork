from os import path, mkdir, remove, listdir, rmdir, chmod
import shutil
from hashlib import md5
from time import time, sleep
import queue_manager

TIME_INTERVAL_BETWEEN_SCANS = 1

# This function will be used to verify that p2pnetwork/data exists
def verify_directory():
	# If a file already exists that has the path we need, then delete it
	if path.isfile("./data"):
		remove("./data")

	# Since there now cannot be a file by the name of the data directory,
	# we will make the data directory if it doesnt exist
	if path.exists("./data"):
		shutil.rmtree("./data")
	mkdir("./data")
	chmod("./data/", 0o777)


def detect_change():
	# This code will detect if the p2pnetwork/data repository ever changes.
	# If it does, then we will handle that change by sending the changed file
	# name to be handled.

	# Here, we keep a cache of all the previous metadata about the the folder.
	# We will constantly be checking to see if the contents changed. If they did,
	# Then we need to send the changed files
	previous_metadata = {}
	next_metadata = {}
	# For our purposes, we know that we need to send an update if:
	# 	1. A file as been deleted
	#	2. A file as been added
	#	3. The contents of a file have changed

	files_who_have_changed_state = []

	while True:
		for item in listdir("./data"):
			if not item.startswith("."):
				# We know that every item that we iterate over needs to be stored in the next
				# metadata - because if we see it currently then by definition it is
				# part of the current state. So, we start by adding the file's name and
				# hash to the next metadata

				md5_hasher = md5()
				with open("./data/"+item, 'rb') as curr_file:
					while True:
						data = curr_file.read(1024)
						if not data:
							break
						md5_hasher.update(data)

				item_hash = md5_hasher.hexdigest()
				next_metadata[item] = item_hash


				# not in previous? okay, then send
				# in previous? then okay, is the hash different? then send

				# If a file was not in the previous metadata, then we know that this file
				# is new, thus an update must be sent

				if item not in previous_metadata.keys():
					change_identifier = queue_manager.get_local_change_identifier(item, "new")
					if change_identifier not in queue_manager.known_changes:
						files_who_have_changed_state.append(change_identifier)
					else:
						queue_manager.known_changes.remove(change_identifier)
				# If the new file was in the previous metadata, but the file's hash changed,
				# then the contents of the file have changed. If that's the case, then we need
				# to also need to report that that file has changed
				elif previous_metadata[item] != item_hash:
					change_identifier = queue_manager.get_local_change_identifier(item, "update")
					if change_identifier not in queue_manager.known_changes:
						files_who_have_changed_state.append(change_identifier)
					else:
						queue_manager.known_changes.remove(change_identifier)


		# Once we have iterated over every file in the directory and put it in to
		# the new metadata, then we need to find all the elements in the previous metatdata
		# that are not in the current one. Those are the files that have been deleted.

		deleted_files = previous_metadata.keys() - next_metadata.keys()
		for item in deleted_files:
				change_identifier = queue_manager.get_local_change_identifier(item, "deleted")
				known_changes_list = [(element[0], element[2]) for element in queue_manager.known_changes]
				known_changes_list_of_names = [element[0] for element in known_changes_list]

				if item not in known_changes_list_of_names:
					files_who_have_changed_state.append(change_identifier)
				else:
					instances = [identifier for identifier in queue_manager.known_changes if identifier[0] == item]
					for instance in instances:
						queue_manager.known_changes.remove(instance)


		# Once we have all the changes, we need to that data off to the queue in order to send
		# the data off

		for id in files_who_have_changed_state:
			queue_manager.to_be_sent_queue.append(id)

		print("FILES WHO HAVE CHANGED STATE")
		print(files_who_have_changed_state)


		# Once we have sent the messages, we need to prepare for the next scan


		previous_metadata.clear()
		for item in next_metadata:
			previous_metadata[item] = next_metadata[item]			
		next_metadata.clear()

		files_who_have_changed_state.clear()


		print("QUEUE OF CHANGES FROM FOLDER MONITOR")
		print(queue_manager.to_be_sent_queue)

		print("KNOWN CHANGES")
		print(queue_manager.known_changes)

		sleep(TIME_INTERVAL_BETWEEN_SCANS)