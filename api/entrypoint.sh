#!/usr/bin/env bash

# Entrypoint for the Dockerfile (API)

set -e

DIR=$(dirname "$0")

$DIR/cli.py \
    --host 0.0.0.0 \
    --port 8080 \
    --manager_host manager \
    --manager_port 6789 \
    deploy \
    --workers 2
