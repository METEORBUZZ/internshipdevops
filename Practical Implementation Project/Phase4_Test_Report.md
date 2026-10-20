# DEVOPS INTERNSHIP
## Test Report: Monitoring Dashboard & Pipeline
### Phase 4: Testing and Quality Assurance

| Intern | DevOps Intern |
| :--- | :--- |
| **Role** | DevOps Intern |
| **Company** | DevOps Training & Internship Program |
| **Mentor** | Assigned Mentor |
| **Date** | October 2026 |

---

### 1. Introduction
This report documents the testing and quality assurance work for the **Automated Monitoring Dashboard & DevOps Pipeline** built in Phase 3. The goal is to confirm that the application, the monitoring stack, and the CI/CD pipeline work correctly, handle errors gracefully, and are reliable enough for production use.

---

### 2. Scope and Test Environment

| Item | Details |
| :--- | :--- |
| **System under test** | Containerized web service, Prometheus, Grafana, and 4-Stage GitHub Actions pipeline |
| **Operating system** | macOS Sonoma / Sequoia (Apple Silicon ARM64) & Ubuntu 22.04 LTS (CI Runner) |
| **Container tools** | Docker Desktop 27.x & Docker Compose v2.x |
| **Test tools** | Python `unittest`, `pytest 8.1.1`, ApacheBench (`ab 2.3`), `curl`, GitHub Actions |
| **Repository** | [https://github.com/METEORBUZZ/internshipdevops](https://github.com/METEORBUZZ/internshipdevops) |
| **Monitored Endpoints** | `http://localhost:5050` (App), `:9090` (Prometheus), `:3000` (Grafana) |

---

### 3. Testing Approach

| Test type | Goal | How it was done |
| :--- | :--- | :--- |
| **Unit** | Check that each function works on its own | `pytest` and `unittest` test suite for endpoints and helper functions |
| **Integration** | Check that the services work together | Verify Prometheus scrapes `app:5000` and Grafana reads Prometheus datasource |
| **System** | Check the whole application end to end | Run full multi-container stack with `docker compose` and verify 4-stage pipeline |
| **Edge case** | Check behavior under unexpected input and failure | Send malformed JSON, stop container, evaluate automatic recovery |
| **Performance** | Check speed and resource use under load | 1,000 requests with concurrency 10 via ApacheBench while observing Grafana |
| **User acceptance** | Check the result is usable in practice | Verify live dashboard gauges, status badge, and clear metrics presentation |

---

### 4. Test Summary

| Measure | Result |
| :--- | :--- |
| **Total test cases** | **15** |
| **Passed** | **15** |
| **Failed** | **0** |
| **Not run** | **0** |
| **Known issues open** | **0 (All 3 architectural challenges resolved)** |
| **Test Execution Success Rate** | **100.0%** |

---

### 5. Test Cases and Results

| ID | Type | What was tested | Expected result | Actual result | Pass/Fail | Known issue |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **UT-01** | Unit | `/health` endpoint | Returns HTTP 200 and a healthy status | HTTP 200, status: healthy, uptime string returned | **Pass** | None |
| **UT-02** | Unit | Metrics endpoint | Returns metrics in Prometheus text format | Exposes valid Prometheus text format with counters and gauges | **Pass** | None |
| **UT-03** | Unit | Helper function with valid input | Returns the correct output | `get_uptime_string()` returns formatted `'0h Xm Ys'` | **Pass** | None |
| **IT-01** | Integration | Prometheus scraping the app | Target shows UP at `localhost:9090/targets` | Scrape target `app:5000` is UP with 0 scrape errors | **Pass** | None |
| **IT-02** | Integration | Grafana reading from Prometheus | Dashboard panels show live data | All 6 panels display real-time live telemetry | **Pass** | None |
| **ST-01** | System | `docker compose up` | App, Prometheus, and Grafana all start | All 3 containers initialized cleanly and stay healthy | **Pass** | None |
| **ST-02** | System | Push code end to end | Pipeline runs, image is deployed, dashboard stays live | 4-stage GitHub Actions pipeline finishes with green ticks | **Pass** | None |
| **EC-01** | Edge case | Empty input to the API | Clear error message, no crash | `POST /api/data` with empty body returns HTTP 400 error | **Pass** | None |
| **EC-02** | Edge case | Malformed input to the API | 4xx error, app keeps running | Missing `name` returns HTTP 400 without crashing service | **Pass** | None |
| **EC-03** | Edge case | Stop the app container | Dashboard shows the service as down | Prometheus marks target DOWN; Grafana status updates | **Pass** | None |
| **EC-04** | Edge case | Restart the whole stack | All services come back up | `docker compose restart` restores all services without state loss | **Pass** | None |
| **PF-01** | Performance | 1,000 requests, 10 at a time | No failed requests; response time & CPU in Grafana | 1,000 requests in 0.214s, 0 failed, 4,679 req/sec, avg 2.14ms | **Pass** | None |
| **CI-01** | Pipeline | Commit with a failing test | Build and push stages do not run | Stage 1 failure immediately aborts Stages 2, 3, and 4 | **Pass** | None |
| **CI-02** | Pipeline | Commit with passing tests | Image is built and pushed to the registry | All 4 stages run to completion (Test -> Build -> Push -> Deploy) | **Pass** | None |
| **UA-01** | User acceptance | A person opens the dashboard | Can tell whether app is up without help | Status badge 'API Healthy' and live gauges immediately clear | **Pass** | None |

---

### 6. Performance Test

A benchmark stress test was executed against the `/health` endpoint using ApacheBench (`ab`):
```bash
ab -n 1000 -c 10 http://localhost:5050/health
```

| Measure | Result |
| :--- | :--- |
| **Total requests** | **1,000 requests** |
| **Concurrent requests** | **10 concurrent connections** |
| **Failed requests** | **0 (100% success rate)** |
| **Average response time** | **2.14 ms (mean) / 0.21 ms across concurrency** |
| **Throughput (Req/Sec)** | **4,679.39 requests per second** |
| **Peak CPU & Memory (Grafana)** | **CPU: 4.8% peak / Memory: 28.5% stable** |

> *Figure 1: Load test result (ApacheBench & Grafana telemetry)*

---

### 7. Test Evidence

- **Unit Test Execution Results (`pytest`)**:
  `7 passed in 0.11s (100% pass rate covering UT-01, UT-02, UT-03, EC-01, EC-02)`
  > *Figure 2: Unit tests passing*

- **GitHub Actions 4-Stage Pipeline Execution**:
  `Stage 1 (Test & Lint) -> Stage 2 (Build) -> Stage 3 (Push) -> Stage 4 (Deploy & Health Check)`
  > *Figure 3: Pipeline passing with 4-stage green ticks*

---

### 8. Known Issues & Resolved Challenges

| ID | Issue Description | Severity | Status |
| :--- | :--- | :---: | :---: |
| **ISSUE-01** | macOS ControlCenter (AirPlay) Port 5000 collision causing blank page | High | **Fixed** (Remapped to 5050) |
| **ISSUE-02** | `psutil` compilation failure on Apple Silicon ARM64 Linux container | High | **Fixed** (Added `gcc` & `python3-dev`) |
| **ISSUE-03** | GitHub remote commit drift causing git push rejection | Medium | **Fixed** (Rebased cleanly on `main`) |

---

### 9. Code Review
- **Modularity**: Clean separation of application code, Prometheus scrape configuration, and Grafana provisioning.
- **Security**: Verified Dockerfile runs with unprivileged `appuser` UID, mitigating container escape vectors.
- **Pipeline Design**: Commended 4-stage sequential architecture with conditional execution safeguards preventing pipeline failures when secrets are absent.

---

### 10. User Acceptance Feedback
- A non-technical evaluator was asked to view the monitoring interface at `http://localhost:5050` and Grafana at `http://localhost:3000`.
- The evaluator immediately confirmed system status as "Healthy" via the status badge and intuitive progress gauges.
- **Usability score**: 10/10 for clarity and self-explanatory metrics presentation.

---

### 11. Conclusion and Recommendations
**Conclusion**:
The Phase 4 Quality Assurance testing confirms that the DevOps Monitoring Platform is robust, resilient, and production-ready. All 15 unit, integration, system, edge-case, and performance scenarios passed with a 100% success rate.

**Recommendations for Future Iterations**:
1. **Automated Alert Rules**: Configure Prometheus Alertmanager to fire webhook notifications to Slack/Discord when error rates exceed 1%.
2. **Automated Load Testing in CI**: Integrate ApacheBench into Stage 4 of the GitHub Actions workflow as an automated regression gate.
3. **Distributed Tracing**: Expand the telemetry stack with OpenTelemetry and Jaeger for microservice tracing.
