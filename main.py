import net_scan
import p2p_conn
import sys


if sys.argv[1] == 'sender':
	ip_arr = []
	ip_arr.append("192.168.1.7")
	print("starting port scan")
	result = net_scan.scan_ports(ip_arr, 2195)
	print("port scan completed")
	for res in result:
		p2p_conn.start_sender(res)
elif sys.argv[1] == 'receiver':
	p2p_conn.start_receiver()
else:
	print('Unknown argument')