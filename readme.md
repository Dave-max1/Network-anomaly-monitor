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

## Choix techniques

| Composant         | Choix technique                      | Justification                                                                 | Limites                                                                 |
|-------------------|--------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| Capture trafic    | Scapy                                | Simple, flexible, permet injecter ou analyser paquets IP/TCP/UDP             | Nécessite privilèges root / Npcap, performances limitées sur gros réseaux |
| Détection anomalies | Seuils + DBSCAN                     | Permet détecter facilement transferts massifs, SYN floods, scans de ports    | Détection basique, seuils statiques, peut générer faux positifs ou rater attaques subtiles |
| Export métriques  | `prometheus_client` (Gauge)          | Standard Prometheus, compatible avec alerting                                | Valeurs instantanées, pas de stockage historique interne                |
| Alerting          | SMTP (Gmail) + webhook               | Permet recevoir alertes par mail et intégrer à systèmes externes             | Dépend du SMTP, risque blocage par Gmail si mauvais mot de passe, limites de quotas |
| Simulation        | Scapy                                | Permet générer différents types d’attaques pour tests                        | À n’utiliser que sur réseau de test (loopback / lab)                   |
| Monitoring central| Prometheus + Alertmanager            | Standard industrie, intégration facile, visualisation via Grafana possible   | Nécessite configuration IP correcte si exporter sous WSL/Windows       |

---

## Cas couverts

- **Transferts massifs**  
  Détecte les IP émettant ou recevant plus de `X` octets par fenêtre configurable. Utile pour identifier exfiltration de données ou anomalies réseau.

- **Connexions inhabituelles / SYN flood**  
  Détecte les IP initiant plus de `Y` connexions TCP par fenêtre. Utile pour repérer scans de ports ou attaques DoS.

- **Scan de ports / activités suspectes**  
  Compte le nombre de ports distincts contactés par IP ; déclenche une alerte si le seuil est dépassé.

- **Alertes centralisées**  
  Envoi d’alertes par mail (Gmail) et webhook pour intégration SIEM / dashboard. Intégration avec Prometheus & Alertmanager pour visualisation et historique.

- **Tests et simulations**  
  Génération de trafic synthétique pour valider les règles et les alertes. Scénarios fournis : SYN flood, transfert massif, UDP/ICMP flood, scan de ports.

---

## Limites connues

- Performances limitées sur gros réseaux en raison de Scapy et Python (outil conçu pour petit bureau / lab).  
- Détection basée principalement sur **seuils statiques** → nécessite ajustement selon
