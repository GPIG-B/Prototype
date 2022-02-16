#!/usr/bin/env bash

# Entrypoint for the Dockerfile

set -e

DIR=$(dirname "$0")

$DIR/cli.py sim \
    --config $DIR/../configs/datagen.yaml &
$DIR/cli.py api \
    --host 0.0.0.0 \
    --port 8080 \
