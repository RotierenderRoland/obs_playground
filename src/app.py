import os
import random
import time
from flask import Flask, jsonify

from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from prometheus_client import start_http_server
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider

from opentelemetry.instrumentation.flask import FlaskInstrumentor


def setup_metrics() -> None:
    resource = Resource.create(
        {SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "job-sleeper-flask")}
    )

    metrics_host = os.getenv("METRICS_HOST", "0.0.0.0")
    metrics_port = int(os.getenv("METRICS_PORT", "9464"))

    start_http_server(port=metrics_port, addr=metrics_host)

    reader = PrometheusMetricReader()
    metrics.set_meter_provider(MeterProvider(
        resource=resource, metric_readers=[reader]))


app = Flask(__name__)
setup_metrics()
FlaskInstrumentor().instrument_app(app)

meter = metrics.get_meter("job-sleeper-meter")

job_started = meter.create_counter(
    name="job_started_total",
    description="Number of jobs started",
    unit="1",
)

job_completed = meter.create_counter(
    name="job_completed_total",
    description="Number of jobs completed",
    unit="1",
)

job_duration = meter.create_histogram(
    name="job_duration_seconds",
    description="Job processing duration in seconds",
    unit="s",
)


@app.route("/<string:customer>/<string:job_type>", methods=["GET"])
def run_job(customer: str, job_type: str):
    duration = random.uniform(10.0, 20.0)

    attrs = {
        "customer": customer,
        "job_type": job_type,
    }

    job_started.add(1, attributes=attrs)

    start = time.perf_counter()
    time.sleep(duration)
    elapsed = time.perf_counter() - start

    job_duration.record(elapsed, attributes=attrs)
    job_completed.add(1, attributes=attrs)

    return jsonify(
        {
            "customer": customer,
            "job_type": job_type,
            "slept_seconds": round(duration, 3),
            "measured_seconds": round(elapsed, 3),
        }
    )


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    app.run(host=host, port=port)
