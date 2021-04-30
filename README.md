# p2pnetwork

A peer-to-peer network that I created for my Distributed Systems class.

## How to Run
In order to run this, simply use Python 3 on your command line. This is essential, becuase this program takes in command line arguments. Currently, the frist and only command line argument needed is the name or code of the operating system being used to run the program.
### Passing in Operating System as an Argument
#### Why do I need to do this?
The two operating systems that are supported for this program are Raspbian and macOS, because those are the two operating systems that were used for development. These two operating systems resolve their local IP addresses differently, which creates problems in the `start_receiver()` function in`p2p_conn.py`. The current solution is the only one that I know of that will consistently return the LAN IP for both operating systems.
#### How do I do this?
For macOS, please state pass in `0` in the first command-line argument (`python3 main.py 0`)
For Raspbian, please state pass in `1` in the first command-line argument (`python3 main.py 1`)

## Design

## Tools
- I used the package [Scapy](https://scapy.net) to write an algorithm that can detect what other devices are on my network
- I used BSD sockets to establish connections between nodes because they are implemented in [Python's socket library](https://docs.python.org/3/library/socket.html), and so I figured it would be a library that had a lot of documentation already


## Resources Used
- [How to create your own decentralized file sharing service using python](https://medium.com/@amannagpal4/how-to-create-your-own-decentralized-file-sharing-service-using-python-2e00005bdc4a)
- [Writing a Network Scanner using Python](https://levelup.gitconnected.com/writing-a-network-scanner-using-python-a41273baf1e2)
- [Build your own tools - Scapy Documentation](https://scapy.readthedocs.io/en/latest/extending.html)
- [socket.py Documentation](https://docs.python.org/3/library/socket.html)
- [Python Socket Programming Tutorial](https://youtu.be/3QiPPX-KeSc)
