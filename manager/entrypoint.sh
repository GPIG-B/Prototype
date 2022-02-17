#!/usr/bin/env bash

# Entrypoint for the Dockerfile (Manager server)

set -e

DIR=$(dirname "$0")

$DIR/cli.py \
    --manager_host manager \
    --manager_port 6789
