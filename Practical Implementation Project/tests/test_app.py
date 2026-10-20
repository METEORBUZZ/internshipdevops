"""
Unit and Integration Tests for DevOps Monitoring Platform
Phase 4: Testing and Quality Assurance
Test Suite covering UT-01, UT-02, UT-03, EC-01, EC-02
"""

import json
import os
import sys
import unittest

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from app import app, get_uptime_string


class TestDevOpsPracticalProject(unittest.TestCase):
    def setUp(self):
        """Configure test client."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_ut01_health_endpoint(self):
        """UT-01: /health endpoint returns HTTP 200 and healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("uptime", data)

    def test_ut02_prometheus_metrics_endpoint(self):
        """UT-02: /metrics endpoint returns metrics in Prometheus text format."""
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("http_requests_total", content)
        self.assertIn("system_cpu_usage_percent", content)
        self.assertIn("system_memory_usage_percent", content)

    def test_ut03_helper_uptime_string(self):
        """UT-03: Helper function get_uptime_string() returns correct format."""
        uptime = get_uptime_string()
        self.assertIsInstance(uptime, str)
        self.assertIn("h", uptime)
        self.assertIn("m", uptime)
        self.assertIn("s", uptime)

    def test_ec01_empty_input_to_api(self):
        """EC-01: Empty/non-JSON input to API returns clear 400 error without crashing."""
        response = self.client.post("/api/data", data="")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_ec02_malformed_input_to_api(self):
        """EC-02: Malformed input (missing required field) returns 400, app continues."""
        response = self.client.post("/api/data", json={"invalid_field": "123"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_valid_input_handling(self):
        """Verify valid payload succeeds."""
        response = self.client.post("/api/data", json={"name": "DevOps Engineer"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

    def test_index_dashboard(self):
        """Verify root UI renders successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DevOps Monitoring Dashboard", response.data)


if __name__ == "__main__":
    unittest.main()
