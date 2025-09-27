# NetWatcher - Outil de surveillance réseau minimal

## But
Outil simple qui capture le trafic et détecte comportements anormaux (transferts massifs, balayage ports, connexions inhabituelles).

## Requirements
- Python 3.9+
- pip install -r requirements.txt
- Sur Windows : Npcap (https://nmap.org/npcap/) installé
- Sur Linux : droits root pour sniff (ou exécuter avec sudo)

## Lancement
1. Modifier `config.yaml` : choisir `iface` (ex: "Software Loopback Interface 1" pour test local).
2. `python main.py`  (ou `sudo python3 main.py`)

## Tests
- Mode loopback : utiliser `iface: "Software Loopback Interface 1"` et simuler du trafic local (exemples Scapy ci-dessous).
- Simulation en local (exemples) :
  ```python
  from scapy.all import IP, TCP, send
  for i in range(300):
      send(IP(dst="127.0.0.1")/TCP(dport=80, flags="S"), verbose=0)
