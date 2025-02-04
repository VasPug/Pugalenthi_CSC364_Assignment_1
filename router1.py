import util
import socket
import sys
import time
import os
import glob
from threading import Thread

# Main Program

# 0. Remove any output files in the output directory
# (this just prevents you from having to manually delete the output files before each run).
files = glob.glob('./output/*')
for f in files:
    os.remove(f)

# 1. Connect to the appropriate sending ports (based on the network topology diagram).
router2_socket = util.create_socket('127.0.0.1', 8002)
router4_socket = util.create_socket('127.0.0.1', 8004)

# 2. Read in and store the forwarding table.
forwarding_table = util.read_csv("input/router_1_table.csv")
# 3. Store the default gateway port.
default_gateway_port = util.find_default_gateway(forwarding_table)
# 4. Generate a new forwarding table that includes the IP ranges for matching against destination IPS.

print(forwarding_table)
print("--------------------------------\n")
forwarding_table_with_range = util.generate_forwarding_table_with_range(forwarding_table)
print(forwarding_table_with_range)
print("------\n")
# 5. Read in and store the packets.
packets_table = util.read_csv("input/packets.csv")


# 6. For each packet,
for packet in packets_table:
    # 7. Store the source IP, destination IP, payload, and TTL.
    sourceIP = packet[0]
    destinationIP = packet[1]
    payload = packet[2]
    ttl = int(packet[3])
    
    # 8. Decrement the TTL by 1 and construct a new packet with the new TTL.
    new_ttl = ttl - 1
    new_packet = sourceIP + "," + destinationIP + "," + payload + "," + str(new_ttl)


    # 9. Convert the destination IP into an integer for comparison purposes.
    destinationIP_int = util.ip_to_bin(destinationIP)
    

    # 9. Find the appropriate sending port to forward this new packet to.
    sending_port = None
    for row in forwarding_table_with_range:
        min_ip = row[0]
        max_ip = row[1]
        if min_ip <= destinationIP_int <= max_ip:
            sending_port = row[2]
            print("Port found")
            break
    
    # 10. If no port is found, then set the sending port to the default port.
    if sending_port is None:
        print("No port found")
        sending_port = default_gateway_port
    
    # 11. Either
    # (a) send the new packet to the appropriate port (and append it to sent_by_router_1.txt),
    # (b) append the payload to out_router_1.txt without forwarding because this router is the last hop, or
    # (c) append the new packet to discarded_by_router_1.txt and do not forward the new packet
    print(sending_port)
    if sending_port == "8002" and new_ttl > 0:
        print("sending packet", new_packet, "to Router 2")
        router2_socket.send(new_packet.encode())
        util.write_to_file("./output/sent_by_router_1.txt", new_packet, "2")
    elif sending_port == "8004" and new_ttl > 0:
        print("sending packet", new_packet, "to Router 4")
        router4_socket.send(new_packet.encode())
        util.write_to_file("./output/sent_by_router_1.txt", new_packet,"4")
    elif sending_port == "127.0.0.1":
        print("OUT:", payload)
        util.write_to_file("./output/out_router_1.txt", payload)
    else:
        util.write_to_file("./output/discarded_by_router_1.txt", new_packet)

    
    # Sleep for some time before sending the next packet (for debugging purposes)
    time.sleep(1)