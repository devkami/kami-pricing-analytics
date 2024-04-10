#!/bin/bash

# Function to try a request multiple times with an interval
# $1: Number of attempts
# $2: Interval between attempts (in seconds)
# ${@:3}: Arguments for curl
attempt_request() {
  local retries=$1
  local interval=$2
  local cmd=("curl" "-f" "-s" "${@:3}")
  
  for i in $(seq 1 $retries); do
    echo "Attempt $i of $retries for the request: ${cmd[*]}"
    if "${cmd[@]}" > /dev/null; then
      echo "Success on the request after $i attempts."
      return 0
    fi
    sleep $interval
  done
  echo "Failure after $retries attempts."
  return 1
}

# Check 1: GET /api/docs with 3 attempts and 1-second interval
if ! attempt_request 3 1 http://0.0.0.0:8001/api/docs; then
  exit 1
fi

# Check 2: POST /api/research (1st URL) with 3 attempts and 1-second interval
if ! attempt_request 3 1 -X 'POST' 'http://0.0.0.0:8001/api/research' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "product_url": "https://www.belezanaweb.com.br/amend-complete-repair-shampoo-250ml/ofertas-marketplace", "research_strategy": 0 }'; then
  exit 1
fi

# Check 3: POST /api/research (2nd URL) with 10 attempts and 3-second interval
if ! attempt_request 10 3 -X 'POST' 'http://0.0.0.0:8001/api/research' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{ "product_url": "https://www.amazon.com.br/dp/B07GYX8QRJ", "research_strategy": 0 }'; then
  exit 1
fi
