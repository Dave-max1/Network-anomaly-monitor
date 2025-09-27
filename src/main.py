import time
import threading
import yaml
from scapy.all import sniff
from detector import FlowAggregator, Detector
from alerting import AlertManager
import logging

def load_config(path="../config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def capture_worker(iface, bpf, pkt_queue):
    # sniff et push les paquets dans la file (simple append)
    def handle(pkt):
        pkt_queue.append(pkt)
    sniff(iface=iface if iface else None, filter=bpf if bpf else None, prn=handle, store=False)

def window_loop(cfg, pkt_queue):
    agg = FlowAggregator()
    alert_mgr = AlertManager(cfg['alerts'])
    detector = Detector(cfg, alert_mgr)

    window = cfg['capture']['window_seconds']
    while True:
        t0 = time.time()
        # drain pkt_queue atomically (simple)
        pkts = []
        while pkt_queue:
            pkts.append(pkt_queue.pop(0))
        logging.info("Processing %d packets in window", len(pkts))
        agg.ingest_packets(pkts)
        summary = agg.summarize_and_reset()
        detector.analyze_window(summary)
        elapsed = time.time() - t0
        sleep_for = max(0, window - elapsed)
        time.sleep(sleep_for)

def setup_logging(cfg):
    logcfg = cfg.get('logging', {})
    level = getattr(logging, logcfg.get('level', 'INFO'))
    logfile = logcfg.get('logfile', None)
    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(level=level, handlers=handlers,
                        format="%(asctime)s %(levelname)s %(message)s")

def main():
    cfg = load_config()
    setup_logging(cfg)
    pkt_queue = []
    iface = cfg['capture'].get('iface', None)
    bpf = cfg['capture'].get('bpf', "")
    capture_thread = threading.Thread(target=capture_worker, args=(iface, bpf, pkt_queue), daemon=True)
    capture_thread.start()
    logging.info("Capture started on iface=%s bpf=%s", iface, bpf)
    try:
        window_loop(cfg, pkt_queue)
    except KeyboardInterrupt:
        logging.info("Stopping...")

if __name__ == "__main__":
    main()
