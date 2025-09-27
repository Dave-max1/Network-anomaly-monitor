"""
Simulate multiple network behaviors for testing detectors.
RUN ONLY IN A LAB / LOOPBACK / VM HOST-ONLY NETWORK.
"""
from scapy.all import IP, TCP, UDP, ICMP, Raw, send, sr1, Ether, ARP, sendp
import time
import random

def syn_flood(dst="127.0.0.1", dport=8080, n=300, src_pool_prefix="10.0.0."):
    """SYN flood: many SYNs from many fake sources."""
    print(f"[SYN FLOOD] target={dst}:{dport}, packets={n}")
    for i in range(n):
        src = f"{src_pool_prefix}{(i % 50) + 10}"
        pkt = IP(src=src, dst=dst)/TCP(dport=dport, flags="S")
        send(pkt, verbose=0)
    print("[SYN FLOOD] done")

def big_data_transfer(dst="127.0.0.1", dport=80, n=50, payload_size=20000, src="10.0.1.5"):
    """Big packets to simulate massive upload/download per source."""
    print(f"[BIG TRANSFER] target={dst}:{dport}, pkts={n}, payload={payload_size}")
    for i in range(n):
        pkt = IP(src=src, dst=dst)/TCP(dport=dport, flags="PA")/Raw(b"A"*payload_size)
        send(pkt, verbose=0)
    print("[BIG TRANSFER] done")





if __name__ == "__main__":
    # Choose which simulations to run (safe defaults to loopback)
    DST = "127.0.0.1"
    # run a sequence with small pauses
    syn_flood(dst=DST, dport=8080, n=300)
    time.sleep(1)
    big_data_transfer(dst=DST, dport=80, n=50, payload_size=20000)
    time.sleep(1)

