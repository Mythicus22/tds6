"""
eShopCo Latency Check API - Serverless endpoint for deployment latency monitoring.
POST /api/latency with {"regions": [...], "threshold_ms": 180}
"""
import json
import math
from http.server import BaseHTTPRequestHandler
from os.path import dirname, join

# Path to telemetry data (relative to project root)
TELEMETRY_PATH = join(dirname(dirname(__file__)), "q-vercel-latency.json")


def load_telemetry():
    """Load telemetry data from JSON file."""
    with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_region_metrics(records, threshold_ms):
    """Compute avg_latency, p95_latency, avg_uptime, and breaches per region."""
    if not records:
        return {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}

    latencies = [r["latency_ms"] for r in records]
    uptimes = [r["uptime_pct"] for r in records]

    avg_latency = sum(latencies) / len(latencies)
    avg_uptime = sum(uptimes) / len(uptimes)
    breaches = sum(1 for L in latencies if L > threshold_ms)

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)
    p95_idx = min(math.ceil(0.95 * n) - 1, n - 1) if n > 0 else 0
    p95_idx = max(0, p95_idx)
    p95_latency = sorted_latencies[p95_idx] if sorted_latencies else 0

    return {
        "avg_latency": round(avg_latency, 2),
        "p95_latency": round(p95_latency, 2),
        "avg_uptime": round(avg_uptime, 2),
        "breaches": breaches,
    }


def process_request(regions, threshold_ms):
    """Filter telemetry by regions and compute per-region metrics."""
    data = load_telemetry()
    result = {}

    for region in regions:
        region_records = [r for r in data if r["region"] == region]
        result[region] = compute_region_metrics(region_records, threshold_ms)

    return result


def cors_headers():
    """CORS headers for POST from any origin."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "86400",
    }


class handler(BaseHTTPRequestHandler):
    def _send_cors(self):
        for k, v in cors_headers().items():
            self.send_header(k, v)

    def _send_json(self, status, body):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self._send_cors()
        self.end_headers()
        self.wfile.write(json.dumps(body).encode("utf-8"))

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_POST(self):
        """Handle POST with regions and threshold_ms."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        regions = payload.get("regions", [])
        threshold_ms = payload.get("threshold_ms")

        if not isinstance(regions, list):
            self._send_json(400, {"error": "regions must be an array"})
            return
        if threshold_ms is None or not isinstance(threshold_ms, (int, float)):
            self._send_json(400, {"error": "threshold_ms is required and must be a number"})
            return

        try:
            result = process_request(regions, float(threshold_ms))
            self._send_json(200, result)
        except FileNotFoundError:
            self._send_json(500, {"error": "Telemetry data not found"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})
