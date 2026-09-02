"""
detector.py
Two-layer detection:
 1. Rule-based checks (fast, explainable, catches obvious cases)
 2. ML anomaly detection using Isolation Forest (catches subtler anomalies)
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from feature_extractor import extract_features, extract_batch

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "isolation_forest.pkl")


# ---------- Rule-based layer ----------

def rule_based_check(flow: dict):
    """Return (is_threat, reason) using simple human-written thresholds."""
    if flow.get("packets_per_sec", 0) > 100:
        return True, "High packet rate — possible DDoS burst"

    if flow.get("dst_port", 0) > 1024 and flow.get("packet_size", 0) < 60:
        return True, "Small packets to unusual port — possible port scan"

    if flow.get("packet_size", 0) > 4000:
        return True, "Abnormally large packet size"

    return False, None


# ---------- ML layer ----------

def train_model(flows, save_path=MODEL_PATH):
    """Train an Isolation Forest on (mostly normal) flow data and save it."""
    X = np.array(extract_batch(flows))
    model = IsolationForest(contamination=0.15, random_state=42)
    model.fit(X)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)
    print(f"Model trained and saved to {save_path}")
    return model


def load_model(path=MODEL_PATH):
    if os.path.exists(path):
        return joblib.load(path)
    return None


def ml_check(flow: dict, model):
    """Return (is_anomaly, score) using the trained Isolation Forest."""
    if model is None:
        return False, 0.0
    x = np.array([extract_features(flow)])
    prediction = model.predict(x)[0]      # -1 = anomaly, 1 = normal
    score = model.decision_function(x)[0]  # lower = more anomalous
    return prediction == -1, round(float(score), 4)


# ---------- Combined detector ----------

def detect(flow: dict, model=None):
    """
    Run both layers and produce a structured alert (or None if clean).
    """
    rule_flag, rule_reason = rule_based_check(flow)
    ml_flag, ml_score = ml_check(flow, model)

    if rule_flag or ml_flag:
        reason = rule_reason if rule_flag else f"ML anomaly detected (score={ml_score})"
        return {
            "src_ip": flow.get("src_ip"),
            "dst_ip": flow.get("dst_ip"),
            "dst_port": flow.get("dst_port"),
            "reason": reason,
            "rule_triggered": rule_flag,
            "ml_triggered": ml_flag,
            "ml_score": ml_score,
            "raw_label": flow.get("label", "unknown"),
        }
    return None


if __name__ == "__main__":
    # Quick manual test: train on simulated data, then run a few flows through it.
    from traffic_simulator import generate_dataset

    dataset = generate_dataset(n_normal=300, n_attacks=0)  # train mostly on normal
    train_model(dataset)

    model = load_model()
    test_flows = generate_dataset(n_normal=5, n_attacks=5)
    for f in test_flows:
        alert = detect(f, model)
        print(alert if alert else f"OK: {f['src_ip']} -> {f['dst_ip']}:{f['dst_port']}")
