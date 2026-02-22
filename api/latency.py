"""
eShopCo Latency Check API - Serverless endpoint for deployment latency monitoring.
POST /api/latency with {"regions": [...], "threshold_ms": 180}
"""
import json
import math
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Path to telemetry data
TELEMETRY_PATH = Path(__file__).parent.parent / "q-vercel-latency.json"


class LatencyRequest(BaseModel):
    regions: list
    threshold_ms: float


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


@app.post("/")
async def latency_check(request: LatencyRequest):
    """Handle POST with regions and threshold_ms."""
    if not isinstance(request.regions, list):
        raise HTTPException(status_code=400, detail="regions must be an array")
    if request.threshold_ms is None:
        raise HTTPException(status_code=400, detail="threshold_ms is required and must be a number")

    try:
        result = process_request(request.regions, float(request.threshold_ms))
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Telemetry data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
