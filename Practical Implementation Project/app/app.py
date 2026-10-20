"""
DevOps Automated Monitoring Platform
Phase 3: Practical Implementation Project
Author: DevOps Intern
Description: Python Flask microservice instrumented with Prometheus client metrics,
             system telemetry, and health check endpoints.
"""

from datetime import datetime
import os
import platform
import socket
import time
from flask import Flask, Response, jsonify, render_template, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
import psutil

app = Flask(__name__)
START_TIME = time.time()

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)

APP_UPTIME = Gauge(
    "app_uptime_seconds",
    "Application uptime in seconds",
)

SYSTEM_CPU_USAGE = Gauge(
    "system_cpu_usage_percent",
    "Host system CPU utilization percentage",
)

SYSTEM_MEMORY_USAGE = Gauge(
    "system_memory_usage_percent",
    "Host system memory utilization percentage",
)


@app.before_request
def before_request_hook():
    """Record request start time for latency tracking."""
    request._start_time = time.time()


@app.after_request
def after_request_hook(response):
    """Update Prometheus metrics after each HTTP request."""
    if hasattr(request, "_start_time"):
        latency = time.time() - request._start_time
        REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code,
    ).inc()
    return response


def get_uptime_string():
    """Calculate application uptime in a human-readable format."""
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@app.route("/")
def index():
    """Render the web monitoring dashboard."""
    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        os_name=f"{platform.system()} {platform.release()}",
        python_version=platform.python_version(),
    )


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint returning service status and uptime."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime": get_uptime_string(),
        }
    ), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus-formatted metrics for scraping."""
    # Update gauge metrics
    APP_UPTIME.set(time.time() - START_TIME)
    SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=None))
    SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().percent)

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    """Return JSON metrics for dashboard UI polling."""
    cpu_percent = psutil.cpu_percent(interval=None)
    virtual_mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return jsonify(
        {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count(logical=True),
            },
            "memory": {
                "total_mb": round(virtual_mem.total / (1024 * 1024), 2),
                "used_mb": round(virtual_mem.used / (1024 * 1024), 2),
                "free_mb": round(virtual_mem.available / (1024 * 1024), 2),
                "percent": virtual_mem.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent,
            },
            "process_count": len(psutil.pids()),
            "uptime": get_uptime_string(),
        }
    ), 200


@app.route("/api/system-info", methods=["GET"])
def system_info():
    """Return host metadata and runtime configuration."""
    return jsonify(
        {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "environment": os.getenv("APP_ENV", "production"),
        }
    ), 200


@app.route("/api/data", methods=["POST"])
def post_data():
    """Sample API endpoint accepting JSON data, validating inputs to test 400 errors."""
    if not request.is_json:
        return jsonify({"error": "Invalid request: body must be JSON"}), 400
    payload = request.get_json()
    if "name" not in payload:
        return jsonify({"error": "Missing required field 'name'"}), 400
    return jsonify({"message": f"Hello, {payload['name']}!", "status": "success"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("APP_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
