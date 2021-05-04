# p2pnetwork

## What is This
 This project is a peer-to-peer application that lets users synchronize the state a directory over a local area network. In many ways, this application operates from the users perspective like a decentralized version of Dropbox, where all the computers running the program find each other automatically.

 I created this project for my Distributed Systems class (CECS 327) at CSU, Long Beach.

## Design
There are a few design issues that made this assignment difficult to implement, which ultimately made me chose the design I did. I'll try to explain my logic for the design of this program in two seperate segments: The design decisions pertaining to networking, and those that pertain to the application's software once the connections already exist

### Networking
For the networking components, I have a network scanner that simply uses ARP to get all the devices on my LAN. Although ARP is often used to get the MAC address for a given IP, I instead used it to ping every device of any MAC address, which returned to me both the MAC address *and* the IP address, and I just save the IP addresses. From there, I have a function that simply pings on port 2194 and tries to see if anyone has that port open. If they do, then that means that they are also runnign this program. I chose that port because it's not current registered with the IANA, so I presumed that there would not be other traffic on my network using that port. 

The reason I have a seperate port only for establishing connections is that the connection messages when being sent on the main port (2195) were not processing correctly.

Since the discovery of new nodes happens automatically, I had trouble resolving what should happen when two nodes simultaneously tried to connect to each other. Eventually, I realized that it might be the most straightforward to simply let both nodes discover each other, and then just use both of the two connections that get created. I then decided that the connection made from Node A to Node B would be to only send messages from A to B - not any messages from B to A. The way to make this work in the application is to then have every node create a new thread for sending messages *after* we discover a node that we know is in fact running the program.

The port for all network traffic related to the actual sending and receiving of updates for the app was 2195. Each node starts a thread that listens at port 2195 for incoming messages. So, each node can have many sending threads (all of which are created immediately after we discover another peer on port 2194), and then one receiver that simply listens to each message.

### Application
The core of this application is detecting when a change happens on a certain directory, and then making that change happen on every directory that's running the app. This can essentially be broken in to 3 components:
1. Detecting changes on the directory
2. Sending the detected changes to all other peers
3. Receiving and executing changes that happen on other peers, in order to make our node more up to date.

To detect the changes on the directory, I have a thread that scans once every second to get the state of the directory (name of files, their timestamps, their hash, etc), and compares it to the state of one second ago. There are 3 key actions that can happen:
1. A file is in the directory that wasnt there one second ago
2. A file that was there one second ago isn't there anymore
3. A file that was there one second ago has different contents than it did a second ago

The change detector, whenever any of thse things happens, knows a change has been made. When a change is made, then that means we need peers to send out the change. This is done by having a queue that is shared between all the sending threads. When the change detector detects the directory has changed, it puts a message in the queue that the senders shares. The senders will constantly be scanning to see if they have sent the message at the top of the queue - if they have, then they just wait. If they havent, then they send it. Once every sender sends a change from the queue, it gets removed from the queue.

So far, I have left out one big component - what happens when we receive a message and update the directory. Won't the change detector thread detect that as a change, and then retransmit a message that it recieved? The answer is that yes, under the details described so far, this would happen. That's why I created a queue of received messsages, and made it mutually exclusive with the senders. 

The way the queue of received messsages works is that when the receiver gets a message, it puts it in the queue, but doesn't actually execute the message's contents yet. Then, from here, there's mutual exclusion between the sending queue and the receiving queue, and that works because then before the sending queue gets time to run, we verfiy that it won't send any updates that were actually received.

Here's a diagram of how the application works:
![Test](https://github.com/drewgom/p2pnetwork/blob/master/diagram.png?raw=True)


## How to Run
In order to run this, simply use Python 3 on your command line. This is essential, becuase this program takes in command line arguments. Currently, there are two command line arguments 
1. code for the operating system being used to run the program
2. code for whether you want to run the program in test mode or not

### Passing in Operating System as an Argument
#### Why do I need to do this?
The two operating systems that are supported for this program are Raspbian and macOS, because those are the two operating systems that were used for development. These two operating systems resolve their local IP addresses differently, which creates problems in the `start_receiver()` function in`p2p_conn.py`. The current solution is the only one that I know of that will consistently return the LAN IP for both operating systems.
#### How do I do this?
For macOS, pass in `0` in the first command-line argument (`python3 main.py 0`)
For Raspbian, pass in `1` in the first command-line argument (`python3 main.py 1`)

### Passing in the Mode
#### Why do I need to do this?
When I was testing the project, it was faster for me to hard code in the results of a network scan, because this would often take a few seconds to do. If you would like to hard code the IP addresses you are dealing with and test that way, feel free, however you will probably almost always want to run this in the non-testing more
#### How do I do this?
For regular operation, pass in `0` in the second command-line argument (`python3 main.py *os* 0`)
To run in test mode, pass in `1` in the second command-line argument (`python3 main.py *os* 1`)


## Tools
- I used the package [Scapy](https://scapy.net) to write the algorithm that can detect what other devices are on my network
- I used BSD sockets to establish connections between nodes because they are implemented in [Python's socket library](https://docs.python.org/3/library/socket.html), and so I figured it would be a library that had a lot of documentation already
- I used the threading tools that Python supplies in order to have multiple of these resources running concurrently and constantly


## Resources Used
- [How to create your own decentralized file sharing service using python](https://medium.com/@amannagpal4/how-to-create-your-own-decentralized-file-sharing-service-using-python-2e00005bdc4a)
- [Writing a Network Scanner using Python](https://levelup.gitconnected.com/writing-a-network-scanner-using-python-a41273baf1e2)
- [Build your own tools - Scapy Documentation](https://scapy.readthedocs.io/en/latest/extending.html)
- [socket.py Documentation](https://docs.python.org/3/library/socket.html)
- [Python Socket Programming Tutorial](https://youtu.be/3QiPPX-KeSc)
- [Python Threading Tutorial](https://realpython.com/intro-to-python-threading/)
- [Peterson's Algorithm](https://en.wikipedia.org/wiki/Peterson's_algorithm)