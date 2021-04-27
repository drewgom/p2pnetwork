from scapy.all import srp, ARP, Ether

# In order for our program to work, we need to have a way to find what
# other machines on the local network are also running our file sharing
# app. The find_peers function works by returning the IP address of any
# computer running our app.

def scan_network():

	# The first step in this process is to get a list of the devices on
	# the network.


	# We want to broadcast our ARP message to every device on the network.
	# This can be done with MAC address ff:ff:ff:ff:ff:ff

	# The srp function in scapy allows us to send packets and receive the response
	# from what we sent. In scapy, we use / to stack messages of different
	# protocols. Here, on the data link layer we used Ether, and we want our
	# Ether messsage to contain the contents of an ARP message that tries to
	# find the MAC address for all the devices on our network (which we can
	# access via the IPs 192.168.1.1 - 192.168.1.255). This function call
	# simply does that.
	answered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.0/24"), timeout=3)[0]

	print("IP" + " "*18+"MAC")

	ip_arr = []
	mac_arr = []
	for sent, received in answered:
		ip_arr.append(received.psrc)
		mac_arr.append(received.hwsrc)

	return ip_arr, mac_arr