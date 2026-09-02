"""
feature_extractor.py
Converts raw flow dicts into a numeric feature vector usable by the detector.
Kept simple on purpose for the selection-round demo.
"""

PROTOCOL_MAP = {"TCP": 0, "UDP": 1, "ICMP": 2}

def extract_features(flow: dict):
    """
    Turn one flow record into a flat list of numeric features:
    [packet_size, packets_per_sec, dst_port, protocol_encoded]
    """
    return [
        flow.get("packet_size", 0),
        flow.get("packets_per_sec", 0),
        flow.get("dst_port", 0),
        PROTOCOL_MAP.get(flow.get("protocol", "TCP"), 0),
    ]


def extract_batch(flows: list):
    """Extract features for a list of flows -> list of feature vectors."""
    return [extract_features(f) for f in flows]
