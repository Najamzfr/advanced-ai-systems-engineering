# Week 7 observability starter

This local stack is for development and course testing. It includes separate
OpenTelemetry Collector, Grafana, Tempo, Prometheus and Loki services. Start it with:

```text
docker compose up -d
```

Open Grafana at `http://localhost:3000` and export OTLP/HTTP traces, metrics and logs to `http://localhost:4318`. Prometheus is available at `http://localhost:9090`, Tempo at `http://localhost:3200`, and Loki at `http://localhost:3100`.

The dashboard expects application metrics named `genai_request_duration_seconds`, `genai_requests_total`, `genai_errors_total`, `genai_cost_usd_total`, `genai_retries_total`, and `genai_tokens_total`. The learner must instrument the Week 4 agent and record the model, operation, run ID, token counts and price version as attributes. Use `failure-injection.json` for the required timeout-after-retrieval exercise and preserve the trace ID in the report. This stack is intended for development, demonstration and testing, not production deployment.
