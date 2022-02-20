#!/usr/bin/env bash

# Entrypoint for the Dockerfile (Datagen sim)

set -e

DIR=$(dirname "$0")

$DIR/cli.py sim \
    --manager_host manager \
    --manager_port 6789
