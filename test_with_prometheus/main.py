from prometheus_client import start_http_server, Gauge
import psutil
import time
import random

# ==============================
# Définition des métriques
# ==============================
bytes_sent = Gauge("network_bytes_sent", "Total bytes sent")
bytes_recv = Gauge("network_bytes_recv", "Total bytes received")
connections = Gauge("network_active_connections", "Active TCP connections")
errors_in = Gauge("network_errors_in", "Incoming packet errors")
errors_out = Gauge("network_errors_out", "Outgoing packet errors")
dropped_in = Gauge("network_dropped_in", "Incoming dropped packets")
dropped_out = Gauge("network_dropped_out", "Outgoing dropped packets")

# ==============================
# Collecte réelle
# ==============================
def collect_real_metrics():
    net_io = psutil.net_io_counters()
    bytes_sent.set(net_io.bytes_sent)
    bytes_recv.set(net_io.bytes_recv)
    errors_in.set(net_io.errin)
    errors_out.set(net_io.errout)
    dropped_in.set(net_io.dropin)
    dropped_out.set(net_io.dropout)

    conns = psutil.net_connections(kind="tcp")
    connections.set(len([c for c in conns if c.status == "ESTABLISHED"]))

    # debug console
    print(f"[REAL] sent={net_io.bytes_sent} recv={net_io.bytes_recv} conns={connections._value.get()}")

# ==============================
# Simulation pour tests
# ==============================
def simulate_high_traffic():
    bytes_sent.set(random.randint(5_000_000, 50_000_000))
    bytes_recv.set(random.randint(5_000_000, 50_000_000))

def simulate_many_connections():
    connections.set(random.randint(200, 1000))

def simulate_errors():
    errors_in.set(random.randint(100, 500))
    errors_out.set(random.randint(50, 300))

def simulate_drops():
    dropped_in.set(random.randint(50, 200))
    dropped_out.set(random.randint(50, 200))

def collect_simulated_metrics():
    simulate_high_traffic()
    simulate_many_connections()
    simulate_errors()
    simulate_drops()
    print(f"[SIMU] sent={bytes_sent._value.get()} recv={bytes_recv._value.get()} conns={connections._value.get()}")

# ==============================
# Mode principal
# ==============================
if __name__ == "__main__":
    start_http_server(8000, addr="0.0.0.0")
    print("Exporter réseau démarré sur : http://localhost:8000/metrics")

    MODE = "simulate"  # "real" ou "simulate"

    while True:
        if MODE == "real":
            collect_real_metrics()
        else:
            collect_simulated_metrics()

        time.sleep(5)
