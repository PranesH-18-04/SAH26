"""
traffic_simulator.py
Generates synthetic unidirectional IP flow records (no real network capture needed).
Mimics: normal background traffic + injected attack patterns (port scan, DDoS burst).
"""

import random
import time
import csv
import os

ATTACK_TYPES = ["normal", "port_scan", "ddos_burst", "unusual_size"]

def generate_flow(attack_type="normal", src_id=None):
    """Create one synthetic flow record."""
    src_ip = src_id or f"192.168.1.{random.randint(2, 254)}"
    dst_ip = f"10.0.0.{random.randint(2, 254)}"

    if attack_type == "normal":
        return {
            "timestamp": time.time(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": random.choice([80, 443, 53, 22]),
            "packet_size": random.randint(64, 1500),
            "packets_per_sec": round(random.uniform(0.5, 5), 2),
            "protocol": random.choice(["TCP", "UDP"]),
            "label": "normal",
        }

    if attack_type == "port_scan":
        return {
            "timestamp": time.time(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": random.randint(1, 65535),   # scanning many ports
            "packet_size": random.randint(40, 60),
            "packets_per_sec": round(random.uniform(20, 60), 2),
            "protocol": "TCP",
            "label": "port_scan",
        }

    if attack_type == "ddos_burst":
        return {
            "timestamp": time.time(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": 80,
            "packet_size": random.randint(40, 100),
            "packets_per_sec": round(random.uniform(200, 800), 2),  # huge spike
            "protocol": "UDP",
            "label": "ddos_burst",
        }

    if attack_type == "unusual_size":
        return {
            "timestamp": time.time(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": random.choice([80, 443]),
            "packet_size": random.randint(5000, 9000),  # abnormally large
            "packets_per_sec": round(random.uniform(1, 10), 2),
            "protocol": "TCP",
            "label": "unusual_size",
        }


def generate_dataset(n_normal=500, n_attacks=100):
    """Build a mixed dataset of normal + attack flows."""
    rows = []
    for _ in range(n_normal):
        rows.append(generate_flow("normal"))
    for _ in range(n_attacks):
        attack = random.choice(ATTACK_TYPES[1:])
        rows.append(generate_flow(attack))
    random.shuffle(rows)
    return rows


def save_to_csv(rows, path="data/sample_traffic.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} flow records to {path}")


def replay_stream(rows, delay=0.1):
    """Yield flow records one at a time, simulating a live unidirectional feed."""
    for row in rows:
        yield row
        time.sleep(delay)


if __name__ == "__main__":
    dataset = generate_dataset()
    save_to_csv(dataset, path="../data/sample_traffic.csv")
