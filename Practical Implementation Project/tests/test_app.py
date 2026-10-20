"""
Unit and Integration Tests for DevOps Monitoring Platform
Phase 3: Practical Implementation Project
"""

import json
import os
import sys
import unittest

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from app import app


class TestDevOpsPracticalProject(unittest.TestCase):
    def setUp(self):
        """Configure test client."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        """Scenario 1: App responds on /health with healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("uptime", data)

    def test_prometheus_metrics_endpoint(self):
        """Scenario 2: Scrape endpoint /metrics exposes valid Prometheus text format."""
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("http_requests_total", content)
        self.assertIn("system_cpu_usage_percent", content)
        self.assertIn("system_memory_usage_percent", content)

    def test_invalid_input_handling(self):
        """Scenario 3: Invalid input to API returns 400 error without crashing."""
        # Non-JSON payload
        res1 = self.client.post("/api/data", data="invalid plain text")
        self.assertEqual(res1.status_code, 400)
        self.assertIn("error", json.loads(res1.data))

        # Missing required parameter
        res2 = self.client.post("/api/data", json={"wrong_field": "val"})
        self.assertEqual(res2.status_code, 400)
        self.assertIn("error", json.loads(res2.data))

    def test_valid_input_handling(self):
        """Scenario 4: Valid input to /api/data succeeds with 200."""
        res = self.client.post("/api/data", json={"name": "DevOps"})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")

    def test_index_dashboard(self):
        """Scenario 5: Root dashboard / renders properly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DevOps Monitoring Dashboard", response.data)


if __name__ == "__main__":
    unittest.main()
