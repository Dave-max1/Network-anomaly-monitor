from collections import defaultdict, Counter
from scapy.layers.inet import IP, TCP, UDP
import numpy as np
from sklearn.cluster import DBSCAN
import logging
from datetime import datetime

class FlowAggregator:
    """
    Construit des métriques par IP source (et flow) pour chaque fenêtre.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.bytes_per_src = defaultdict(int)
        self.pkt_per_src = defaultdict(int)
        self.conn_count = defaultdict(int)     # tentative de connexion (SYN)
        self.dst_ports_per_src = defaultdict(set)
        self.first_seen = dict()

    def ingest_packets(self, pkts):
        for p in pkts:
            self.process_pkt(p)

    def process_pkt(self, p):
        if not p.haslayer(IP):
            return
        ip = p[IP]
        src = ip.src
        self.bytes_per_src[src] += len(p)
        self.pkt_per_src[src] += 1
        if src not in self.first_seen:
            self.first_seen[src] = datetime.utcnow()
        # ports
        if p.haslayer(TCP):
            tcp = p[TCP]
            self.dst_ports_per_src[src].add(tcp.dport)
            # Count SYN attempts as connection
            flags = tcp.flags
            if flags & 0x02:  # SYN
                self.conn_count[src] += 1
        elif p.haslayer(UDP):
            udp = p[UDP]
            self.dst_ports_per_src[src].add(udp.dport)

    def summarize_and_reset(self):
        summary = []
        for src in set(list(self.bytes_per_src.keys()) + list(self.pkt_per_src.keys())):
            summary.append({
                'src': src,
                'bytes': self.bytes_per_src.get(src, 0),
                'pkts': self.pkt_per_src.get(src, 0),
                'conns': self.conn_count.get(src, 0),
                'distinct_dst_ports': len(self.dst_ports_per_src.get(src, [])),
                'first_seen': self.first_seen.get(src)
            })
        self.reset()
        return summary

class Detector:
    def __init__(self, cfg, alert_mgr):
        self.cfg = cfg
        self.alert_mgr = alert_mgr
        self.th = cfg['thresholds']
        self.cluster_cfg = cfg.get('clustering', {})
        self.cluster_enabled = self.cluster_cfg.get('enabled', False)

    def analyze_window(self, summary_records):
        # Règles seuils simples
        for rec in summary_records:
            src = rec['src']
            if rec['bytes'] > self.th['bytes_per_ip_per_window']:
                msg = f"High data transfer: {src} sent {rec['bytes']} bytes in window"
                logging.warning(msg)
                self.alert_mgr.alert('high_transfer', rec, msg)
            if rec['conns'] > self.th['conn_count_per_ip_per_window']:
                msg = f"High connection rate: {src} made {rec['conns']} SYNs"
                logging.warning(msg)
                self.alert_mgr.alert('high_conn', rec, msg)
            if rec['distinct_dst_ports'] > self.th['distinct_dst_ports_per_ip']:
                msg = f"Port scan suspicious: {src} hit {rec['distinct_dst_ports']} distinct dst ports"
                logging.warning(msg)
                self.alert_mgr.alert('port_scan', rec, msg)

        # Clustering-based anomaly detection
        if self.cluster_enabled and summary_records:
            X = []
            ips = []
            for r in summary_records:
                ips.append(r['src'])
                # features (normalize/scaling simple)
                X.append([r['bytes'], r['pkts'], r['conns'], r['distinct_dst_ports']])
            X = np.array(X, dtype=float)
            # small feature scaling: log(1+x)
            X = np.log1p(X)
            model = DBSCAN(eps=self.cluster_cfg.get('eps',0.5),
                           min_samples=self.cluster_cfg.get('min_samples',3)).fit(X)
            labels = model.labels_
            for ip, lab, feat in zip(ips, labels, X):
                if lab == -1:
                    msg = f"Cluster anomaly detected for {ip} (features={np.expm1(feat).tolist()})"
                    logging.warning(msg)
                    self.alert_mgr.alert('cluster_outlier', {'src': ip}, msg)
