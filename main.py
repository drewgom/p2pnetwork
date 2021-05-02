import net_scan
import p2p_conn
import folder_monitor
import sys
import threading

def main():
	if sys.argv[1] == 'sender':
		# ip_arr = net_scan.scan_network()
		ip_arr = []
		ip_arr.append("192.168.1.98")
		ip_arr.sort()
		print("starting port scan")
		result = net_scan.scan_ports(ip_arr, p2p_conn.DISCOVERY_PORT)
		print("port scan completed")
		change_detector_thread = threading.Thread(target=folder_monitor.detect_change, args=())
		change_detector_thread.start()
		for res in result:
			print("starting sender")
			p2p_conn.start_sender(res)
	elif sys.argv[1] == 'receiver':
		discovery_thread = threading.Thread(target=p2p_conn.disovery_receiver, args=(sys.argv[2]))
		discovery_thread.start()
		p2p_conn.start_receiver(sys.argv[2])
	elif sys.argv[1] == 'scan':
		ip_arr = net_scan.scan_network()
		ip_arr.sort()
		for ip in ip_arr:
			print(ip)
	else:
		print('Unknown argument')



if __name__ == "__main__":
    #folder_monitor.verify_directory()
    #p2p_conn.send_change()
    main()