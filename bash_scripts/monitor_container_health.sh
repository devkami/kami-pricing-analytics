#!/bin/bash

SERVICE_NAME="pricing-analytics"
DB_SERVICE_NAME="postgres"
START_PERIOD=120
CHECK_INTERVAL=10

start_containers() {
    echo "Starting and rebuilding containers..."
    docker compose up -d --build $SERVICE_NAME $DB_SERVICE_NAME
    echo "Containers are starting, waiting for $START_PERIOD seconds before checking health..."
    sleep $START_PERIOD
}

check_health() {
    local service=$1
    start=$(date +%s)

    while true; do
        container_id=$(docker compose ps -q $service)
        health_status=$(docker inspect --format='{{.State.Health.Status}}' $container_id)
        echo "Checking health of $service: $health_status"
        if [ "$health_status" == "healthy" ]; then
            break
        fi
        sleep $CHECK_INTERVAL
    done

    end=$(date +%s)
    elapsed=$((end - start))    
    total_elapsed=$((START_PERIOD + elapsed))
    formated_total_elapsed=$(date -d@$total_elapsed -u +%H:%M:%S)
    echo "Time until $service is healthy: $total_elapsed seconds"
    echo "Total time until $service is healthy: $formated_total_elapsed"
}

main() {
    start_containers
    check_health $SERVICE_NAME
}

main
