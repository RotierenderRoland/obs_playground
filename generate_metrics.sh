#!/usr/bin/env bash

APP_URL="http://localhost:8080"

customers=(siemens bosch miele bauknecht)
jobs=(backup reindex restart data_export)

RUNS_PER_COMBINATION=3

for ((i=1; i<=RUNS_PER_COMBINATION; i++)); do
  for customer in "${customers[@]}"; do
    for job in "${jobs[@]}"; do
      echo "Trigger job: customer=${customer}, job_type=${job}"
      curl -s "${APP_URL}/${customer}/${job}" >/dev/null &
    done
  done
done

wait

echo "Alle Jobs abgeschlossen."
