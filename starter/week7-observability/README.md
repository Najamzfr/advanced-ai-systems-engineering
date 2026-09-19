# Week 7 observability starter

This local stack is for development and course testing. Start it with:

```text
docker compose up -d
```

Open Grafana at `http://localhost:3000` with the default local credentials shown by the image documentation. Export OTLP/HTTP traces and metrics to `http://localhost:4318`.

The dashboard expects application metrics named `genai_request_duration_seconds`, `genai_requests_total`, `genai_errors_total`, `genai_cost_usd_total`, `genai_retries_total`, and `genai_tokens_total`. The learner must instrument the Week 4 agent and record the model, operation, run ID, token counts and price version as attributes. This image is intended for development, demonstration and testing, not production deployment.
