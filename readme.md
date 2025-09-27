# NetWatcher - Outil de surveillance réseau minimal

## But
Outil simple qui capture le trafic et détecte comportements anormaux (transferts massifs, balayage ports, connexions inhabituelles).

## Requirements
- Python 3.9+
- pip install -r requirements.txt
- Sur Windows : Npcap (https://nmap.org/npcap/) installé
- Sur Linux : droits root pour sniff (ou exécuter avec sudo)

## Lancement
- Se rassurer d'être positionné dans le dossier `src`
1. Modifier `config.yaml` : choisir `iface` (ex: "Software Loopback Interface 1" pour test local).
2. Configurer les alerts par mail ou par webhook dans le config.yaml
3. `python main.py`  (ou `sudo python3 main.py`)

## Tests
- Simulation en local (exemples) :
  ```python
  from scapy.all import IP, TCP, send
  for i in range(300):
      send(IP(dst="127.0.0.1")/TCP(dport=80, flags="S"), verbose=0)
- Lancer une simulation via `python attack.py`

## Lancer avec Prometheus

1. Installer Prometheus (local)
 ```shell
  wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
  tar xzf prometheus-2.48.0.linux-amd64.tar.gz
  cd prometheus-2.48.0.linux-amd64
  ```
- Utiliser la configuration prometheus.yml, et alerts.yml en le mettant à la racine et pour lancer prometheus avec ./prometheus --config.file=prometheus.yml

2. Installer Alert Manager
  ```shell
  wget https://github.com/prometheus/alertmanager/releases/download/v0.27.0/alertmanager-0.27.0.linux-amd64.tar.gz
  tar -xvzf alertmanager-0.27.0.linux-amd64.tar.gz
  cd alertmanager-0.27.0.linux-amd64
  ```
- Utiliser la configuration alertmanager.yml en le mettant à la racine de l'alert manager et lancer avec ./alertmanager --config.file=alertmanager.yml

3. Lancer l'exporteur prometheus avec `python main.py` (rassurer votre d'être dans le repertoire `test_with_prometheus`)