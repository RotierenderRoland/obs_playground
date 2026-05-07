# Observability Playground

Dieses Repository ist ein kleiner Playground zum Demonstrieren von Metriken und Monitoring mit Prometheus und Grafana. Es startet eine instrumentierte Flask-App zusammen mit Prometheus, Grafana, Node Exporter und cAdvisor per Docker Compose.

Der Fokus liegt darauf, schnell nachvollziehbar zu zeigen:

- wie eine Anwendung eigene Metriken exportiert
- wie Prometheus Metriken scraped und Alert-Regeln auswertet
- wie Grafana eine Prometheus-Datenquelle und Dashboards automatisch bereitstellt
- wie System-, Container- und Applikationsmetriken zusammen betrachtet werden können

## Komponenten

| Komponente | Zweck | URL |
| --- | --- | --- |
| Flask-App | Demo-Service, der Jobs simuliert und OpenTelemetry-Metriken exportiert | http://localhost:8080 |
| App-Metriken | Prometheus-kompatibler Metrik-Endpunkt der App | http://localhost:9464/metrics |
| Prometheus | Scraping, Speicherung und Alert Rule Evaluation | http://localhost:9090 |
| Grafana | Visualisierung der Prometheus-Metriken | http://localhost:3000 |
| Node Exporter | Host/System-Metriken | http://localhost:9100 |
| cAdvisor | Container-Metriken | http://localhost:8081 |

Grafana wird mit `admin` / `admin` gestartet. Die Prometheus-Datenquelle und Dashboards werden über die Dateien in `grafana/provisioning` automatisch provisioniert.

## Voraussetzungen

- Docker
- Docker Compose
- `curl` für das optionale Skript `generate_metrics.sh`

## Start

```bash
docker compose up --build
```

Danach sind die Dienste über die oben genannten URLs erreichbar.

Zum Stoppen:

```bash
docker compose down
```

Wenn auch die gespeicherten Prometheus- und Grafana-Daten entfernt werden sollen:

```bash
docker compose down -v
```

## Demo-App

Die Flask-App stellt dynamische Job-Endpunkte bereit:

```text
GET /<customer>/<job_type>
```

Beispiel:

```bash
curl http://localhost:8080/siemens/backup
```

Ein Request simuliert einen Job, schläft zufällig zwischen 10 und 20 Sekunden und schreibt dabei Metriken mit den Labels `customer` und `job_type`.

Wichtige App-Metriken:

- `job_started_total`: Anzahl gestarteter Jobs
- `job_completed_total`: Anzahl abgeschlossener Jobs
- `job_duration_seconds`: Dauer der Jobs als Histogramm

Zusätzlich instrumentiert OpenTelemetry die Flask-App automatisch, sodass weitere HTTP-bezogene Metriken verfügbar sind.

## Metriken erzeugen

Das Skript `generate_metrics.sh` erzeugt Beispiel-Last für mehrere Kunden und Job-Typen:

```bash
./generate_metrics.sh
```

Anschließend können die Metriken in Prometheus oder Grafana ausgewertet werden.

Beispiel-Queries für Prometheus:

```promql
sum by (customer, job_type) (job_started_total)
```

```promql
sum by (customer, job_type) (job_completed_total)
```

```promql
histogram_quantile(
  0.95,
  sum by (le, customer, job_type) (rate(job_duration_seconds_bucket[5m]))
)
```

## Prometheus

Die Prometheus-Konfiguration liegt unter `prometheus/prometheus.yml`.

Aktuell werden diese Targets gescraped:

- `node-exporter:9100` für Host-Metriken
- `cadvisor:8081` für Container-Metriken
- `app:9464` für App-Metriken
- `localhost:9090` für Prometheus-eigene Metriken

Alert-Regeln liegen unter `prometheus/rules/`, zum Beispiel:

- hohe CPU-Last
- hohe Speicherauslastung
- hohe Festplattenauslastung
- ungewöhnliches Speicherwachstum

Hinweis: In `docker-compose.yml` ist Alertmanager aktuell auskommentiert. Die Prometheus-Konfiguration enthält bereits eine Alertmanager-Referenz auf `alertmanager:9093`; diese kann aktiviert werden, sobald der Alertmanager-Service und seine Konfiguration ergänzt werden.

## Grafana

Grafana wird automatisch mit Prometheus als Datenquelle gestartet:

- Datasource Provisioning: `grafana/provisioning/datasources/datasource.yml`
- Dashboard Provisioning: `grafana/provisioning/dashboards/dashboards.yml`
- Dashboard JSON: `grafana/dashboards/system-overview.json`

Nach dem Start unter http://localhost:3000 anmelden und das provisionierte Dashboard öffnen.

## Projektstruktur

```text
.
├── docker-compose.yml
├── Dockerfile
├── generate_metrics.sh
├── requirements.txt
├── src/
│   └── app.py
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
│       └── node_alerts.yml
└── grafana/
    ├── dashboards/
    │   └── system-overview.json
    └── provisioning/
        ├── dashboards/
        │   └── dashboards.yml
        └── datasources/
            └── datasource.yml
```

## Typischer Ablauf fuer eine Demo

1. Stack starten:

   ```bash
   docker compose up --build
   ```

2. Prometheus Targets pruefen:

   http://localhost:9090/targets

3. Beispiel-Last erzeugen:

   ```bash
   ./generate_metrics.sh
   ```

4. App-Metriken in Prometheus abfragen:

   ```promql
   sum by (customer, job_type) (job_completed_total)
   ```

5. Dashboard in Grafana ansehen:

   http://localhost:3000

## Ziel

Der Playground ist bewusst klein gehalten und eignet sich zum Erklaeren, Experimentieren und Erweitern von Observability-Grundlagen. Er kann als Ausgangspunkt dienen, um weitere Metriken, Dashboards, Alerts oder Alertmanager-Routen zu demonstrieren.
