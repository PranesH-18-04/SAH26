import React from "react";

export default function AlertTable({ alerts }) {
  if (alerts.length === 0) {
    return <p>No alerts yet. Click "Start Traffic Replay" above.</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr style={{ textAlign: "left", borderBottom: "2px solid #ccc" }}>
          <th>Source IP</th>
          <th>Dest IP</th>
          <th>Port</th>
          <th>Reason</th>
          <th>ML Score</th>
          <th>AI Summary</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((a, i) => (
          <tr key={i} style={{ borderBottom: "1px solid #eee" }}>
            <td>{a.src_ip}</td>
            <td>{a.dst_ip}</td>
            <td>{a.dst_port}</td>
            <td>{a.reason}</td>
            <td>{a.ml_score}</td>
            <td>{a.summary}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
